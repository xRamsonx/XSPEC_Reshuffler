#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 22:16:29 2023

@author: kai
"""

from numpy import (
    array,
    where,
    linspace,
    absolute
)
from numpy.linalg import norm
from PyQt5.QtCore import Qt, pyqtSignal, QLocale
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QAbstractSpinBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QPushButton,
    QMessageBox,
)
from scipy.optimize import curve_fit
from matplotlib.pyplot import figure, connect
from matplotlib.backends.backend_qt5agg import FigureCanvas
from h5py import File as open_h5py

from xspec_reshuffler.widgets import DragAndDropLabelwithButton, RangeSlider

def cubic(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

class EmissionCalibration(QFrame):
    openRefCanvas = pyqtSignal(str)
    updated = pyqtSignal()
    def __init__(self):
        
        super(EmissionCalibration, self).__init__()
        self.dragAndDrop = DragAndDropLabelwithButton(
            "reference file (.h5)",
            loadtext="Parameters extracted\nDrag and drop a reference file\nto change the parameters\nor",
        )
        self.dragAndDrop.fileDropped.connect(self.openRefCanvas.emit)
        self.cubic = CubicFunction(0,0, 1, 0)
        self.cubic.itemChanged.connect(self.set_params)
        self.params = []
        title = QLabel("Emission energy calibration")

        layout = QVBoxLayout()
        layout.addWidget(title, 10)
        layout.addWidget(self.dragAndDrop, 80)
        layout.addWidget(self.cubic,20)
        layout.setSpacing(10)
        self.setLayout(layout)
        self.setFrameShape(QFrame.Box)
        self.canvas_opened =False

    def set_params(self, params):
        self.params = params
        self.cubic.setParameters(params)
        self.updated.emit()

class CubicFunction(QWidget):
    itemChanged = pyqtSignal(float,float, float, float)

    def __init__(self, cube, jerk, slope, offset):
        super(CubicFunction, self).__init__()
        subtitle = QLabel("Where N =1,2,3,... is the measurement row")
        subtitle.setAlignment(Qt.AlignCenter)
        self.cube = QDoubleSpinBox()
        self.cube.setValue(cube)
        self.cube.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.cube.setMaximum(9999.99)
        self.cube.setMinimum(-9999.99)
        self.cube.setDecimals(9)
        self.cube.setLocale(QLocale(QLocale.English))
        self.cube.editingFinished.connect(self.update)
        
        self.jerk = QDoubleSpinBox()
        self.jerk.setValue(jerk)
        self.jerk.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.jerk.setMaximum(9999.99)
        self.jerk.setMinimum(-9999.99)
        self.jerk.setDecimals(9)
        self.jerk.setLocale(QLocale(QLocale.English))
        self.jerk.editingFinished.connect(self.update)
        
        self.slope = QDoubleSpinBox()
        self.slope.setValue(slope)
        self.slope.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.slope.setMaximum(9999.99)
        self.slope.setMinimum(-9999.99)
        self.slope.setDecimals(9)
        self.slope.setLocale(QLocale(QLocale.English))
        self.slope.editingFinished.connect(self.update)
        
        self.offset = QDoubleSpinBox()
        self.offset.setValue(offset)
        self.offset.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.offset.setMaximum(9999.99)
        self.offset.setMinimum(-9999.99)
        self.offset.setDecimals(9)
        self.offset.editingFinished.connect(self.update)
        self.offset.setLocale(QLocale(QLocale.English))

        linear_function_chooser = QHBoxLayout()
        linear_function_chooser.addStretch()
        linear_function_chooser.addWidget(QLabel("E_em="))
        linear_function_chooser.addWidget(self.cube)
        linear_function_chooser.addWidget(QLabel("* N^3 +"))       
        linear_function_chooser.addWidget(self.jerk)
        linear_function_chooser.addWidget(QLabel("* N^2 +"))
        linear_function_chooser.addWidget(self.slope)
        linear_function_chooser.addWidget(QLabel("* N +"))
        linear_function_chooser.addWidget(self.offset)
        linear_function_chooser.addStretch()

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(linear_function_chooser)
        layout.addWidget(subtitle)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)
        layout.addStretch()

        self.setLayout(layout)
        # self.setAlignment(Qt.AlignCenter)
        self.setAutoFillBackground(True)

    def setParameters(self,params):
        self.cube.setValue(params[0])
        self.jerk.setValue(params[1])
        self.slope.setValue(params[2])
        self.offset.setValue(params[3])

    def update(self):
        self.itemChanged.emit(
            
            self.cube.value(), self.jerk.value(), self.slope.value(), self.offset.value()
        )
        
class CanvasRef(QWidget):
    paramsSaved = pyqtSignal(list)
    closing = pyqtSignal()

    def __init__(self, Ref, app_icon, mode="points"):
        super(CanvasRef, self).__init__()
        self.setWindowTitle("XAS")
        self.setGeometry(100, 100, 1600, 1200)
        self.setWindowIcon(app_icon)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.setStyleSheet(" font-size: 12pt; ")
        
        self.entered = False
        self.figure = figure()
        self.axis = self.figure.add_subplot()
        self.canvas = FigureCanvas(self.figure)

        self.points = []
        self.plotData = []
        self.plotData.append(Ref)
        self.x = linspace(1, len(Ref), len(Ref))
        
        self.slider = RangeSlider(Qt.Horizontal)
        self.slider.setMinimumHeight(10)
        self.slider.setMinimum(int(min(self.x)))
        self.slider.setMaximum(int(max(self.x)))
        self.slider.setLow(int(min(self.x)))
        self.slider.setHigh(int(max(self.x)))
        self.slider.sliderMoved.connect(self.update)

        notice= QLabel("Drop other reference files into this window to add")
        label = QLabel("Peaks sorted by energies in eV")

        self.energy_sorter = EnergySorter()
        layout = QVBoxLayout()
        layout.addWidget(notice)
        layout.addWidget(self.canvas, 100)
        layout.addWidget(self.slider, 10)
        layout.addWidget(label)
        layout.addLayout(self.energy_sorter, 50)

        self.reset = QPushButton("Reset")
        self.reset.clicked.connect(self.reset_points)
        self.saveParams = QPushButton("Save parameters and close")
        self.saveParams.clicked.connect(self.save_parameters)
        buttons = QHBoxLayout()
        buttons.addWidget(self.reset)
        buttons.addWidget(self.saveParams)

        layout.addLayout(buttons, 10)

        self.setLayout(layout)
        connect("axes_enter_event", self.mouse_enter)
        connect("axes_leave_event", self.mouse_leave)
        connect("button_press_event", self.mouse_click)

        self.update(min(self.x), max(self.x))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.file_path = str(url.toLocalFile())
        data = Ref(self.file_path).data
        if not any((data == point).all() for point in self.plotData):
            self.plotData.append(data)
            self.update(*self.offsets)
        event.accept()

    def save_parameters(self):
        e_list = []
        for energy in self.energy_sorter.elisted:
            e_list.append(energy.value())
        
        e_list = sorted(e_list)
        e_list = list(reversed(e_list))
        peaks = sorted(self.energy_sorter.peaks)
        print(peaks)
        print(e_list)
        if not any(E == 0 for E in e_list):
            if len(e_list) > 4:   
                params, pcov = curve_fit(cubic, peaks, e_list)
                print("Parameters:", params)
                self.paramsSaved.emit(list(params))
                self.close()
            else:
                button = QMessageBox.critical(
                    self,
                    "Error too few points",
                    "You need at least 4 points for a cubic fit",
                    buttons=QMessageBox.Cancel,
                    defaultButton=QMessageBox.Cancel,
                )
                button.exec()
        else:
            button = QMessageBox.critical(
                self,
                "Error loading the data",
                "Some peaks are not set yet",
                buttons=QMessageBox.Cancel,
                defaultButton=QMessageBox.Cancel,
            )
            button.exec()

    def reset_points(self):
        self.points = []
        self.energy_sorter.reset()
        self.update(*self.offsets)

    def mouse_click(self, event):
        if self.entered:
            x = event.xdata
            if all(norm(array(point) - x) > 5 for point in self.points):
                self.points.append(x)
                self.update(*self.offsets)
            else:
                points = array(self.points)
                distances = absolute(points - x)
                i = int(where(distances == min(distances))[0])
                self.energy_sorter.remove(self.points[i])
                self.points.pop(i)
                self.update(*self.offsets)

    def mouse_enter(self, event):
        self.entered = True

    def mouse_leave(self, event):
        self.entered = False

    def update(self, low, upper):
        self.axis.cla()
        a, b = int(low), int(upper)
        self.offsets = [low, upper]
        maximum = 0
        minimum = min(self.plotData[0])
        for data in self.plotData:
            self.img = self.axis.plot(self.x, data)
            if max(data[a:b]) > maximum:
                maximum = max(data[a:b])
            if min(data[a:b]) < minimum:
                minimum = min(data[a:b])

        self.axis.set_xlabel("Emission Energy [ch]")
        self.axis.set_xlim(a, b)
        self.axis.set_ylabel("Intesity")
        self.axis.set_ylim(minimum, maximum)

        self.energy_sorter.update(self.points)
        for point in self.points:
            if point > a and point < b:
                self.axis.vlines(point, 0, maximum, "r")
        self.canvas.draw()
        
    def closeEvent(self,event):
        self.closing.emit()
        event.accept() 
        
class EnergySorter(QFormLayout):
    def __init__(self):
        super(EnergySorter, self).__init__()
        self.elisted = []
        self.peaks = []

    def update(self, peaks):
        for peak in peaks:
            if not peak in self.peaks:
                self.peaks.append(peak)
                box = QDoubleSpinBox()
                box.setValue(0)
                box.setButtonSymbols(QAbstractSpinBox.NoButtons)
                box.setMinimum(0)
                box.setMaximum(9999.99)
                box.setDecimals(6)
                box.setLocale(QLocale(QLocale.English))
                self.elisted.append(box)
                # to not have duplicates
                self.addRow("Peak at "+str(int(peak))+" ch", self.elisted[-1])

    def remove(self, peak):
        print(peak,self.peaks)
        i = int(where(self.peaks == peak)[0])
        self.peaks.pop(i)
        label = self.labelForField(self.elisted[i])
        if label is not None:
            label.deleteLater()
        self.elisted[i].deleteLater()
        self.elisted.pop(i)

    def reset(self):
        while len(self.peaks) > 0:
            self.remove(self.peaks[len(self.peaks) - 1])


class Ref:
    def __init__(self, file_path):
        with open_h5py(file_path, "r") as f:
            self.data = array(f["data"]["processed"]["sensor1d"]["XES"])[0][1]
