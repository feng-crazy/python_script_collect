#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/4 15:36
# @Author  : hedengfeng
# @Site    : 
# @File    : directional_move_test.py
# @Software: EAI_test
# @description:
import sys
import time
import scanf
import serial
import zmq
import math
import threading
import signal

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

once_run_time = 2  # 已知驱动一个电机的持续时间2s


class DirectionalMove(object):
    def __init__(self, x, y, angle):
        """........."""
        self.end_mark = False
        self.serial = None
        self.recv_socket = None
        self.pub_socket = None

        self.target_x = float(x)
        self.target_y = float(y)
        self.target_radian = 0
        self.init_radian = self.angle_to_radian(float(angle))

        self.optic_x = 0
        self.optic_y = 0
        self.optic_start_radian = 0

        self.odom_x = 0
        self.odom_y = 0
        self.odom_angle = 0

        # 必须创建线程接收，不然位置会受网络缓存影响
        self.thread = threading.Thread(target=self.zmq_thread_run, args=(), name="zmq network thread")
        self.thread.start()

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

    def zmq_thread_run(self):
        self.init_zmq_network()
        while True:
            x, y, radian = self.recv_optic_loc()
            # print('recv_optic_loc:', x, y, radian)
            if x is not None:
                self.optic_x = x
            if y is not None:
                self.optic_y = y
            if radian is not None:
                self.optic_start_radian = radian

            if self.end_mark is True:
                break

    def init_zmq_network(self):
        ctx = zmq.Context()
        self.recv_socket = ctx.socket(zmq.SUB)

        self.recv_socket.setsockopt_string(zmq.SUBSCRIBE, 'Loc robot filtered')
        recv_connect_cmd = 'tcp://localhost:6102'
        print('create_zmq_connect:' + recv_connect_cmd)
        self.recv_socket.connect(recv_connect_cmd)

        self.pub_socket = ctx.socket(zmq.PUB)
        self.pub_socket.bind('tcp://*:6105')
        time.sleep(0.5)

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

        # if x is not None and y is not None:
            # x = x / 100.00
            # y = y / 100.00

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
        self.odom_x = self.optic_x + (
                    (s_right + s_left) / 2 * math.cos(self.optic_start_radian + (s_right - s_left) / (2 * b)))
        self.odom_y = self.optic_y + (
                    (s_right + s_left) / 2 * math.sin(self.optic_start_radian + (s_right - s_left) / (2 * b)))
        self.odom_angle = self.optic_start_radian + (s_right - s_left) / b
        while self.odom_angle < 0:
            self.odom_angle += TAU
        while self.odom_angle > TAU:
            self.odom_angle -= TAU

    @staticmethod
    def angle_to_radian(angle):
        return (PI/180.00)*angle

    @staticmethod
    def calc_points_radian(x1, y1, x2, y2):
        radian = math.atan2((y2 - y1), (x2 - x1))
        if radian < 0.0:
            radian = PI - radian
        # print('radian:', radian)
        return radian

    @staticmethod
    def calc_distance(x1, y1, x2, y2):
        s = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
        return s

    def calc_radian_pulse_count(self):
        v_radian = (self.target_radian - self.init_radian) / 2  # 弧度/秒
        v_left = v_radian * eai_robot_arg['wheel_track'] / 2.0
        v_right = -1 * v_radian * eai_robot_arg['wheel_track'] / 2.0
        left_pulse = int(v_left * meter_rosolution / eai_robot_arg['pid_rate'])
        right_pulse = int(v_right * meter_rosolution / eai_robot_arg['pid_rate'])
        return left_pulse, right_pulse

    @staticmethod
    def calc_move_pulse_count(distance):
        v_move = (distance/100) / 2  # 2秒后到达，计算速度 米/秒
        pulse_count = int(v_move * meter_rosolution / eai_robot_arg['pid_rate'])
        return pulse_count

    def start_move(self):
        """....."""
        while True:  # 循环进行 直到到达目标点附近
            # 计算距离，单位厘米
            distance = self.calc_distance(self.optic_y, self.optic_y, self.target_x, self.target_y)
            print('init distance:', distance)
            while distance > 5:
                """"""
                print('self.optic_y:', self.optic_y, 'self.optic_y:', self.optic_y)
                # 计算初始点 到 目标点的 弧度
                self.target_radian = self.calc_points_radian(self.optic_y, self.optic_y, self.target_x, self.target_y)
                print('calc_points_radian:', self.init_radian, self.target_radian)
                # 计算初始弧度 到 目标弧度 原地转向 左右轮应该发送的脉冲
                left_pulse, right_pulse = self.calc_radian_pulse_count()
                print('left_pulse:', left_pulse, 'right_pulse:', right_pulse)
                # 驱动机器人原地转向到目标弧度方向
                self.drive_robot(left_pulse, right_pulse)
                # 计算直线到目标点移动距离 左右轮应该发送的脉冲
                distance = distance / 2  # 每次移动一半，逐步靠近
                if distance > 50:  # 限定一次最大移动距离，从而限定速度
                    distance = 50
                move_pulse = self.calc_move_pulse_count(distance)
                print('move_pulse:', move_pulse, 'distance:', distance)
                # 驱动机器人直线移动到目标点
                self.drive_robot(move_pulse, move_pulse)

                time.sleep(1.8)
                self.init_radian = self.optic_start_radian
                # 计算到目标点的距离
                distance = self.calc_distance(self.optic_y, self.optic_y, self.target_x, self.target_y)
                print('calc_distance:', self.optic_y, self.optic_y, self.target_x, self.target_y, distance)

                if self.end_mark is True:
                    break

            print('到达目标点')
            # 命令行读取新的目标点位置
            input_data = input('please target location:')
            if input_data == 'q':
                self.end_mark = True
            else:
                location = input_data.split(',')
                self.target_x = float(location[0])
                self.target_y = float(location[1])

            if self.end_mark is True:
                break

    def signal_handler(self, signum, frame):
        print('Received signal: ', signum)
        self.end_mark = True

    def register_signal(self):
        signal.signal(signal.SIGHUP, self.signal_handler)  # 1
        signal.signal(signal.SIGINT, self.signal_handler)  # 2
        signal.signal(signal.SIGQUIT, self.signal_handler)  # 3
        signal.signal(signal.SIGABRT, self.signal_handler)  # 6
        signal.signal(signal.SIGTERM, self.signal_handler)  # 15
        signal.signal(signal.SIGSEGV, self.signal_handler)  # 11


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please enter three parameters, the position of the target point (in centimeters),"
              " and the Angle (in degrees).")
    else:
        argv_list = sys.argv[1:]
        target_x = argv_list[0]
        target_y = argv_list[1]
        start_angle = argv_list[2]

        test = DirectionalMove(target_x, target_y, start_angle)
        test.start_move()

