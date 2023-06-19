#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 22:20:12 2023

@author: kai
"""
from numpy import (
    array,
    unique,
    flip,
    where,
    linspace,
    copy
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
    QFrame,
    QPushButton
)
from scipy.optimize import curve_fit
from matplotlib.pyplot import figure, connect
from matplotlib.backends.backend_qt5agg import FigureCanvas

from xspec_reshuffler.widgets import RangeSlider

def linear(x, a, b):
    return a * x + b

class ExcitationCalibration(QFrame):
    openLinearCanvas = pyqtSignal()
    updated = pyqtSignal()
    
    def __init__(self):
        super(ExcitationCalibration, self).__init__()
        self.params = [1,0]
        self.path = None
        title = QLabel("Excitation energy calibration")
        self.linear_function = LinearFunction(*self.params)
        self.linear_function.itemChanged.connect(self.update)
        self.choose_linear_function = QPushButton("Extract parameters from RIXS map")
        self.choose_linear_function.clicked.connect(self.open_canvas)
        layout = QVBoxLayout()
        layout.addWidget(title, 10)
        layout.addWidget(self.linear_function, 100)
        layout.addWidget(self.choose_linear_function, 10)

        self.setFrameShape(QFrame.Box)
        self.setLayout(layout)

    def update(self, slope, offset):
        self.params=[slope,offset]
        self.linear_function.setParameters(slope, offset)
        self.updated.emit()

    def open_canvas(self):
        self.openLinearCanvas.emit()
        

class LinearCallibration(QWidget):
    paramsSaved = pyqtSignal(float, float)
    closed = pyqtSignal()

    def __init__(self, XAS, app_icon):
        super(LinearCallibration, self).__init__()
        self.setWindowTitle("XAS")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(app_icon)
        self.entered = False
        self.figure = figure()
        self.axis = self.figure.add_subplot()
        self.canvas = FigureCanvas(self.figure)
        self.background = []
        self.points = []
        self.params = []

        x_list, y_list, z_list = XAS.T
        self.x = unique(x_list)
        self.y = flip(unique(y_list))
        self.z = z_list.reshape(len(self.y), len(self.x))
        self.offsets = [0, len(self.x) - 1]
        self.img = self.axis.imshow(flip(self.z), aspect="auto")
        self.cbar = self.figure.colorbar(self.img)
        self.update(0, len(self.x))

        self.slider = RangeSlider(Qt.Horizontal)
        self.slider.setMinimumHeight(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.x) - 1)
        self.slider.setLow(0)
        self.slider.setHigh(len(self.x) - 1)
        self.slider.sliderMoved.connect(self.update)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.slider)

        self.reset = QPushButton("Reset")
        self.reset.clicked.connect(self.reset_points)
        self.saveParams = QPushButton("Save parameters and close")
        self.saveParams.clicked.connect(self.save_parameters)
        buttons = QHBoxLayout()
        buttons.addWidget(self.reset)
        buttons.addWidget(self.saveParams)

        layout.addLayout(buttons)

        self.setLayout(layout)
        connect("axes_enter_event", self.mouse_enter)
        connect("axes_leave_event", self.mouse_leave)
        connect("button_press_event", self.mouse_click)

    def reset_points(self):
        self.points = []
        self.update(*self.offsets)

    def save_parameters(self):
        if self.params.size > 0:
            self.paramsSaved.emit(1 / self.params[0], -self.params[1] / self.params[0])
        self.close()

    def coordTransform(self, x, y):
        x = self.x[int(x) + self.offsets[0]]
        y = self.y[int(y)]
        return x, y

    def reTransform(self, x, y):
        x = where(self.x == x)
        y = where(self.y == y)
        return x[0], y[0]

    def mouse_click(self, event):
        if self.entered:
            x, y = event.xdata, event.ydata
            x_trans, y_trans = self.coordTransform(x, y)

            if all(
                norm(array([x_trans, y_trans]) - array(point)) > 3
                for point in self.points
            ):
                self.points.append([x_trans, y_trans])
                self.update(*self.offsets)
            else:
                points = array(self.points)
                distances = norm(points - [x_trans, y_trans], axis=1)
                self.points.pop(int(where(distances == min(distances))[0]))
                self.update(*self.offsets)

    def mouse_enter(self, event):
        self.entered = True

    def mouse_leave(self, event):
        self.entered = False

    def closeEvent(self, event):
        self.closed.emit()  # Signal erzeugen
        event.accept()  # let the window close

    def update(self, low, upper):
        self.axis.cla()
        m = len(self.x)
        a, b = low, upper - 1
        data = copy(flip(self.z[:, m - b : m - a]))

        self.img = self.axis.imshow(data, aspect="auto")
        if [low, upper] != self.offsets:
            self.offsets = [low, upper]
            self.cbar.mappable.set_clim(vmin=data.min(),vmax=data.max()) #this works
            self.cbar.draw_all()

        ticks = linspace(0, len(self.y) - 1, 10, endpoint=True)
        self.axis.set_ylim(len(self.y), 0)
        self.axis.set_yticks(ticks)
        ticks = ticks.astype("int32")
        self.axis.set_yticklabels(self.y[ticks].astype("int32"))
        self.axis.set_xlabel("Emission Energy")

        ticks = linspace(0, b - a, 10, endpoint=True)
        self.axis.set_xlim(0, b - a)
        self.axis.set_xticks(ticks)
        ticks = ticks.astype("int32")
        self.axis.set_xticklabels(self.x[ticks + a].astype("int32"))
        self.axis.set_ylabel("Excitation Energy")

        point_list_real = []
        point_list_transformed = []
        for point in self.points:
            point_list_real.append([point[0], point[1]])
            if point[0] > self.x[a] and point[0] < self.x[b]:
                x, y = self.reTransform(*point)
                x = x - a
                point_list_transformed.append([x[0], y[0]])
                self.axis.plot(x, y, "ro")
        point_list_real = array(point_list_real).T
        point_list_transformed = array(point_list_transformed).T

        if (
            point_list_real
        ).size > 2 and point_list_real.size == point_list_transformed.size:  # 2 entries per point
            p, p_cov = curve_fit(linear, *point_list_transformed)
            x = linspace(0, b - a)
            self.axis.plot(x, linear(x, *p))
            self.params, p_cov = curve_fit(linear, *point_list_real)
        self.canvas.draw()
        
class LinearFunction(QWidget):
    itemChanged = pyqtSignal(float, float)

    def __init__(self, slope, offset):
        super(LinearFunction, self).__init__()
        subtitle = QLabel("Where N =1,2,3,... is the measurement row")
        subtitle.setAlignment(Qt.AlignCenter)
        self.slope = QDoubleSpinBox()
        self.slope.setValue(slope)
        self.slope.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.slope.setMaximum(9999.99)
        self.slope.setMinimum(-9999.99)
        self.slope.setDecimals(9)
        self.slope.setLocale(QLocale(QLocale.English))
        self.slope.valueChanged.connect(self.update)
        self.offset = QDoubleSpinBox()
        self.offset.setValue(offset)
        self.offset.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.offset.setMaximum(9999.99)
        self.offset.setMinimum(-9999.99)
        self.offset.setDecimals(9)
        self.offset.valueChanged.connect(self.update)
        self.offset.setLocale(QLocale(QLocale.English))

        linear_function_chooser = QHBoxLayout()
        linear_function_chooser.addStretch()
        linear_function_chooser.addWidget(QLabel("E_xc="))
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

    def setParameters(self, slope, offset):
        self.slope.setValue(slope)
        self.offset.setValue(offset)

    def update(self):
        self.itemChanged.emit(self.slope.value(), self.offset.value())