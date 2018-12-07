#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/10/10 10:10
# @Author  : hedengfeng
# @Site    : 
# @File    : serial_test.py
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

# ser.write('b\r'.encode())
# time.sleep(1)
# b_return = ser.readline().decode()
# print('b_return:', b_return)

# ser.write('e\r'.encode())
# time.sleep(1)
# e_return = ser.readline().decode()
# print('e_return:', e_return)

# ser.write('p\r'.encode())
# time.sleep(1)
# p_return = ser.readline().decode()
# print('p_return:', p_return)


print('begin:', time.asctime())

# ser.write('r\r'.encode())
# r_return = ser.readline().decode()
# print('r_return:', r_return, time.asctime())

ser.write('z 30 -30;\r'.encode())
z_return = ser.readline().decode()
print('z_return:', z_return, time.asctime())

exit(0)

ser.write('e\r'.encode())
e_return = ser.readline().decode()
print('e_return:', e_return, time.asctime())

ser.write('z 30 -30;\r'.encode())
z_return = ser.readline().decode()
print('z_return:', z_return, time.asctime())

time.sleep(1.6)

ser.write('e\r'.encode())
e_return = ser.readline().decode()
print('e_return:', e_return, time.asctime())

ser.write('z 50 -50;\r'.encode())
z_return = ser.readline().decode()
print('z_return:', z_return, time.asctime())

time.sleep(1.6)

ser.write('e\r'.encode())
e_return = ser.readline().decode()
print('e_return:', e_return, time.asctime())

time.sleep(1.6)

ser.write('r\r'.encode())
r_return = ser.readline().decode()
print('r_return:', r_return, time.asctime())

ser.write('e\r'.encode())
e_return = ser.readline().decode()
print('e_return:', e_return, time.asctime())