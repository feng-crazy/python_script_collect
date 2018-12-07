#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/5 15:49
# @Author  : hedengfeng
# @Site    : 
# @File    : aei_time_test.py
# @Software: EAI_test
# @description: 
import time
import serial


ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

time.sleep(1)

ser.write('e\r'.encode())
e_return = ser.readline().decode()
print('begin:',  e_return, time.asctime(), time.time())

ser.write('z 30 -30;\r'.encode())
z_return = ser.readline().decode()
print('z_return:', z_return, time.asctime(), time.time())

while True:
    ser.write('e\r'.encode())
    e_return = ser.readline().decode()
    print('e_return:', e_return, time.asctime(), time.time())