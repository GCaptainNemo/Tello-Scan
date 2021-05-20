# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # author： 11360
# # datetime： 2021/5/20 0:12
# import os, sys
# sys.path.append(os.getcwd())
# import cv2
# import av
# import socket
#
#
# tello_ip = '192.168.10.1'
# tello_port = 8889
# dir = 'udp://{}:{}'.format(tello_ip, tello_port)
# print("dir = ", dir)
# tello_address = (tello_ip, tello_port)
# socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
#
# socket.sendto(b'command', tello_address)
# print ('sent: command')
# socket.sendto(b'streamon', tello_address)
# print ('sent: streamon')
#
# video = av.open(dir, 'r')
# index = 0
# try:
#     for frame in video.decode():
#         img = frame.to_nd_array(format='bgr24')
#         cv2.imshow("Test", img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
# except Exception as e:
#     print('fate erro:{}'.format(e))
#
# cv2.destroyAllWindows()

import threading


def video_loop():
    while True:
        print(1)


thread_get_video = threading.Thread(target=video_loop)
thread_get_video.start()


