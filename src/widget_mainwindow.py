#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/5/17 22:30 
# import pyqt5
import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
import qdarkstyle
import sys
import threading
import os
import socket
from widget_control_tello import TelloControllerWidget
from widget_path_planning import PathPlanningWidget
from tello import Tello
from utils import *


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.showMaximized()
        self.setWindowTitle("Tello Scan")
        self.tello_obj = Tello('', 8889)
        self.control_widget = TelloControllerWidget(self.tello_obj, self)
        self.path_widget = PathPlanningWidget()
        self.set_layout()

    def set_layout(self):
        self.hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.hsplitter.addWidget(self.path_widget)
        self.hsplitter.addWidget(self.control_widget)
        hlayout = QtWidgets.QHBoxLayout(self)
        # hlayout.addWidget(self.control_widget)
        hlayout.addWidget(self.hsplitter)
        self.setLayout(hlayout)

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '',
                                               "Are you sure to Exit？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            stop_thread(self.control_widget.thread_get_video)
            stop_thread(self.control_widget.thread_send_command)
            stop_thread(self.tello_obj.receive_thread)
            stop_thread(self.tello_obj.receive_video_thread)
            self.control_widget.stop_event.set()
            del self.tello_obj
            self.deleteLater()
        else:
            event.ignore()


class SavephotosWidget(QtWidgets.QWidget):
    def __init__(self):
        super(SavephotosWidget, self).__init__()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    myshow = MainWindow()  # 主窗口实例化
    sys.exit(app.exec_())



