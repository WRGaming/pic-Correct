import os
import sys
from enum import Enum


class Language(Enum):
    Chi = 0
    Eng = 1
    Fra = 2
    Ger = 3
    Jan = 4
    Alo = 5
    Lad = 6
    Hib = 7


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 判断sys中是否存在frozen变量,即是否是打包程序
        base_path = sys._MEIPASS  # sys._MEIPASS在一些编辑器中会报错，不用理会
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


now_Lan = Language.Eng
