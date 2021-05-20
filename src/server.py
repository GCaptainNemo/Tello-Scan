#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/5/20 21:06 

import socket

socket_send_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for sending cmd
socket_send_command.bind(("", 1000))

while True:
    socket_send_command.send(1)


