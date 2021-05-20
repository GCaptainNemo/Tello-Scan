#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/5/18 9:46 
# coding=utf8
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import cv2
import matplotlib.pyplot as plt
import numpy as np


class PathPlanningWidget(QtWidgets.QWidget):
    signal_trajectory_point = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super(PathPlanningWidget, self).__init__(parent)
        self.view_widget = gl.GLViewWidget()
        self.view_widget.setBackgroundColor((35, 38, 41, 0))
        self.plot_grid_axis()
        self.dst_img = None
        self.plt_arrow = True
        self.set_ui()

    def set_ui(self):
        hlayout = QtWidgets.QHBoxLayout()
        self.path_planning_widget = QtWidgets.QWidget()
        vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vsplitter.addWidget(self.view_widget)
        vsplitter.addWidget(self.path_planning_widget)
        self.setLayout(hlayout)
        hlayout.addWidget(vsplitter)
        path_plan_vlayout = QtWidgets.QVBoxLayout(self.path_planning_widget)
        path_plan_hlayout_1 = QtWidgets.QHBoxLayout()
        path_plan_hlayout_2 = QtWidgets.QHBoxLayout()

        self.region_btn = QtWidgets.QPushButton("Region Selection")
        self.x_num_label = QtWidgets.QLabel("X point num:")
        self.x_num_lineedit = QtWidgets.QLineEdit()
        self.y_num_label = QtWidgets.QLabel("Y point num:")
        self.y_num_lineedit = QtWidgets.QLineEdit()
        self.z_num_label = QtWidgets.QLabel("Z point num:")
        self.z_num_lineedit = QtWidgets.QLineEdit()
        self.z_interval_label = QtWidgets.QLabel("Z-axis interval(m):")
        self.z_interval_lineedit = QtWidgets.QLineEdit()
        self.confirm_btn = QtWidgets.QPushButton("OK")
        self.start_trajectory_btn = QtWidgets.QPushButton("Follow the path")
        self.start_trajectory_btn.clicked.connect(self.start_trajectory)
        path_plan_hlayout_1.addWidget(self.region_btn)
        path_plan_hlayout_1.addWidget(self.x_num_label)
        path_plan_hlayout_1.addWidget(self.x_num_lineedit)
        path_plan_hlayout_1.addWidget(self.y_num_label)
        path_plan_hlayout_1.addWidget(self.y_num_lineedit)

        path_plan_hlayout_2.addWidget(self.z_num_label)
        path_plan_hlayout_2.addWidget(self.z_num_lineedit)
        path_plan_hlayout_2.addWidget(self.z_interval_label)
        path_plan_hlayout_2.addWidget(self.z_interval_lineedit)
        path_plan_hlayout_2.addWidget(self.confirm_btn)
        path_plan_hlayout_2.addWidget(self.start_trajectory_btn)

        path_plan_vlayout.addLayout(path_plan_hlayout_1)
        path_plan_vlayout.addLayout(path_plan_hlayout_2)
        self.region_btn.clicked.connect(self.region_selection)
        self.confirm_btn.clicked.connect(self.confirm)

    def start_trajectory(self):
        self.signal_trajectory_point.emit(self.lst_xyz)

    def confirm(self):
        self.replot()
        if self.dst_img is not None:
            self.plot_image()
        x_num = int(self.x_num_lineedit.text())
        y_num = int(self.y_num_lineedit.text())
        z_num = int(self.z_num_lineedit.text())
        z_interval = float(self.z_interval_lineedit.text()) * 100
        if self.dst_img is not None:
            x_interval = float(self.dst_img.shape[0]) / (max(x_num, 2) - 1)
            y_interval = float(self.l.shape[1]) / (max(y_num, 2) - 1)
        else:
            x_interval = 100
            y_interval = 100
        z_translate = 300

        # #################################################
        # add camera
        # #################################################
        self.lst_xyz = []
        for z in range(z_num):
            lst_xy = []
            for y in range(y_num):
                lst = []
                for x in range(x_num):
                    md = pg.opengl.MeshData.sphere(rows=10, cols=20)
                    pos = pg.opengl.GLMeshItem(meshdata=md, smooth=True,
                                                color=(.7019607843137254, .8901960784313725, .9607843137254902, .5),
                                                shader='shaded',
                                                drawFaces=True)
                    pos_array = np.array([x_interval * x, y_interval * y, z_interval * z + z_translate])
                    lst.append(pos_array)
                    pos.translate(pos_array[0], pos_array[1], pos_array[2])
                    pos.scale(10, 10, 10)
                    self.view_widget.addItem(pos)
                if y % 2 == 1:
                    lst.reverse()
                lst_xy += lst
            if z % 2 == 1:
                lst_xy.reverse()
            self.lst_xyz += lst_xy

        # ############################################################
        # plot trajectory
        # ############################################################
        print("plt_arrow = ", self.plt_arrow)
        if self.plt_arrow:
            for i in range(len(self.lst_xyz) - 1):
                pos = np.array([self.lst_xyz[i], self.lst_xyz[i + 1]])
                self.line_item_x = gl.GLLinePlotItem(pos=pos,
                                                     color=(.7019607843137254, .8901960784313725, .9607843137254902, .5),
                                                     width=10)
                self.view_widget.addItem(self.line_item_x)

    def region_selection(self):
        self.browse_picture_widget = BrowsePictureWidget()
        self.browse_picture_widget.signal_img.connect(self.slot_get_image)
        self.browse_picture_widget.resize(1000, 800)
        self.browse_picture_widget.showNormal()

    def slot_get_image(self, dst_img):
        dst_img = dst_img[0]
        dst_img = cv2.flip(dst_img, 0)  # flip vertical
        self.dst_img = dst_img.transpose((1, 0, 2))  # row, column to x, y
        self.plot_image()

    def replot(self):
        self.view_widget.clear()
        self.plot_grid_axis()

    def plot_image(self):
        self.replot()
        tex3 = pg.makeRGBA(self.dst_img, levels=[0, 255])[0]  # xy plane
        v3 = gl.GLImageItem(tex3)
        self.view_widget.addItem(v3)

    def plot_grid_axis(self):
        self.grid_item = gl.GLGridItem()  # 画网格
        self.grid_item.scale(100, 100, 100)
        # self.grid.translate(self.translate_pos[0], self.translate_pos[1], self.translate_pos[2])
        self.view_widget.addItem(self.grid_item)
        x_axis_pos = np.array([[-500, -500, 0], [0, -500, 0]])
        self.line_item_x = gl.GLLinePlotItem(pos=x_axis_pos, color="r")
        y_axis_pos = np.array([[-500, -500, 0], [-500, 0, 0]])
        self.line_item_y = gl.GLLinePlotItem(pos=y_axis_pos, color="g")
        y_axis_pos = np.array([[-500, -500, 0], [-500, -500, 500]])
        self.line_item_z = gl.GLLinePlotItem(pos=y_axis_pos, color="b")
        self.view_widget.addItem(self.line_item_x)
        self.view_widget.addItem(self.line_item_y)
        self.view_widget.addItem(self.line_item_z)


