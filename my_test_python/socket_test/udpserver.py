#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

from socket import *
from time import ctime

HOST = ''
PORT = 5500
BUFSIZE = 1024

ADDR = (HOST,PORT)

udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
udpSerSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
udpSerSock.bind(ADDR)

while True:
	print 'wating for message...'
	data, addr = udpSerSock.recvfrom(BUFSIZE)
	udpSerSock.sendto('[%s] %s'%(ctime(),data),addr)
	print '...received from and retuned to:',addr

udpSerSock.close()
