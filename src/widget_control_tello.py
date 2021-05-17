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
        self.thread_get_video = threading.Thread(target=self.videoLoop, args=())
        self.thread_get_video.start()
        self.thread_send_command = threading.Thread(target=self._sendingCommand)
        self.thread_send_command.start()
        self.output_path = "./image"
        self.logger_text = ""
        self.set_ui()
        self.setWindow

    def set_ui(self):
        vlayout = QtWidgets.QVBoxLayout(self)
        # self.vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.label = QtWidgets.QLabel("")
        self.label.setScaledContents(True)
        # self.vsplitter.addWidget(self.label)

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
        # self.text_widget = QtWidgets.QTextEdit()
        hlayout.addWidget(self.radio_btn1)
        hlayout.addWidget(self.radio_btn2)
        hlayout.addWidget(self.snap_btn)
        vlayout.addWidget(self.subwidget)
        # self.sub_vlayout.addLayout(hlayout)
        # self.vsplitter.addWidget(self.subwidget)
        # vlayout.addWidget(self.vsplitter)

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

    def _sendingCommand(self):
        """
        start a while loop that sends 'command' to tello every 5 second
        """
        while True:
            self.tello_obj.send_command('command')
            time.sleep(5)

    def videoLoop(self):
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




