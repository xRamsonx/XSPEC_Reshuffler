#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:23:57 2023

@author: kai
"""
from setuptools import setup

setup(
    name='xspec_reshuffler',
    version='0.1.0',    
    description='A example Python package',
    url='https://github.com/xRamsonx/XSPEC_Reshuffler',
    author='Kai Arnold',
    author_email='kai.arnold@design4webs.de',
    license='MIT License',
    packages=['xspec_reshuffler'],
    install_requires=['matplotlib',
                      'numpy',
                      'python-dateutil',
                      'pandas',
                      'PyQt5'
                      ],
    entry_points={
       'console_scripts': [
            'XSPEC_Reshuffler = xspec_reshuffler.main:run',
            'XSPEC_Reshuffler_shortcut = xspec_reshuffler.create:shortcut',
            
        ],
    },

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: MIT License',  
        'Operating System :: POSIX :: Linux/Windows',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
