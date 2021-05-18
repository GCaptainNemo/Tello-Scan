#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/5/18 9:46 
# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from PyQt5 import QtWidgets, QtGui, QtCore

import pyqtgraph.opengl as gl
import cv2
import matplotlib.pyplot as plt
import numpy as np




class PathPlanningWidget(QtWidgets.QWidget):
    def __init__(self):
        super(PathPlanningWidget, self).__init__()
        self.view_widget = gl.GLViewWidget()
        # self.view_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.view_widget.setBackgroundColor((35, 38, 41, 0))
        self.set_ui()

    def set_ui(self):
        self.browse_picture_widget = BrowsePictureWidget()
        hlayout = QtWidgets.QHBoxLayout()
        self.setLayout(hlayout)
        # hlayout.addWidget(self.view_widget)
        hlayout.addWidget(self.browse_picture_widget)


class BrowsePictureWidget(QtWidgets.QWidget):
    def __init__(self):
        super(BrowsePictureWidget, self).__init__()
        VSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vlayout = QtWidgets.QVBoxLayout(self)
        self.rgb_widget = MyWinPicture()
        self.output_widget = MyWinPicture()
        VSplitter.addWidget(self.rgb_widget)
        VSplitter.addWidget(self.output_widget)
        Hlayout = QtWidgets.QHBoxLayout()
        self.btn_browse_rgb = QtWidgets.QPushButton('Browse')
        self.btn_browse_rgb.clicked.connect(self.browse_rgb)
        self.btn_extract_points = QtWidgets.QPushButton('Extract points')
        self.btn_extract_points.clicked.connect(self.extract_feature_points)
        self.btn_registration = QtWidgets.QPushButton('Registrtion')
        self.btn_registration.clicked.connect(self.registration)

        Hlayout.addWidget(self.btn_browse_rgb)
        Hlayout.addWidget(self.btn_extract_points)
        Hlayout.addWidget(self.btn_registration)

        vlayout.addWidget(VSplitter)
        vlayout.addLayout(Hlayout)

    def browse_rgb(self):
        try:
            self.rgb_file_dir, filetype = QtWidgets.QFileDialog.getOpenFileName(self, '选择可见光图片', '',
                                                                                 'files(*.jpg , *.png)')
            print(self.rgb_file_dir, filetype)
            self.rgb_widget.pixmap = QtGui.QPixmap(self.rgb_file_dir)
            self.rgb_widget.repaint()
        except Exception as e:
            print(e)

    def extract_feature_points(self):
        try:
            self.feature_point_lst = []
            im_bgr = cv2.imread(self.rgb_file_dir)
            self.im_rgb = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB)
            fig = plt.figure('Manual Projective')
            self.ax_rgb = plt.subplot(111), plt.imshow(self.im_rgb), plt.title('RGB')
            self.ax_rgb[0].set_autoscale_on(False)
            fig.canvas.mpl_connect("button_press_event", self.press_feature_points)
            fig.canvas.mpl_connect("scroll_event", self.scroll_zoom_in)
            fig.canvas.mpl_connect('key_press_event', self.on_key_press)
            plt.show()
        except Exception as e:
            print(e)

    def press_feature_points(self, event):
        """ Click the mouse to extract the featured points."""
        try:
            x = event.xdata
            y = event.ydata
            if event.inaxes == self.ax_rgb[0]:
                event.inaxes.scatter(x, y, c='orange', s=150, alpha=1.0, marker='*')
                y_shape = self.im_rgb.shape[0]
                print("x = ", x)
                print("y = ", y_shape - y)
                print(self.im_rgb.shape)  # row, column
                self.feature_point_lst.append([x, y])
                event.inaxes.text(x, y, str(len(self.feature_point_lst)),
                                  fontdict={'size': 20, 'color': 'red'})
            event.inaxes.figure.canvas.draw()
        except Exception as e:
            print(e)

    def scroll_zoom_in(self, event):
        """ Scroll the mouse to zoom in(out) the picture."""
        try:
            # axtemp = event.inaxes
            axtemp = self.ax_rgb[0]

            x_min, x_max = axtemp.get_xlim()
            y_min, y_max = axtemp.get_ylim()
            fanwei_x = (x_max - x_min) / 10
            fanwei_y = (y_max - y_min) / 10
            if event.button == 'up':
                axtemp.set(xlim=(x_min + fanwei_x, x_max - fanwei_x), ylim=(y_min + fanwei_y, y_max - fanwei_y))
            elif event.button == 'down':
                axtemp.set(xlim=(x_min - fanwei_x, x_max + fanwei_x), ylim=(y_min - fanwei_y, y_max + fanwei_y))
            event.inaxes.figure.canvas.draw_idle()  # 绘图动作实时反映在图像上
        except Exception as e:
            print(e)

    def on_key_press(self, event):
        """ Use up, down, left, right to translate the picture."""
        try:
            axtemp = event.inaxes
            x_min, x_max = axtemp.get_xlim()
            y_min, y_max = axtemp.get_ylim()
            x_fanwei = (x_max - x_min) / 10
            y_fanwei = (y_max - y_min) / 10
            if event.key == 'up':
                axtemp.set(ylim=(y_min + y_fanwei, y_max + y_fanwei))
            elif event.key == 'down':
                axtemp.set(ylim=(y_min - y_fanwei, y_max - y_fanwei))
            elif event.key == 'left':
                axtemp.set(xlim=(x_min - x_fanwei, x_max - x_fanwei))
            elif event.key == 'right':
                axtemp.set(xlim=(x_min + x_fanwei, x_max + x_fanwei))
            elif event.key == 'ctrl+z':
                xlim = axtemp.get_xlim()
                ylim = axtemp.get_ylim()
                axtemp.cla()
                if axtemp == self.ax_rgb[0]:
                    self.feature_point_lst.pop()
                    axtemp.imshow(cv2.cvtColor(cv2.imread(self.rgb_file_dir), cv2.COLOR_BGR2RGB))
                    axtemp.set_title('RGB')
                    for i, pos in enumerate(self.feature_point_lst):
                        event.inaxes.scatter(pos[0], pos[1], c='orange', s=150, alpha=1.0, marker='*')
                        event.inaxes.text(pos[0], pos[1], i + 1, fontdict={'size': 20, 'color': 'red'})
                    axtemp.set(xlim=xlim, ylim=ylim)
            axtemp.figure.canvas.draw_idle()
        except Exception as e:
            print(e)

    def registration(self):
        try:

            feature_pos = np.array(self.feature_point_lst[:4], dtype='float32')
            obj_pos = np.array([[0, 1000], [1000, 1000], [1000, 0], [0, 0]])
            homography_matrix = cv2.findHomography(feature_pos, obj_pos)
            dst = cv2.warpPerspective(self.im_rgb, homography_matrix[0], (1000, 1000))
            img = QtGui.QImage(dst, dst.shape[1],
                                 dst.shape[0], QtGui.QImage.Format_RGB888)
            self.output_widget.pixmap = QtGui.QPixmap.fromImage(img)
            self.output_widget.repaint()
        except Exception as e:
            print(e)


class MyWinPicture(QtWidgets.QWidget):
    def __init__(self):
        """
        Rewrite Qwidget to display pictures.
        param flag_:
        Two mode: 1. flag_ = 1, display through pictures address(self.dir)
                  2. flag_ = 0 display through pictures (self.picture_matrix)
        """
        super(MyWinPicture, self).__init__()
        self.pixmap = None

    def paintEvent(self, event):
        try:
            if self.pixmap is not None:
                painter = QtGui.QPainter(self)
                painter.drawPixmap(self.rect(), self.pixmap)
        except Exception as e:
            print(e)

