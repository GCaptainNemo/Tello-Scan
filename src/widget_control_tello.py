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
        self.distance = 0.1  # default distance for 'move' cmd
        self.degree = 30  # default degree for 'cw' or 'ccw' cmd
        # if the flag is TRUE,the auto-takeoff thread will stop waiting for the response from tello
        self.quit_waiting_flag = False
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
        self.label = QtWidgets.QLabel("")
        self.label.setScaledContents(True)
        self.subwidget = QtWidgets.QWidget()
        hlayout = QtWidgets.QHBoxLayout(self.subwidget)
        vlayout.addWidget(self.label)
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


        hlayout.addWidget(self.radio_btn1)
        hlayout.addWidget(self.radio_btn2)
        hlayout.addWidget(self.take_off_btn)
        hlayout.addWidget(self.land_btn)
        hlayout.addWidget(self.snap_btn)

        vlayout.addWidget(self.subwidget)
        self.setLayout(vlayout)

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
                self.label.setPixmap(QtGui.QPixmap.fromImage(img))
                time.sleep(0.05)
        except RuntimeError, e:
            print("[INFO] caught a RuntimeError")

    def tello_take_off(self):
        return self.tello.takeoff()

    def tello_landing(self):
        return self.tello.land()

    def on_keypress_w(self, event):
        print "up %d m" % self.distance
        self.tello_obj.move_up(self.distance)

    def on_keypress_s(self, event):
        print "down %d m" % self.distance
        self.tello_obj.move_down(self.distance)

    def on_keypress_a(self, event):
        print "ccw %d degree" % self.degree
        self.tello_obj.rotate_ccw(self.degree)

    def on_keypress_d(self, event):
        print "cw %d m" % self.degree
        self.tello_obj.rotate_cw(self.degree)

    def on_keypress_up(self, event):
        print "forward %d m" % self.distance
        self.tello_obj.move_forward(self.distance)

    def on_keypress_down(self, event):
        print "backward %d m" % self.distance
        self.tello_obj.move_backward(self.distance)

    def on_keypress_left(self, event):
        print "left %d m" % self.distance
        self.tello_obj.move_left(self.distance)

    def on_keypress_right(self, event):
        print "right %d m" % self.distance
        self.tello_obj.move_right(self.distance)

    def on_keypress_enter(self, event):
        if self.frame is not None:
            self.registerFace()
        self.tmp_f.focus_set()


class TelloOperate:
    def __init__(self, tello_obj):
        self.tello_obj = tello_obj

    def tello_take_off(self):
        return self.tello_obj.takeoff()

    def tello_landing(self):
        return self.tello_obj.land()

    def tello_flip_l(self):
        return self.tello_obj.flip('l')

    def tello_flip_r(self):
        return self.tello_obj.flip('r')

    def tello_flip_f(self):
        return self.tello_obj.flip('f')

    def tello_flip_b(self):
        return self.tello_obj.flip('b')

    def tello_cw(self, degree):
        return self.tello_obj.rotate_cw(degree)

    def tello_ccw(self, degree):
        return self.tello_obj.rotate_ccw(degree)

    def tello_move_forward(self, distance):
        return self.tello_obj.move_forward(distance)

    def tello_move_backward(self, distance):
        return self.tello_obj.move_backward(distance)

    def tello_move_left(self, distance):
        return self.tello_obj.move_left(distance)

    def tello_move_right(self, distance):
        return self.tello_obj.move_right(distance)

    def tello_up(self, dist):
        return self.tello_obj.move_up(dist)

    def tello_down(self, dist):
        return self.tello_obj.move_down(dist)