class BrowsePictureWidget(QtWidgets.QWidget):
    signal_img = QtCore.pyqtSignal(list)
    def __init__(self):
        super(BrowsePictureWidget, self).__init__()
        VSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vlayout = QtWidgets.QVBoxLayout(self)
        self.rgb_widget = MyWinPicture()
        self.output_widget = MyWinPicture()
        VSplitter.addWidget(self.rgb_widget)
        VSplitter.addWidget(self.output_widget)
        Hlayout_1 = QtWidgets.QHBoxLayout()
        self.btn_browse_rgb = QtWidgets.QPushButton('Browse')
        self.btn_browse_rgb.clicked.connect(self.browse_rgb)
        self.btn_extract_points = QtWidgets.QPushButton('Extract points')
        self.btn_extract_points.clicked.connect(self.extract_feature_points)
        self.btn_registration = QtWidgets.QPushButton('Registrtion')
        self.btn_registration.clicked.connect(self.registration)

        # ####################################################
        Hlayout_1.addWidget(self.btn_browse_rgb)
        Hlayout_1.addWidget(self.btn_extract_points)
        Hlayout_1.addWidget(self.btn_registration)
        Hlayout_2 = QtWidgets.QHBoxLayout()
        self.width_label = QtWidgets.QLabel("Width(m):")
        self.width_lineedit = QtWidgets.QLineEdit()
        self.height_label = QtWidgets.QLabel("Height(m):")
        self.height_lineedit = QtWidgets.QLineEdit()
        self.confirm_btn = QtWidgets.QPushButton("OK")
        Hlayout_2.addWidget(self.width_label)
        Hlayout_2.addWidget(self.width_lineedit)
        Hlayout_2.addWidget(self.height_label)
        Hlayout_2.addWidget(self.height_lineedit)
        Hlayout_2.addWidget(self.confirm_btn)
        self.confirm_btn.clicked.connect(self.confirm)
        # #############################################################

        vlayout.addWidget(VSplitter)
        vlayout.addLayout(Hlayout_1)
        vlayout.addLayout(Hlayout_2)

        self.setWindowTitle("Region selection")

    def confirm(self):
        width = int(self.width_lineedit.text())
        height = int(self.height_lineedit.text())
        resize_img = cv2.resize(self.dst, [height * 100, width * 100])
        self.signal_img.emit([resize_img])
        self.close()

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
            self.dst = cv2.warpPerspective(self.im_rgb, homography_matrix[0], (1000, 1000))
            dst_img = QtGui.QImage(self.dst, self.dst.shape[1],
                                 self.dst.shape[0], QtGui.QImage.Format_RGB888)
            self.output_widget.pixmap = QtGui.QPixmap.fromImage(dst_img)
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

