#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/10/15 10:12
# @Author  : hedengfeng
# @Site    : 
# @File    : eai_public_pusle_count.py
# @Software: EAI_test
# @description:

import serial
import zmq
import sys
import time


class EaiPublic(object):
    def __init__(self, left_wheel, right_wheel, wheel_count):
        """"""
        self.serial = None
        self.pub_socket = None

        self.left_wheel = left_wheel
        self.right_wheel = right_wheel
        self.wheel_count = int(wheel_count)

        self.init_eai_serial()
        self.init_zmq_network()

    def init_eai_serial(self):
        self.serial = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        time.sleep(1)

    def init_zmq_network(self):
        ctx = zmq.Context()

        self.pub_socket = ctx.socket(zmq.PUB)
        self.pub_socket.bind('tcp://*:6105')

    def public_pusle_count(self, pusle_count):
        public_topic = "eai"
        self.pub_socket.send_multipart([public_topic.encode(), pusle_count.encode()])

    def read_pusle_count(self):
        self.serial.write('e\r'.encode())
        e_return = self.serial.readline().decode()

        pulse_count_list = e_return.split()
        # print(pulse_count_list)

        if pulse_count_list[0]=='0' and pulse_count_list[1]=='0':
            return
        self.public_pusle_count('{},{},{}'.format(pulse_count_list[0], pulse_count_list[1], time.time()))

    def drive_robot(self, left_value, right_value):
        cmd = 'z {} {};\r'.format(left_value, right_value)
        self.serial.write(cmd.encode())

    def start(self):
        drive_count = 0
        try:
            while True:
                self.read_pusle_count()

                if self.left_wheel is not None and self.right_wheel is not None:
                    self.drive_robot(self.left_wheel, self.right_wheel)
                    drive_count += 1
                    # print(drive_count, self.wheel_count, type(drive_count), type(wheel_count))
                    if drive_count == self.wheel_count:
                        print("Done.")
                        break

                time.sleep(0.02)
        except KeyboardInterrupt:
            pass
        print("Done.")


if __name__ == "__main__":
    """"""
    left_wheel = None
    right_wheel = None
    wheel_count = None
    if len(sys.argv) == 4:
        left_wheel = sys.argv[1]
        right_wheel = sys.argv[2]
        wheel_count = sys.argv[3]

    eai_public = EaiPublic(left_wheel, right_wheel, wheel_count)
    eai_public.start()

