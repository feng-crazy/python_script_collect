#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/22 15:54
# @Author  : hedengfeng
# @Site    : 
# @File    : revert_serial_baud.py
# @Software: terminal
# @description:

import serial
import sys
import time


class RevertCanConfig(object):
    def __init__(self, src_baud='115200', dest_baud='19200'):
        self.src_baud = int(src_baud)
        self.dest_baud = int(dest_baud)
        self.serial_dev = serial.Serial('/dev/ttyAMA0',  self.src_baud, timeout=0.5)

    def run(self):
        try:
            data = 'AT+CG\r\n'
            send_data = data.encode()
            print('send data:', send_data)
            self.serial_dev.write(send_data)
            r_return = self.serial_dev.readline()
            print('recv:', r_return.decode())

            data = 'AT+USART_PARAM={},0,1,0\r\n'.format(self.dest_baud)
            send_data = data.encode()
            print('send data:', send_data)
            self.serial_dev.write(send_data)
            r_return = self.serial_dev.readline()
            print('recv:', r_return.decode())

            if self.src_baud != self.dest_baud:
                self.serial_dev.close()
                self.serial_dev = serial.Serial('/dev/ttyAMA0', self.dest_baud, timeout=0.5)

                data = 'AT+CG\r\n'
                send_data = data.encode()
                print('send data:', send_data)
                self.serial_dev.write(send_data)
                r_return = self.serial_dev.readline()
                print('recv:', r_return.decode())

            data = 'AT+USART_PARAM=?\r\n'
            send_data = data.encode()
            print('send data:', send_data)
            self.serial_dev.write(send_data)
            r_return = self.serial_dev.readline()
            print('recv:', r_return.decode())

            data = 'AT+ET\r\n'
            send_data = data.encode()
            print('send data:', send_data)
            self.serial_dev.write(send_data)
            r_return = self.serial_dev.readline()
            print('recv:', r_return.decode())

        except Exception as e:
            print('Exception:', e)


if __name__ == '__main__':
    test = None
    if len(sys.argv) < 3:
        test = RevertCanConfig()
    else:
        test = RevertCanConfig(sys.argv[1], sys.argv[2])
    test.run()