#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

import socket,sys
from socket import *
import time, threading
import sys
import signal

HOST = ''
PORT = 1500
BUFSIZE = 1024

ADDR = (HOST, PORT)
dest = ('<broadcast>', PORT)

udpCliSock = socket(AF_INET, SOCK_DGRAM)
udpCliSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)

over_flag = False
scan = 'scan'


try:
	while True:
		data = input('>')
		if data == scan:
			udpCliSock.sendto(data.encode(),dest)
# 	while True:
# 		data,ADDR = udpCliSock.recvfrom(BUFSIZE)
# 		if not data:
# 			break
# 		print('scan get data: ', data.decode())
# 		print('scan get addr: ', ADDR)
		
except Exception as e:
	print (str(e))

udpCliSock.close()
