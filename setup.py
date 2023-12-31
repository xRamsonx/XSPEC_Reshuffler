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
    include_package_data=True,
    package_data={'':['icons/*']},
    install_requires=['matplotlib', 'numpy', 'python-dateutil', 'pandas', 'PyQt5','pyshortcuts'],
    entry_points={
        'gui_scripts': [
            'XSPEC_Reshuffler = xspec_reshuffler.main:run',
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