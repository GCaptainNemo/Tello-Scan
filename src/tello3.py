#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/5/20 21:26 
#
# Tello Python3 Control Demo
#
# http://www.ryzerobotics.com/
#
# 1/1/2018

import threading
import socket
import sys
import time
import platform
import cv2




host = ''
port = 9000
locaddr = (host, port)

# video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# video_sock.bind(('', 11111))

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(locaddr)

tello_address = ('192.168.10.1', 8889)


def recv():
    count = 0
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print('\nExit . . .\n')
            break

#
# def _receive_video_func():
#     """
#     Listens for video streaming (raw h264) from the Tello.
#
#     Runs as a thread, sets self.frame to the most recent frame Tello captured.
#
#     """
#     packet_data = ""
#     while 1:
#         print("in receive videos")
#         # try:
#             # res_string, ip = self.socket_video.recvfrom(2048)
#         res_string, ip = video_sock.recvfrom(2048)
#         # except Exception as e:
#         #     print(e)
#         print("ip = ", ip)
#         print(type(res_string))
#         packet_data += str(res_string)
#
#
# print('\r\n\r\nTello Python3 Demo.\r\n')
#
# print('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')
#
# print('end -- quit demo.\r\n')


#recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()
#
# receive_video_thread = threading.Thread(target=
#                                              _receive_video_func)
# receive_video_thread.start()


msg = "command"
msg = msg.encode(encoding="utf-8")
sent = sock.sendto(msg, tello_address)
msg = "streamon"
msg = msg.encode(encoding="utf-8")
sent = sock.sendto(msg, tello_address)

# while True:
#     try:
#         python_version = str(platform.python_version())
#         version_init_num = int(python_version.partition('.')[0])
#        # print (version_init_num)
#         if version_init_num == 3:
#             msg = input("command:");
#         elif version_init_num == 2:
#             # msg = raw_input("");
#             msg = input("");
#
#         if not msg:
#             break
#
#         if 'end' in msg:
#             print('...')
#             sock.close()
#             break
#
#         # Send data
#         msg = msg.encode(encoding="utf-8")
#         sent = sock.sendto(msg, tello_address)
#     except KeyboardInterrupt:
#         print('\n . . .\n')
#         sock.close()
#         break


# telloVideo.set(cv2.CAP_PROP_FPS, 3)

# wait for frame
telloVideo = cv2.VideoCapture("udp://@0.0.0.0:11111")
ret = False
# scale down
scale = 3
while True:
    # Capture frame-by-framestreamon
    print("in")
    ret, frame = telloVideo.read()
    print("ret = ", ret)
    if (ret):
        # Our operations on the frame come here
        height, width, layers = frame.shape
        new_h = int(height / scale)
        new_w = int(width / scale)
        resize = cv2.resize(frame, (new_w, new_h))  # <- resize for improved performance
        # Display the resulting frame
        cv2.imshow('Tello', resize)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
telloVideo.release()
cv2.destroyAllWindows()


