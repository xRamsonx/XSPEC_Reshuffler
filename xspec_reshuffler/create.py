#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 20:12:58 2023

@author: kai
"""
from pyshortcuts import make_shortcut
# Create a desktop shortcut using pyshortcuts
def shortcut():
        make_shortcut(
            'xspec_reshuffler/main.py',  # Path to your main script
            name='XSPEC Reshuffler',  # Shortcut name
            description='A description of your application',
            icon='Icon/512.ico',  # Path to your application icon
            terminal=False,  # Set this to True if your application needs a terminal
        )