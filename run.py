#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 23:41:23 2023

@author: kai
"""
import sys
import os
#from ctypes import windll
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QApplication
)
from xspec_reshuffler import GenerateXASWindow

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    myappid = "XSPEC_Reshuffler"  # arbitrary string
    # if sys.platform == "win32":

    #windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    app_icon = QIcon()
    app_icon.addFile(resource_path("Icon/16.png"), QSize(16, 16))
    app_icon.addFile(resource_path("Icon/24.png"), QSize(24, 24))
    app_icon.addFile(resource_path("Icon/32.png"), QSize(32, 32))
    app_icon.addFile(resource_path("Icon/48.png"), QSize(48, 48))
    app_icon.addFile(resource_path("Icon/256.png"), QSize(256, 256))
    w = GenerateXASWindow(app_icon)
    app.exec_()