#!/usr/bin/env python
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

def run_send_thread():
	while True:
		data = raw_input('>')
		if data == scan:
			udpCliSock.sendto(data,dest)
		elif data == 'exit':
			over_flag = True
			break
		else:
			print('please input scan!')
		time.sleep(1)
			

def run_recv_thread():
	while True:
		data,ADDR = udpCliSock.recvfrom(BUFSIZE)
		if not data:
			break
		print data,ADDR

def quit(signal_num,frame):
	print "you stop the threading"
	udpCliSock.close()
	sys.exit()
	

signal.signal(signal.SIGINT, quit)
signal.signal(signal.SIGTERM, quit)
t1 = threading.Thread(target=run_send_thread,  name='SendThread')
t2 = threading.Thread(target=run_recv_thread,  name='RecvThread')
t1.setDaemon(True)
t2.setDaemon(True)
t1.start()
t2.start()

while True:
	pass
		
print '%s thread end!'%(time.ctime())
udpCliSock.close()
