"""
Xiaomi 17 Pro Max 一键生成 QyzROM
国行
"""

import os
import shutil
import pathlib
import json

RUN_EXTRA_STEPS = os.getenv("RUN_EXTRA_STEPS") == "1"

from src.custom.ModuleDealer import ModuleDealer
from src.custom.VendorDealer import VendorDealer
from src.custom.ProductDealer import ProductDealer
from src.device import general
from src.image.Image import MyImage
from src.image.ImageConverter import ImageConverter
from tikpath import TikPath
from src.custom import prepare, lp, Payload
from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("TEST")

myprinter = MyPrinter()

# VAB
DEVICE = "popsicle"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

general.clean()

# 1. 提取需要的文件
zip_file_path = prepare.unarchive_ota()

# extract ver
ver = prepare.extract_ver_of_ota(f"{WORK}/extracted/care_map.pb")
myprinter.print_green(f"Extracted version: {ver}")

# extract imgs from payload.bin
Payload.Payload(f"{WORK}/extracted/payload.bin").extract(f"{WORK}/images")

if RUN_EXTRA_STEPS:
    os.remove(zip_file_path)
    shutil.rmtree(f"{WORK}/extracted")
    # save version info
    with open(
        os.path.join(tikpath.project_path, "version_info.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(ver)

# 2. 分门别类处理镜像
# 2.1 avb去除
general.deal_with_avb()

# 2.2 内核替换
# now it's 6.12.23 lkm
general.replace_kernel(PRIV_RESOURCE, WORK)
# 补充 进行ksu-lkm修补
general.patch_lkm("android16-6.12")

# 2.3 替换twrp
# general.replace_rec(PRIV_RESOURCE)

# 2.4 处理vendor_boot
general.deal_with_vboot(False)

# 2.5 处理optics
pass

# 处理super
json_path = os.path.join(PRIV_RESOURCE, "super.json")
if os.path.exists(json_path):
    with open(json_path, "r") as f:
        super_info = json.load(f)
        qti_size = super_info.get("group_size", 0)
        device_size = super_info.get("device_size", 0)
    myprinter.print_green(
        f"Extracted super info from JSON: qti_size={qti_size}, device_size={device_size}"
    )
else:
    myprinter.print_yellow("super.json not found, using default 0")

# move
targets = [
    "vendor",
    "system",
    "mi_ext",
    "product",
    "system_ext",
    "odm",
    "system_dlkm",
    "vendor_dlkm",
]

# move images to project_path
for target in targets:
    img_path = os.path.join(WORK, "images", f"{target}.img")
    if os.path.exists(img_path):
        shutil.move(img_path, f"{tikpath.project_path}/{target}_a.img")
        myprinter.print_green(f"Moved {target} to project path")
    else:
        myprinter.print_yellow(f"{target} not found in images")

# unpack
img_vendor = MyImage("vendor_a")
img_vendor.unpack()

img_system = MyImage("system_a")
img_system.unpack()

img_mi_ext = MyImage("mi_ext_a")
img_mi_ext.unpack()

img_product = MyImage("product_a")
img_product.unpack()

img_system_ext = MyImage("system_ext_a")
img_system_ext.unpack()

# remove gms restrictions
ProductDealer(is_aonly=False).unlock_gms()
VendorDealer(is_aonly=False).remove_avb()

# add general components
ModuleDealer("GeneralComponents").perform_task()

# split mi_ext and move stuff to corresponding partition
ModuleDealer("MiExt").perform_task()

ModuleDealer("FixNfc").perform_task()

ModuleDealer("FixRecorder").perform_task()

# add binary to system
ModuleDealer("Binary").perform_task()

# preload apks
ModuleDealer("Preload").perform_task()

ModuleDealer("DeBloat").perform_task()

ModuleDealer("ChargeProp").perform_task()

ModuleDealer("UiProp").perform_task()

# fast enter game
ModuleDealer("GameProp").perform_task()

# fast dexoat
ModuleDealer("DexoatProp").perform_task()

ModuleDealer("BLFake").perform_task()

# misc
ModuleDealer("PropMod").perform_task()

# repack and move to super
img_vendor.pack_erofs().out2super()
img_vendor.unlink().rm_content()

img_mi_ext.pack_erofs().out2super()
img_product.pack_ext().out2super()
img_system.pack_ext().out2super()
img_system_ext.pack_ext().out2super()

if RUN_EXTRA_STEPS:
    img_system.unlink().rm_content()
    img_product.unlink().rm_content()
    img_mi_ext.unlink().rm_content()
    img_system_ext.unlink().rm_content()

# untouched partitions
MyImage("odm_a").move2super()
MyImage("system_dlkm_a").move2super()
MyImage("vendor_dlkm_a").move2super()

sh = lp.make_sh(
    tikpath.super,
    device_size,
    qti_size,
    super_type=lp.SuperType.VAB,
    targets=list(lp.get_targets()),
)
lp.cook(sh, tikpath.super)

# 清理super目录 只保留super.img
if RUN_EXTRA_STEPS:
    for item in pathlib.Path(tikpath.super).iterdir():
        if not item.name.startswith("super"):
            if not item.is_dir():
                item.unlink()
                myprinter.print_cyan(f"{item.name} removed from super directory")
ImageConverter(f"{tikpath.super}/super.img").zstd_compress(need_remove_old=True)

# 3. 打包
prepare.archive_ota(__name__)
