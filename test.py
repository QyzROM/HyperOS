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
tikpath.set_project("Mi")

myprinter = MyPrinter()

# VAB
DEVICE = "popsicle"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

# general.clean()


img_system = MyImage("system_a")
img_system.unpack()

ModuleDealer("Fonts_Mi").perform_task()

img_system.pack_ext()