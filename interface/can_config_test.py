#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/26 18:04
# @Author  : hedengfeng
# @Site    : 
# @File    : can_config_test.py
# @Software: terminal
# @description: 

import serial
import sys
import time


class CanConfigTest(object):
    def __init__(self, baud):
        self.baud = int(baud)
        self.serial_dev = serial.Serial('/dev/ttyAMA0',  self.baud, timeout=0.5)

    def run(self):
        while True:
            data = input('please input cmd:')
            if data == 'q':
                break
            data += '\r\n'
            try:
                send_data = data.encode()
                print('send data:', send_data)
                self.serial_dev.write(send_data)

                r_return = self.serial_dev.readline()
                print('can model return:', r_return)

                # if '115200' in data:
                #     self.serial_dev.close()
                #     self.baud = 115200
                #     self.serial_dev = serial.Serial('/dev/ttyAMA0', self.baud, timeout=0.5)
                #     print('change baud is:', self.baud)
                # elif '9600' in data:
                #     self.serial_dev.close()
                #     self.baud = 9600
                #     self.serial_dev = serial.Serial('/dev/ttyAMA0', self.baud, timeout=0.5)
                #     print('change baud is:', self.baud)

            except Exception as e:
                print('Exception:', e)
                # self.serial_dev.close()
                # if self.baud == 9600:
                #     self.baud = 115200
                #     self.serial_dev = serial.Serial('/dev/ttyAMA0', self.baud, timeout=0.5)
                # else:
                #     self.baud= 9600
                #     self.serial_dev = serial.Serial('/dev/ttyAMA0', self.baud, timeout=0.5)
                # print('current baud is :', self.baud)


if __name__ == '__main__':
    test = CanConfigTest(sys.argv[1])
    test.run()