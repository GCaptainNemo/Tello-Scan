#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/5/18 9:46 

from PyQt5 import QtWidgets, QtGui
import pyqtgraph.opengl as gl


class PathPlanningWidget(QtWidgets.QWidget):
    def __init__(self):
        super(PathPlanningWidget, self).__init__()
        self.view_widget = gl.GLViewWidget()
        # self.view_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.view_widget.setBackgroundColor((35, 38, 41, 0))
        self.set_ui()

    def set_ui(self):
        vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(vlayout)
        vlayout.addWidget(self.view_widget)


