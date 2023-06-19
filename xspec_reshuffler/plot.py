#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 22:20:00 2023

@author: kai
"""
from numpy import (
    unique,
    flip,
    where,
    linspace,
    copy
)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout
)
from matplotlib.pyplot import figure, connect
from matplotlib.backends.backend_qt5agg import FigureCanvas

from xspec_reshuffler.widgets import RangeSlider


class DataPlot(QWidget):
    def __init__(self, XAS, app_icon):
        super(DataPlot, self).__init__()
        self.setWindowTitle("XAS")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(app_icon)
        self.entered = False
        self.figure = figure()
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.background = []
        self.points = []

        x_list, y_list, z_list = XAS.T
        self.x = unique(x_list)
        self.y = flip(unique(y_list))
        self.z = z_list.reshape(len(self.y), len(self.x))
        self.offsets = [0, len(self.x) - 1]
        self.img = self.axis.imshow(flip(self.z), aspect="auto")
        self.cbar = self.figure.colorbar(self.img)
        

        self.slider = RangeSlider(Qt.Horizontal)
        self.slider.setMinimumHeight(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.x) - 1)
        self.slider.setLow(0)
        self.slider.setHigh(len(self.x) - 1)
        self.slider.sliderMoved.connect(self.update)
        self.update(0, len(self.x))
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.slider)

        self.setLayout(layout)
        connect("axes_enter_event", self.mouse_enter)
        connect("axes_leave_event", self.mouse_leave)
        connect("button_press_event", self.mouse_click)

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
            if not [x_trans, x_trans] in self.points:
                self.points.append([x_trans, y_trans])
                self.update(*self.offsets)
            else:
                self.points.pop([x_trans, x_trans])
                self.update(*self.offsets)

    def mouse_enter(self, event):
        self.entered = True

    def mouse_leave(self, event):
        self.entered = False

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

        for point in self.points:
            if point[0] > self.x[a] and point[0] < self.x[b]:
                x, y = self.reTransform(*point)
                x = x - a
                self.axis.plot(x, y, "ro")
        self.scan_plot_list = {}
        self.canvas.draw()