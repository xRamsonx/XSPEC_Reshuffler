#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 11:51:56 2023

@author: kai
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 21:07:45 2023

@author: kai
"""
import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication

from xspec_reshuffler import GenerateXASWindow

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def run():
    myappid = "bh_gui"  # arbitrary string
    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
    #set fontsize:
    # Get the default font
    # defaultFont = QtWidgets.QApplication.font()
    
    # # Define a scaling factor for the font size (adjust as needed)
    # scalingFactor = 1.2
    
    # # Calculate the scaled font size
    # scaledFontSize = defaultFont.pointSizeF() * scalingFactor
    
    # # Create a font with the scaled font size
    # scaledFont = defaultFont
    # scaledFont.setPointSizeF(scaledFontSize)
    
    # # Set the scaled font as the application font
    # QtWidgets.QApplication.setFont(scaledFont)

    app = QApplication(sys.argv)
    app_icon = QIcon()
    app_icon.addFile(resource_path("Icon/48.png"), QSize(48, 48))
    app_icon.addFile(resource_path("Icon/256.png"), QSize(256, 256))
    window = GenerateXASWindow(app_icon)
    window.show()
    app.exec_()