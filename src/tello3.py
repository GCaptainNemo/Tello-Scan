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

host = ''
port = 9000
locaddr = (host, port)


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
    count = 0
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print('\nExit . . .\n')
            break


def _receive_video_func():
    """
    Listens for video streaming (raw h264) from the Tello.

    Runs as a thread, sets self.frame to the most recent frame Tello captured.

    """
    packet_data = ""
    while 1:
        print("in receive videos")
        try:
            # res_string, ip = self.socket_video.recvfrom(2048)
            res_string, ip = sock.recvfrom(1024)

        except Exception as e:
            print(e)
        print("ip = ", ip)
        print(type(res_string))
        packet_data += str(res_string)
        # end of frame
        # if len(res_string) != 1460:
        #     for frame in _h264_decode(packet_data):
        #     # for frame in self.video_udp.decode():
        #         self.frame = frame
        #         # print("frame = ", self.frame)
        #     packet_data = ""


print('\r\n\r\nTello Python3 Demo.\r\n')

print('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')

print('end -- quit demo.\r\n')


#recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()

receive_video_thread = threading.Thread(target=
                                             _receive_video_func)
receive_video_thread.daemon = True
receive_video_thread.start()


while True:
    try:
        python_version = str(platform.python_version())
        version_init_num = int(python_version.partition('.')[0])
       # print (version_init_num)
        if version_init_num == 3:
            msg = input("command:");
        elif version_init_num == 2:
            # msg = raw_input("");
            msg = input("");

        if not msg:
            break

        if 'end' in msg:
            print('...')
            sock.close()
            break

        # Send data
        msg = msg.encode(encoding="utf-8")
        sent = sock.sendto(msg, tello_address)
    except KeyboardInterrupt:
        print('\n . . .\n')
        sock.close()
        break




