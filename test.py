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

general.replace_kernel(PRIV_RESOURCE, WORK)
