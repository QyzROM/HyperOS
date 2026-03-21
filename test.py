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

MyImage("super").unpack()

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

# split mi_ext and move stuff to corresponding partition
ModuleDealer("MiExt").perform_task()

# add binary to system
ModuleDealer("Binary").perform_task()

# preload apks
ModuleDealer("Preload").perform_task()

# add general components
# ModuleDealer("GeneralComponents").perform_task()

ModuleDealer("DeBloat").perform_task()

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
