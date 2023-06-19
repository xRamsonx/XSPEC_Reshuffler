#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 22:11:38 2023

@author: kai
"""
import os

from PyQt5.QtGui import QPainter, QBrush, QPalette, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QSlider,
    QStyle,
    QApplication,
    QFrame,
    QPushButton,
    QFileDialog,
    QStyleOptionSlider
)


class DragAndDropLabelwithButton(QFrame):
    fileDropped = pyqtSignal(str)

    def __init__(self, text, loadtext=None):
        super(DragAndDropLabelwithButton, self).__init__()
        self.setObjectName("DragAndDropLabelwithButton")
        self.file = text
        self.loadtext = loadtext
        print(self.loadtext)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.file_path = None
        self.setStyleSheet(
            "QFrame#DragAndDropLabelwithButton {border: 2px dashed #aaa; border-radius: 10px}"
        )
        self.label = QLabel("Drop " + self.file + " here\nor")
        self.label.setAlignment(Qt.AlignCenter)
        button = QPushButton("Select File")
        button.clicked.connect(self.chooseFile)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(button)
        layout.addStretch()
        self.setLayout(layout)

    def chooseFile(self):
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getSaveFileName()",
            "",
            "All Files (*);;Text Files (*.txt)",
            options=options,
        )
        if self.file_path:
            self.fileDropped.emit(self.file_path)
            self.setStyleSheet(
                "QFrame#DragAndDropLabelwithButton {border: 2px solid green; border-radius: 10px}"
            )
            filename = os.path.basename(self.file_path)
            if self.loadtext:
                self.label.setText(self.loadtext)
            else:
                self.label.setText(
                    filename
                    + " loaded\nDrag and drop anothor "
                    + self.file
                    + "\nto change the file\nor"
                )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet(
                "QFrame#DragAndDropLabelwithButton {border: 2px dashed #00f; border-radius: 10px}"
            )
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        if not self.file_path:
            self.setStyleSheet(
                "QFrame#DragAndDropLabelwithButton {border: 2px dashed #aaa; border-radius: 10px}"
            )
        else:
            self.setStyleSheet(
                "QFrame#DragAndDropLabelwithButton {border: 2px solid green; border-radius: 10px}"
            )

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.file_path = str(url.toLocalFile())
            self.fileDropped.emit(self.file_path)
        self.setStyleSheet(
            "QFrame#DragAndDropLabelwithButton {border: 2px solid green; border-radius: 10px}"
        )
        filename = os.path.basename(self.file_path)
        if self.loadtext:
            self.label.setText(self.loadtext)
        else:
            self.label.setText(
                filename
                + " loaded\nDrag and drop anothor "
                + self.file
                + "\nto change the file\nor"
            )
        event.accept()

class RangeSlider(QSlider):
    # Originated from
    # https://www.mail-archive.com/pyqt@riverbankcomputing.com/msg22889.html
    # Modification refered from
    # https://gist.github.com/Riateche/27e36977f7d5ea72cf4f
    sliderMoved = pyqtSignal(int, int)
    """ A slider for ranges.
    
        This class provides a dual-slider for ranges, where there is a defined
        maximum and minimum, as is a normal slider, but instead of having a
        single slider value, there are 2 slider values.
        
        This class emits the same signals as the QSlider base class, with the
        exception of valueChanged
    """
    def __init__(self, *args):
        super(RangeSlider, self).__init__(*args)

        self._low = self.minimum()
        self._high = self.maximum()

        self.pressed_control = QStyle.SC_None
        self.tick_interval = 0
        self.tick_position = QSlider.NoTicks
        self.hover_control = QStyle.SC_None
        self.click_offset = 0

        # 0 for the low, 1 for the high, -1 for both
        self.active_slider = 0

    def low(self):
        return self._low

    def setLow(self, low: int):
        self._low = low
        self.update()

    def high(self):
        return self._high

    def setHigh(self, high):
        self._high = high
        self.update()

    def paintEvent(self, event):
        # based on http://qt.gitorious.org/qt/qt/blobs/master/src/gui/widgets/qslider.cpp

        painter = QPainter(self)
        style = QApplication.style()

        # draw groove
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.siderValue = 0
        opt.sliderPosition = 0
        opt.subControls = QStyle.SC_SliderGroove
        if self.tickPosition() != self.NoTicks:
            opt.subControls |= QStyle.SC_SliderTickmarks
        style.drawComplexControl(QStyle.CC_Slider, opt, painter, self)
        groove = style.subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
        )

        # drawSpan
        # opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QStyle.SC_SliderGroove
        # if self.tickPosition() != self.NoTicks:
        #    opt.subControls |= QStyle.SC_SliderTickmarks
        opt.siderValue = 0
        # print(self._low)
        opt.sliderPosition = self._low
        low_rect = style.subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
        )
        opt.sliderPosition = self._high
        high_rect = style.subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
        )

        # print(low_rect, high_rect)
        low_pos = self.__pick(low_rect.center())
        high_pos = self.__pick(high_rect.center())

        min_pos = min(low_pos, high_pos)
        max_pos = max(low_pos, high_pos)

        c = QRect(low_rect.center(), high_rect.center()).center()
        # print(min_pos, max_pos, c)
        if opt.orientation == Qt.Horizontal:
            span_rect = QRect(QPoint(min_pos, c.y() - 2), QPoint(max_pos, c.y() + 1))
        else:
            span_rect = QRect(QPoint(c.x() - 2, min_pos), QPoint(c.x() + 1, max_pos))

        # self.initStyleOption(opt)
        # print(groove.x(), groove.y(), groove.width(), groove.height())
        if opt.orientation == Qt.Horizontal:
            groove.adjust(0, 0, -1, 0)
        else:
            groove.adjust(0, 0, 0, -1)

        if True:  # self.isEnabled():
            highlight = self.palette().color(QPalette.Highlight)
            painter.setBrush(QBrush(highlight))
            painter.setPen(QPen(highlight, 0))
            # painter.setPen(QPen(self.palette().color(QPalette.Dark), 0))
            """
            if opt.orientation == Qt.Horizontal:
                self.setupPainter(painter, opt.orientation, groove.center().x(), groove.top(), groove.center().x(), groove.bottom())
            else:
                self.setupPainter(painter, opt.orientation, groove.left(), groove.center().y(), groove.right(), groove.center().y())
            """
            # spanRect =
            painter.drawRect(span_rect.intersected(groove))
            # painter.drawRect(groove)

        for i, value in enumerate([self._low, self._high]):
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)

            # Only draw the groove for the first slider so it doesn't get drawn
            # on top of the existing ones every time
            if i == 0:
                opt.subControls = QStyle.SC_SliderHandle  # | QStyle.SC_SliderGroove
            else:
                opt.subControls = QStyle.SC_SliderHandle

            if self.tickPosition() != self.NoTicks:
                opt.subControls |= QStyle.SC_SliderTickmarks

            if self.pressed_control:
                opt.activeSubControls = self.pressed_control
            else:
                opt.activeSubControls = self.hover_control

            opt.sliderPosition = value
            opt.sliderValue = value
            style.drawComplexControl(QStyle.CC_Slider, opt, painter, self)

    def mousePressEvent(self, event):
        event.accept()

        style = QApplication.style()
        button = event.button()

        # In a normal slider control, when the user clicks on a point in the
        # slider's total range, but not on the slider part of the control the
        # control would jump the slider value to where the user clicked.
        # For this control, clicks which are not direct hits will slide both
        # slider parts

        if button:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)

            self.active_slider = -1

            for i, value in enumerate([self._low, self._high]):
                opt.sliderPosition = value
                hit = style.hitTestComplexControl(
                    style.CC_Slider, opt, event.pos(), self
                )
                if hit == style.SC_SliderHandle:
                    self.active_slider = i
                    self.pressed_control = hit

                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
                    self.setSliderDown(True)
                    break

            if self.active_slider < 0:
                self.pressed_control = QStyle.SC_SliderHandle
                self.click_offset = self.__pixelPosToRangeValue(
                    self.__pick(event.pos())
                )
                self.triggerAction(self.SliderMove)
                self.setRepeatAction(self.SliderNoAction)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.pressed_control != QStyle.SC_SliderHandle:
            event.ignore()
            return

        event.accept()
        new_pos = self.__pixelPosToRangeValue(self.__pick(event.pos()))
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        if self.active_slider < 0:
            offset = new_pos - self.click_offset
            self._high += offset
            self._low += offset
            if self._low < self.minimum():
                diff = self.minimum() - self._low
                self._low += diff
                self._high += diff
            if self._high > self.maximum():
                diff = self.maximum() - self._high
                self._low += diff
                self._high += diff
        elif self.active_slider == 0:
            if new_pos >= self._high:
                new_pos = self._high - 1
            self._low = new_pos
        else:
            if new_pos <= self._low:
                new_pos = self._low + 1
            self._high = new_pos

        self.click_offset = new_pos

        self.update()
        self.sliderMoved.emit(self._low, self._high)

    def __pick(self, pt):
        if self.orientation() == Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()

    def __pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = QApplication.style()

        gr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderGroove, self)
        sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1

        return style.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            pos - slider_min,
            slider_max - slider_min,
            opt.upsideDown,
        )