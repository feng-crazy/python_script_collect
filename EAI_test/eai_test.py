#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/10/10 14:34
# @Author  : hedengfeng
# @Site    : 
# @File    : eai_test.py
# @Software: EAI_test
# @description:
import sys
import time
import scanf
import serial
import zmq
import math

# from eai_public_pusle_count import EaiPublic

eai_robot_arg = {'wheel_diameter': 0.124,  # 0.1280,  # 轮子直径，单位：米
                 'wheel_track': 0.3559,  # 两轮子的间距，单位: 米
                 'encoder_resolution': 1200,  # 编码器分辨率，轮子转一圈，编码器产生的脉冲数
                 'pid_rate': 30  # PID 调节PWM值的频率
                 }

PI = 3.1415926
TAU = PI * 2
drive_num = 1
wheel_perimeter = eai_robot_arg['wheel_diameter'] * PI  # 轮子的周长，转一圈的长度
meter_rosolution = eai_robot_arg['encoder_resolution'] / wheel_perimeter  # 移动一米的脉冲数  脉冲数除以它，等于移动的距离


class eai_test(object):
    def __init__(self, left_value, right_value, drive_num):
        self.left_value = left_value
        self.right_value = right_value
        self.drive_num = drive_num
        self.serial = None
        self.recv_socket = None
        self.pub_socket = None

        self.optic_start_x = 0
        self.optic_start_y = 0
        self.optic_start_angle = 0

        self.optic_end_x = 0
        self.optic_end_y = 0
        self.optic_end_angle = 0

        self.odom_x = 0
        self.odom_y = 0
        self.odom_angle = 0

        self.init_eai_serial()

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
        self.reset_eai_encode()

    def reset_eai_encode(self):
        self.serial.write('r\r'.encode())
        r_return = self.serial.readline().decode()
        print('eai reset:', r_return)

    def init_zmq_network(self):
        ctx = zmq.Context()
        self.recv_socket = ctx.socket(zmq.SUB)

        self.recv_socket.setsockopt_string(zmq.SUBSCRIBE, 'Loc robot filtered')
        recv_connect_cmd = 'tcp://localhost:6102'
        print('create_zmq_connect:' + recv_connect_cmd)
        self.recv_socket.connect(recv_connect_cmd)

        self.pub_socket = ctx.socket(zmq.PUB)
        self.pub_socket.bind('tcp://*:6105')

    def recv_optic_loc(self):
        x = None
        y = None
        radian = None
        while self.recv_socket.poll(20):  # 20毫秒不能太高，因为位置频率很高，会陷入死循环，一直为true
            try:
                topic, msg = self.recv_socket.recv_multipart()
                if msg is not None:
                    x, y, z, radian, gamma, theta, ts, bs_index, sensor_id \
                        = scanf.scanf("%f %f %f %f %f %f %f %d %d", msg.decode())
            except zmq.error.Again as err:
                print('Exception:%s', err)

        if x is not None and y is not None:
            x = x / 100.00
            y = y / 100.00

        return x, y, radian

    def drive_robot(self, left_value, right_value):
        cmd = 'z {} {};\r'.format(left_value, right_value)
        self.serial.write(cmd.encode())

        # z_return = self.serial.readline().decode()
        # print('z_return:', z_return)

    def public_pusle_count(self, pusle_count):
        public_topic = "eai"
        self.pub_socket.send_multipart([public_topic.encode(), pusle_count.encode()])

    def read_wheel_distance(self):
        self.serial.write('e\r'.encode())
        e_return = self.serial.readline().decode()

        pulse_count_list = e_return.split()
        # print(pulse_count_list)

        self.public_pusle_count('{},{},{}'.format(pulse_count_list[0], pulse_count_list[1], time.time()))

        left_wheel_distance = int(pulse_count_list[0]) / meter_rosolution
        right_wheel_distance = int(pulse_count_list[1]) / meter_rosolution

        print('wheel_distance: %.3f, %.3f' % (left_wheel_distance, right_wheel_distance))
        return left_wheel_distance, right_wheel_distance

    def get_odom_loc(self):
        s_left, s_right = self.read_wheel_distance()
        b = eai_robot_arg['wheel_track']
        self.odom_x = self.optic_start_x + (
                    (s_right + s_left) / 2 * math.cos(self.optic_start_angle + (s_right - s_left) / (2 * b)))
        self.odom_y = self.optic_start_y + (
                    (s_right + s_left) / 2 * math.sin(self.optic_start_angle + (s_right - s_left) / (2 * b)))
        self.odom_angle = self.optic_start_angle + (s_right - s_left) / b
        while self.odom_angle < 0:
            self.odom_angle += TAU
        while self.odom_angle > TAU:
            self.odom_angle -= TAU

    def get_moving_distance(self, x1, y1, x2, y2):
        s = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
        return s

    def robot_run(self):
        self.init_zmq_network()
        time.sleep(0.5)
        self.optic_start_x, self.optic_start_y, self.optic_start_angle = self.recv_optic_loc()
        if self.optic_start_x is None and self.optic_start_y is None:
            return

        print('optic_start_x: %.3f, optic_start_y: %.3f, optic_start_angle: %.3f' % (
        self.optic_start_x, self.optic_start_y, self.optic_start_angle))

        for i in range(0, int(self.drive_num)):
            self.drive_robot(self.left_value, self.right_value)
            time.sleep(1)

        time.sleep(2)
        self.optic_end_x, self.optic_end_y, self.optic_end_angle = self.recv_optic_loc()
        print('optic_end_x: %.3f, optic_end_y: %.3f, optic_end_angle: %.3f' % (
        self.optic_end_x, self.optic_end_y, self.optic_end_angle))
        if self.optic_end_x is None and self.optic_end_y is None:
            return

        print('-' * 40)

        self.get_odom_loc()
        print('odom_x: %.3f, odom_y: %.3f, odom_angle: %.3f' % (self.odom_x, self.odom_y, self.odom_angle))
        print('-' * 40)

        print(
            'Optic distance: %.3f' % self.get_moving_distance(self.optic_start_x, self.optic_start_y, self.optic_end_x,
                                                              self.optic_end_y))
        print('Odometry distance: %.3f' % self.get_moving_distance(self.optic_start_x, self.optic_start_y, self.odom_x,
                                                                   self.odom_y))

        # print('lt_eai_diff_x:', self.optic_end_x - self.odom_x, 'optic_end_y-lt_eai_diff_y:', self.optic_end_y -
        # self.odom_y, 'lt_eai_diff_angle:', self.optic_end_angle-self.odom_angle)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("argv error")
    else:
        argv_list = sys.argv[1:]
        left_value = argv_list[0]
        right_value = argv_list[1]
        if len(sys.argv) == 4:
            drive_num = argv_list[2]

        test = eai_test(left_value, right_value, drive_num)
        test.robot_run()
