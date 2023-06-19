#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 22:14:28 2023

@author: kai
"""
from numpy import (
    loadtxt,
    array,
    flip,
    linspace
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QFrame,
    QVBoxLayout
)
from h5py import File as open_h5py

from xspec_reshuffler.widgets import DragAndDropLabelwithButton


def cubic(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

class XAS:
    def __init__(
        self, xas_path, emission_factors=[0, 0, 1, 0], excitation_factors=[1, 0]
    ):
        self.xas = self.readXAS(xas_path)
        x = linspace(0,len(self.xas[0])-1,len(self.xas[0]))
        self.emission = self.indexToEmission(x, emission_factors)
        print(emission_factors)
        y = flip(linspace(0,len(self.xas)-1,len(self.xas)))
        self.excitation = self.indexToExcitation(y,excitation_factors)
        
    def indexToExcitation(self, x, factors):
        y = factors[0] * x + factors[1]
        return y

    def indexToEmission(self, x, factors):
        #print(self.emission_factors)
        y = cubic(x,*factors)
        return y

    def readXAS(self, filename):
        if ".h5" in filename:
            with open_h5py(filename, "r") as f:
                XAS = array(f["data"]["processed"]["sensor1d"]["XES"][0])
        else:
            XAS = loadtxt(filename,skiprows=1)[:,1:]
        print(XAS.shape)
        return XAS

    def rotateXAS(self):
        out = []
        for i in range(0, len(self.xas)):
            for j in range(0, len(self.xas[0])):
                out.append(
                    [self.emission[j], self.excitation[i], self.xas[i, j]]
                )
        out=array(out)
        return out

class DragXASMeasurement(QFrame):
    updated = pyqtSignal()
    def __init__(self):
        super(DragXASMeasurement, self).__init__()
        self.dragAndDrop = DragAndDropLabelwithButton("measurement file (.h5)")
        self.dragAndDrop.fileDropped.connect(self.update_path)

        self.path = None
        title = QLabel("XSpec Measurement")

        layout = QVBoxLayout()
        layout.addWidget(title, 10)
        layout.addWidget(self.dragAndDrop, 100)
        self.setLayout(layout)
        self.setFrameShape(QFrame.Box)

    def update_path(self, filepath):
        self.path = filepath
        self.updated.emit()
        