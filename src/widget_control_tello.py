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

        # two thread: one to receive videos, another to send command
        self.thread_get_video = threading.Thread(target=self.video_loop, args=())
        self.thread_get_video.start()
        self.thread_send_command = threading.Thread(target=self._sending_command)
        self.thread_send_command.start()
        self.output_path = "./image"
        self.logger_text = ""
        self.set_ui()

    def set_ui(self):
        vlayout = QtWidgets.QVBoxLayout(self)
        self.label_show = QtWidgets.QLabel("")
        self.label_show.setScaledContents(True)
        # self.subwidget = QtWidgets.QWidget()

        vlayout.addWidget(self.label_show)
        self.text_widget = QtWidgets.QTextEdit()
        vlayout.addWidget(self.text_widget)
        self.set_readme()
        hlayout_1 = QtWidgets.QHBoxLayout()
        hlayout_2 = QtWidgets.QHBoxLayout()
        hlayout_3 = QtWidgets.QHBoxLayout()
        hlayout_4 = QtWidgets.QHBoxLayout()

        self.radio_btn1 = QtWidgets.QRadioButton("start")
        self.radio_btn1.setChecked(True)
        self.radio_btn1.toggled.connect(lambda: self.btnstate(self.radio_btn1))
        self.radio_btn2 = QtWidgets.QRadioButton("stop")
        self.radio_btn2.toggled.connect(lambda: self.btnstate(self.radio_btn2))
        self.snap_btn = QtWidgets.QPushButton("Snapshot")
        self.snap_btn.clicked.connect(self.snap_shot)
        self.take_off_btn = QtWidgets.QPushButton("Take off")
        self.land_btn = QtWidgets.QPushButton("land")
        self.take_off_btn.clicked.connect(self.tello_take_off)
        self.land_btn.clicked.connect(self.tello_landing)
        hlayout_1.addWidget(self.radio_btn1)
        hlayout_1.addWidget(self.radio_btn2)
        hlayout_1.addWidget(self.take_off_btn)
        hlayout_1.addWidget(self.land_btn)
        hlayout_1.addWidget(self.snap_btn)
        # vlayout.addWidget(self.subwidget)

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
        self.slider_dist = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_dist.setRange(25, 500)  # 3
        self.slider_dist.valueChanged.connect(self.on_change_dist)
        self.dist_button = QtWidgets.QPushButton("ok")

        hlayout_3.addWidget(self.dist_label)
        hlayout_3.addWidget(self.slider_dist)
        hlayout_3.addWidget(self.dist_button)
        self.dist_button.clicked.connect(self.confirm_dist)

        self.degree_label = QtWidgets.QLabel("degree: 0°")
        self.slider_degree = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_degree.setRange(0, 360)  # 3
        self.slider_degree.valueChanged.connect(self.on_change_degree)
        self.degree_button = QtWidgets.QPushButton("ok")
        self.degree_button.clicked.connect(self.confirm_degree)

        hlayout_4.addWidget(self.degree_label)
        hlayout_4.addWidget(self.slider_degree)
        hlayout_4.addWidget(self.degree_button)

        vlayout.addLayout(hlayout_3)
        vlayout.addLayout(hlayout_4)
        self.setLayout(vlayout)

    def set_readme(self):
        text = " This Controller map keyboard inputs to Tello control commands." \
               " Adjust the trackbar to reset distance and degree parameter\n"\
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
            self.dist_label.setText("distance:" + str(float(self.slider_dist.value()) / 100) + "m")
        except Exception as e:
            print(e)

    def on_change_degree(self):
        try:
            self.degree_label.setText("degree:" + str(self.slider_degree.value()) + "°")
        except Exception as e:
            print(e)

    def confirm_degree(self):
        self.degree = self.slider_degree.value()

    def confirm_dist(self):
        self.distance = float(self.slider_dist.value()) / 100
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

    def btnstate(self, btn):
        if btn.text() == "start":
            # self.stop_event.clear()
            self.tello_obj.video_freeze(False)
            # text ="[Info] stream on\n"
            # self.logger_text += text
            # self.text_widget.setText(self.logger_text)
        elif btn.text() == "stop":
            self.tello_obj.video_freeze(True)

            # text = "[Info] stream off\n"
            # self.logger_text += text
            # self.text_widget.setText(self.logger_text)

    def snap_shot(self):
        try:
            ts = datetime.datetime.now()
            filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
            p = os.path.sep.join((self.output_path, filename))
            cv2.imwrite(p, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
            # self.text_widget.setText("[Info] saved {} \n ".format(filename))
            print("[INFO] saved {}".format(filename))
        except Exception as e:
            print e

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
                # if not self.stop_event.is_set():
                img = QtGui.QImage(self.frame,
                                   self.frame.shape[1],
                                   self.frame.shape[0],
                                   QtGui.QImage.Format_RGB888)
                self.label_show.setPixmap(QtGui.QPixmap.fromImage(img))
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


class ChildWindow(QtWidgets.QWidget):
    def __init__(self):
        a = 1

