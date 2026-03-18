"""
Xiaomi 17 Pro Max 一键生成 QyzROM
国行
"""

import os
import pathlib
import shutil

RUN_EXTRA_STEPS = os.getenv("RUN_EXTRA_STEPS") == "1"

from src.custom.ModuleDealer import ModuleDealer
from src.custom.VendorDealer import VendorDealer
from src.device import general
from src.image.Image import MyImage
from src.image.ImageConverter import ImageConverter
from tikpath import TikPath
from src.custom import prepare, lp
from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("TEST")

myprinter = MyPrinter()

DEVICE = "popsicle"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

general.clean()

# 1. 提取需要的文件
tgz_file_path = prepare.unarchive()
if RUN_EXTRA_STEPS:
    os.remove(tgz_file_path)
    # save version info
    with open(
        os.path.join(tikpath.project_path, "version_info.txt"), "w", encoding="utf-8"
    ) as f:
        ver = os.path.basename(tgz_file_path).split("_")[2]
        f.write(ver)

# 处理super
general.moveimg2project("super")
MyImage("super").unpack()
qti_size = lp.get_qti_dynamic_partitions_size()
device_size = lp.get_device_size()
MyImage("super").unlink()

# unpack


img_product = MyImage("product_a")
img_product.unpack()
