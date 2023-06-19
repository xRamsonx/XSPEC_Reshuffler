#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 21:07:45 2023

@author: kai
"""
import os
import sys
import argparse

from pyshortcuts import make_shortcut
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

def init_app():
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
    
def generate_shortcut():
    import xspec_reshuffler
    package_dir = os.path.abspath(os.path.join(os.path.dirname(xspec_reshuffler.__file__), '..'))
    # if sys.platform == 'win32':  # For Windows
    #     package_dir = os.path.join(sys.prefix, 'Lib', 'site-packages')
    # else:  # For Linux
    #     package_dir = os.path.join(sys.prefix, 'lib', 'python{}'.format(sys.version_info[0]), 'site-packages')
    main_script_path = os.path.join(package_dir, 'xspec_reshuffler', 'main.py')
    icon_path = os.path.join(
        package_dir,
        'Icon',  # Package name/folder
        '512.ico'
    )

    # Create a desktop shortcut
    make_shortcut(
        main_script_path,  # Path to your main script
        name='XSPEC Reshuffler',  # Shortcut name
        description='A description of your application',
        icon=icon_path,  # Path to your application icon
        terminal=False,  # Set this to True if your application needs a terminal
    )
    
def run():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('-s','--shortcut', action='store_true',
                    help='creates a shortcut on your desktop')
    args = parser.parse_args()
    if args.shortcut:
        generate_shortcut()
    else:
        init_app()
        