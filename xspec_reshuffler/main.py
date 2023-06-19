#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 10:30:26 2023

@author: kai.arnold@design4webs.de
"""

import sys
import os

from numpy import array

#from ctypes import windll

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QApplication,
    QPushButton,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from xspec_reshuffler.emission_calibration import EmissionCalibration, CanvasRef, Ref
from xspec_reshuffler.excitation_calibration import ExcitationCalibration, LinearCallibration
from xspec_reshuffler.xas import DragXASMeasurement, XAS
from xspec_reshuffler.plot import DataPlot
from xspec_reshuffler.background_remover import BackgroundRemover

class GenerateXASWindow(QMainWindow):
    def __init__(self, app_icon):
        super(GenerateXASWindow, self).__init__()
        self.app_icon = app_icon
        
        self.setAcceptDrops(True)
        self.setWindowTitle("XAS data reshuffler")
        self.setGeometry(100, 100, 800, 1200)
        self.setWindowIcon(app_icon)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #B0B0B0;')
        
        self.emissionCalibration = EmissionCalibration()
        self.emissionCalibration.openRefCanvas.connect(self.openRefCanvas)
        self.emissionCalibration.updated.connect(self.loaded)
        self.emissionCalibration.setAttribute(Qt.WA_StyledBackground, True)
        self.emissionCalibration.setStyleSheet('background-color: #606060;')
        
        #00876C
        self.excitationCalibration = ExcitationCalibration()
        self.excitationCalibration.openLinearCanvas.connect(self.openLinearCanvas)
        self.excitationCalibration.updated.connect(self.loaded)
        self.excitationCalibration.setAttribute(Qt.WA_StyledBackground, True)
        self.excitationCalibration.setStyleSheet('background-color: #606060;')
        calib_layout = QVBoxLayout()
        calib_layout.addWidget(self.emissionCalibration, 100)
        calib_layout.addWidget(self.excitationCalibration, 100)

        
        self.saveParams=  QPushButton("Save Params")
        self.saveParams.clicked.connect(self.save_params)
        self.loadParams=  QPushButton("Load Params")
        self.loadParams.clicked.connect(self.load_params)
        self.plot_XAS = QPushButton("Plot XAS")
        self.plot_XAS.clicked.connect(self.plotXAS)
        self.plot_XAS.setAttribute(Qt.WA_StyledBackground, True)
        self.plot_XAS.setStyleSheet('background-color: #606060;')
        self.save_XAS = QPushButton("Set Background and save XSPEC file")
        self.save_XAS.clicked.connect(self.saveXAS)
        self.save_XAS.setAttribute(Qt.WA_StyledBackground, True)
        self.save_XAS.setStyleSheet('background-color: #606060;')
        
        parameter_layout = QHBoxLayout()
        parameter_layout.addWidget(self.loadParams, 100)
        parameter_layout.addWidget(self.saveParams, 100)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.plot_XAS, 100)
        button_layout.addWidget(self.save_XAS, 100)
        
        self.xas_measurement = DragXASMeasurement()
        self.xas_measurement.setAttribute(Qt.WA_StyledBackground, True)
        self.xas_measurement.setStyleSheet('background-color: #4664AA;')
        self.xas_measurement.updated.connect(self.loaded)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.xas_measurement, 100)
        main_layout.addLayout(calib_layout, 100)
        main_layout.addLayout(parameter_layout,10)
        main_layout.addLayout(button_layout, 10)

        widget = QWidget()
        widget.setStyleSheet(" font-size: 12pt; ")
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.show()
    
    def loaded(self):
        if self.xas_measurement.path:
            self.xas_measurement.setStyleSheet('background-color: #00876C;')
            if self.emissionCalibration.params:
                self.emissionCalibration.setStyleSheet('background-color: #00876C;')
                if self.excitationCalibration.params[1] > 0:
                    self.excitationCalibration.setStyleSheet('background-color: #00876C;')
                    self.save_XAS.setStyleSheet('background-color: #00876C;')
                    self.plot_XAS.setStyleSheet('background-color: #00876C;')
                else:
                    self.excitationCalibration.setStyleSheet('background-color: #4664AA;')  
                    self.save_XAS.setStyleSheet('background-color: #4664AA;')
                    self.plot_XAS.setStyleSheet('background-color: #4664AA;')
            else:
                self.emissionCalibration.setStyleSheet('background-color: #4664AA;')
                self.save_XAS.setStyleSheet('background-color: #4664AA;')
                self.plot_XAS.setStyleSheet('background-color: #4664AA;')
                
                
    def openLinearCanvas(self):
        if self.xas_measurement.path and self.emissionCalibration.params:
            print(self.emissionCalibration.params)
            xas = XAS(self.xas_measurement.path, self.emissionCalibration.params)
            xas_rot = array(xas.rotateXAS())
            self.lincanvas = LinearCallibration(xas_rot,self.app_icon)
            self.lincanvas.paramsSaved.connect(self.excitationCalibration.update)
            self.lincanvas.show()
        else:
            QMessageBox.critical(
                self,
                "Error loading the data",
                "Make sure you dragged in the .h5 file containing the measurement and did the emission callibration",
                buttons=QMessageBox.Cancel,
                defaultButton=QMessageBox.Cancel,
            )

    def openRefCanvas(self, path):
        self.refcanvas = CanvasRef(Ref(path).data,self.app_icon)
        self.refcanvas.paramsSaved.connect(self.emissionCalibration.set_params)
        self.refcanvas.closing.connect(self.show)
        self.hide()
        self.refcanvas.show()
        
        

    def plotXAS(self):
        if self.xas_measurement.path:
            emission_params = [0, 0, 1, 0]
            excitationParams = [1, 0]
            if self.emissionCalibration.params:
                emission_params = self.emissionCalibration.params
            if self.excitationCalibration.params[0] > 0:
                excitationParams = self.excitationCalibration.params
            print("Plotting")
            xas = XAS(self.xas_measurement.path, emission_params, excitationParams)
            xas_rot = array(xas.rotateXAS())
            self.canvas = DataPlot(xas_rot,self.app_icon)
            self.canvas.show()
        else:
            QMessageBox.critical(
                self,
                "Error loading the data",
                "Make sure you dragged in the .h5 file containing the measurement",
                buttons=QMessageBox.Cancel,
                defaultButton=QMessageBox.Cancel,
            )

    def saveXAS(self):
        if (
            self.xas_measurement.path
            and self.emissionCalibration.params
            and self.excitationCalibration.params[0] != 0
        ):
            print("Plotting")
            xas = XAS(
                self.xas_measurement.path,
                self.emissionCalibration.params,
                self.excitationCalibration.params,
            )
            xas_rot = array(xas.rotateXAS())
            self.BackgroundRemover = BackgroundRemover(xas_rot, self.app_icon)
            self.BackgroundRemover.show()
        else:
            QMessageBox.critical(
                self,
                "Error loading the data",
                "Make sure you dragged in the .h5 file containing the measurement and finished your callibration",
                buttons=QMessageBox.Cancel,
                defaultButton=QMessageBox.Cancel,
            )
    def save_params(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Parameters", "", "Parameter Files (*.param)", options=options
        )
        if fileName:
            emission_calib=""
            for value in self.emissionCalibration.params:
                emission_calib+=str(value)+";"
            excitation_calib=""
            for value in self.excitationCalibration.params:
                excitation_calib+=str(value)+";"
            with open(fileName,"w")as file:
                file.write("Emission Calibration\n"+emission_calib+"\nExcitation Calibration \n"+excitation_calib+"\n")

        
    def load_params(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Load Parameters", "", "Parameter Files (*.param)", options=options
        )
        if fileName:
            with open(fileName,"r")as file:
                i=0
                for line in file:
                    if i == 1:
                        params = line.replace(";"," ").split()
                        for j in range(0,len(params)):
                            params[j]=float(params[j])
                        self.emissionCalibration.set_params(params)
                    if i == 3:
                        params = line.replace(";"," ").split()
                        for j in range(0,len(params)):
                            params[j]=float(params[j])
                        self.excitationCalibration.update(*params)                        
                    i+=1
            self.loaded()


