#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/26 19:16
# @Author  : hedengfeng
# @Site    : 
# @File    : can_tranfer_test.py
# @Software: terminal
# @description: 

import serial
import sys
import time


class CanTransferTest(object):
    def __init__(self):
        self.baud = 9600
        self.serial_dev = serial.Serial('/dev/ttyAMA0',  self.baud, timeout=0.5)

    def run(self):
        while True:
            # 0x00, 0x00, 0x00, 0x07, 0xFF, 0x08,
            data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
            send_data = bytes(data)
            print('send data:', send_data)
            self.serial_dev.write(send_data)
            time.sleep(0.01)
            r_return = self.serial_dev.readline()
            print('can model return:', r_return)

            time.sleep(1)


if __name__ == '__main__':
    test = CanTransferTest()
    test.run()