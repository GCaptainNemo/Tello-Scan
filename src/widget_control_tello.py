#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/5/17 23:38 


from PyQt5 import QtWidgets, QtCore, QtGui
import threading
import time
import datetime
import os
import cv2


class TelloControllerWidget(QtWidgets.QWidget):
    def __init__(self, tello_obj, parent):
        super(TelloControllerWidget, self).__init__(parent)
        self.tello_obj = tello_obj  # videostream device
        # self.outputPath = outputpath  # the path that save pictures created by clicking the takeSnapshot button
        self.stop_event = threading.Event()
        self.stop_event.clear()
        self.distance = 0.25  # default distance for 'move' cmd
        self.degree = 0  # default degree for 'cw' or 'ccw' cmd
        self.is_setpixmap = False

        # two thread: one to receive videos, another to send command
        self.thread_get_video = threading.Thread(target=self.video_loop)
        self.thread_get_video.start()
        self.thread_send_command = threading.Thread(target=self._sending_command)
        self.thread_send_command.start()
        self.output_path = "./image"
        self.logger_text = ""
        self.set_ui()

    def set_ui(self):
        vlayout = QtWidgets.QVBoxLayout(self)
        # self.label_show = QtWidgets.QLabel("")
        # self.label_show.setScaledContents(True)
        # # self.subwidget = QtWidgets.QWidget()
        #
        # vlayout.addWidget(self.label_show)
        self.text_widget = QtWidgets.QTextEdit()
        vlayout.addWidget(self.text_widget)
        self.set_readme()
        hlayout_1 = QtWidgets.QHBoxLayout()
        hlayout_2 = QtWidgets.QHBoxLayout()
        hlayout_3 = QtWidgets.QHBoxLayout()
        hlayout_4 = QtWidgets.QHBoxLayout()

        self.show_btn = QtWidgets.QPushButton("Show")
        self.close_btn = QtWidgets.QPushButton("Close")
        self.take_off_btn = QtWidgets.QPushButton("Take off")
        self.land_btn = QtWidgets.QPushButton("Land")
        self.show_btn.clicked.connect(self.tello_show)
        self.close_btn.clicked.connect(self.tello_close)

        self.take_off_btn.clicked.connect(self.tello_take_off)
        self.land_btn.clicked.connect(self.tello_landing)
        hlayout_1.addWidget(self.show_btn)
        hlayout_1.addWidget(self.close_btn)
        hlayout_1.addWidget(self.take_off_btn)
        hlayout_1.addWidget(self.land_btn)

        self.flip_forward_btn = QtWidgets.QPushButton("Flip forward")
        self.flip_backward_btn = QtWidgets.QPushButton("Flip backward")
        self.flip_right_btn = QtWidgets.QPushButton("Flip right")
        self.flip_left_btn = QtWidgets.QPushButton("Flip left")
        hlayout_2.addWidget(self.flip_forward_btn)
        hlayout_2.addWidget(self.flip_backward_btn)
        hlayout_2.addWidget(self.flip_right_btn)
        hlayout_2.addWidget(self.flip_left_btn)
        self.flip_forward_btn.clicked.connect(self.tello_flip_f)
        self.flip_backward_btn.clicked.connect(self.tello_flip_b)
        self.flip_right_btn.clicked.connect(self.tello_flip_r)
        self.flip_left_btn.clicked.connect(self.tello_flip_l)
        vlayout.addLayout(hlayout_1)
        vlayout.addLayout(hlayout_2)

        self.dist_label = QtWidgets.QLabel("distance: 0.25m")
        self.dist_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.dist_slider.setRange(25, 500)  # 3
        self.dist_slider.valueChanged.connect(self.on_change_dist)
        self.dst_button = QtWidgets.QPushButton("ok")

        hlayout_3.addWidget(self.dist_label)
        hlayout_3.addWidget(self.dist_slider)
        hlayout_3.addWidget(self.dst_button)
        self.dst_button.clicked.connect(self.confirm_dst)
        self.degree_label = QtWidgets.QLabel("degree: 0°")
        self.degree_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.degree_slider.setRange(0, 360)  # 3
        self.degree_slider.valueChanged.connect(self.on_change_degree)
        self.degree_button = QtWidgets.QPushButton("ok")
        self.degree_button.clicked.connect(self.confirm_degree)

        hlayout_4.addWidget(self.degree_label)
        hlayout_4.addWidget(self.degree_slider)
        hlayout_4.addWidget(self.degree_button)

        vlayout.addLayout(hlayout_3)
        vlayout.addLayout(hlayout_4)
        self.setLayout(vlayout)

    def set_readme(self):
        text = " This Controller map keyboard inputs to Tello control commands." \
               " Adjust the trackbar to reset distance and degree parameter\n\n"\
               " ---------------------------------------------------------\n"\
               "W - Move Tello Up\n" \
               "S - Move Tello Down\n" \
               "A - Rotate Tello Counter-Clockwise\n" \
               "D - Rotate Tello Clockwise\n" \
               "Arrow Up - Move Tello Forward\n" \
               "Arrow Down - Move Tello Backward\n" \
               "Arrow Left - Move Tello Left\n"\
               "Arrow Right - Move Tello Right"
        self.text_widget.setText(text)
        self.text_widget.setReadOnly(True)

    def on_change_dist(self):
        try:
            self.dist_label.setText("distance:" + str(float(self.dist_slider.value()) / 100) + "m")
        except Exception as e:
            print(e)

    def on_change_degree(self):
        try:
            self.degree_label.setText("degree:" + str(self.degree_slider.value()) + "°")
        except Exception as e:
            print(e)

    def confirm_degree(self):
        self.degree = self.degree_slider.value()

    def confirm_dst(self):
        self.distance = float(self.dist_slider.value()) / 100
        print "self.distance = ", self.distance

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.on_keypress_up()
        elif event.key() == QtCore.Qt.Key_Down:
            self.on_keypress_down()
        elif event.key() == QtCore.Qt.Key_Left:
            self.on_keypress_left()
        elif event.key() == QtCore.Qt.Key_Right:
            self.on_keypress_right()
        elif event.key() == QtCore.Qt.Key_W:
            self.on_keypress_w()
        elif event.key() == QtCore.Qt.Key_S:
            self.on_keypress_s()
        elif event.key() == QtCore.Qt.Key_A:
            self.on_keypress_a()
        elif event.key() == QtCore.Qt.Key_D:
            self.on_keypress_d()
        elif event.key() == QtCore.Qt.Key_Enter:
            self.on_keypress_enter()

    def tello_show(self):
        print("in tello show")
        self.show_video_widget = ShowVideoWindow()
        self.show_video_widget.signal_snap_shot.connect(self.snap_shot)
        self.show_video_widget.signal_freeze.connect(self.freeze_videos)
        self.show_video_widget.show()
        self.is_setpixmap = True

    def snap_shot(self):
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.output_path, filename))
        cv2.imwrite(p, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
        print("[INFO] saved {}".format(filename))

    def freeze_videos(self, opt):
        if opt == "Start":
            self.tello_obj.video_freeze(False)
        elif opt == "Stop":
            self.tello_obj.video_freeze(True)

    def tello_close(self):
        self.show_video_widget.close()
        self.is_setpixmap = False

    def _sending_command(self):
        """
        start a while loop that sends 'command' to tello every 5 second
        """
        while True:
            self.tello_obj.send_command('command')
            time.sleep(5)

    def video_loop(self):
        try:
            while not self.stop_event.is_set():
                self.frame = self.tello_obj.read()
                if self.frame is None or self.frame.size == 0:
                    time.sleep(0.1)
                    continue
                if self.is_setpixmap:
                    img = QtGui.QImage(self.frame,
                                       self.frame.shape[1],
                                       self.frame.shape[0],
                                       QtGui.QImage.Format_RGB888)
                    self.show_video_widget.label_show.setPixmap(QtGui.QPixmap.fromImage(img))
                time.sleep(0.05)
        except RuntimeError, e:
            print("[INFO] caught a RuntimeError")

    def tello_take_off(self):
        return self.tello_obj.takeoff()

    def tello_landing(self):
        return self.tello_obj.land()

    def on_keypress_w(self):
        print "up %d m" % self.distance
        self.tello_obj.move_up(self.distance)

    def on_keypress_s(self):
        print "down %d m" % self.distance
        self.tello_obj.move_down(self.distance)

    def on_keypress_a(self):
        print "ccw %d degree" % self.degree
        self.tello_obj.rotate_ccw(self.degree)

    def on_keypress_d(self):
        print "cw %d m" % self.degree
        self.tello_obj.rotate_cw(self.degree)

    def on_keypress_up(self):
        print "forward %d m" % self.distance
        self.tello_obj.move_forward(self.distance)

    def on_keypress_down(self):
        print "backward %d m" % self.distance
        self.tello_obj.move_backward(self.distance)

    def on_keypress_left(self):
        print "left %d m" % self.distance
        self.tello_obj.move_left(self.distance)

    def on_keypress_right(self):
        print "right %d m" % self.distance
        self.tello_obj.move_right(self.distance)

    def on_keypress_enter(self):
        if self.frame is not None:
            self.registerFace()
        self.tmp_f.focus_set()

    def tello_flip_l(self):
        return self.tello_obj.flip('l')

    def tello_flip_r(self):
        return self.tello_obj.flip('r')

    def tello_flip_f(self):
        return self.tello_obj.flip('f')

    def tello_flip_b(self):
        return self.tello_obj.flip('b')


class ShowVideoWindow(QtWidgets.QWidget):
    signal_freeze = QtCore.pyqtSignal(str)
    signal_snap_shot = QtCore.pyqtSignal()
    def __init__(self):
        super(ShowVideoWindow, self).__init__()
        self.set_ui()
        # self.setWindowFlags(
        #     QtCore.Qt.WindowMinimizeButtonHint |
        #     QtCore.Qt.WindowMaximizeButtonHint)

    def set_ui(self):
        self.label_show = QtWidgets.QLabel("")
        self.label_show.setScaledContents(True)
        # self.subwidget = QtWidgets.QWidget()
        self.radio_btn1 = QtWidgets.QRadioButton("Start")
        self.radio_btn1.setChecked(True)
        self.radio_btn1.toggled.connect(lambda: self.btnstate(self.radio_btn1))
        self.radio_btn2 = QtWidgets.QRadioButton("Stop")
        self.radio_btn2.toggled.connect(lambda: self.btnstate(self.radio_btn2))
        self.snap_btn = QtWidgets.QPushButton("Snapshot")
        self.snap_btn.clicked.connect(self.snap_shot)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.label_show)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.radio_btn1)
        hlayout.addWidget(self.radio_btn2)
        hlayout.addWidget(self.snap_btn)
        vlayout.addLayout(hlayout)
        self.setLayout(vlayout)
        # self.label_show.setFixedSize(self.label_show.size())

    def snap_shot(self):
        try:
            self.signal_snap_shot.emit()

        except Exception as e:
            print e

    def btnstate(self, btn):
        self.signal_freeze.emit(btn.text())
