#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/8/2 14:09
# @Author  : hedengfeng
# @Site    : 
# @File    : term)simulator.py
# @Software: terminal
# @description:
import random
import select
import threading
import time
import traceback
from socket import *

import zmq

from utility import message_pb2
from utility.NetWorkInfo import NetWorkInfo

CONTEXT = zmq.Context()


class TerminalSimulator(object):
    def genegate_ip(self):
        ip_addr_list = []
        for i in range(0, 4):
            ip_addr_list.append(random.randint(0, 255))
        return '{}.{}.{}.{}'.format(ip_addr_list[0], ip_addr_list[1], ip_addr_list[2], ip_addr_list[3])

    def genegate_mac(self):
        mac_addr_list = []
        for i in range(0, 6):
            mac_addr_list.append(random.randint(0, 255))
        return '{:x}-{:x}-{:x}-{:x}-{:x}-{:x}'.format(mac_addr_list[0], mac_addr_list[1], mac_addr_list[2],
                                                      mac_addr_list[3], mac_addr_list[4], mac_addr_list[5])

    def __init__(self):
        self.global_local_ip_addr = self.genegate_ip()
        self.global_local_mac_addr = self.genegate_mac()
        self.global_local_hostname = 'test terminal'


class TermBroadCast(object):
    """
    terminal BroadCast Response
    接收udp广播包，响应广播，与控制器建立连接
    """
    HOST = ''
    PORT = NetWorkInfo.UDP_BROADCAST_PORT
    BUFSIZE = 4068
    ADDR = (HOST, PORT)

    def __init__(self, terminal):
        self.terminal = terminal
        self.rep_cast_ip_addr = None

        self.controller_rep_port = None
        self.loc_xsub_port = None
        self.controller_ip_addr = None

        self.find_ctrller_flag = False

        self.thread = threading.Thread(target=self.thread_task, args=())
        self.thread.start()

    def thread_task(self):
        """
        线程主循环函数
        """
        self.setup_thread()
        while True:
            # 循环接收控制器广播包
            readable, writeable, exceptional = select.select([self._udp_sock], [self._udp_sock], [self._udp_sock],
                                                             self.__sock_timeout)
            for self._udp_sock in readable:
                self._recv_broadcast()
            time.sleep(0.5)

    def setup_thread(self):
        """
        子线程初始操作函数
        """
        print('setup_thread...........', threading.current_thread())
        self._init_udp_socket()

    def _init_udp_socket(self):
        self.context = CONTEXT

        self._udp_sock = socket(AF_INET, SOCK_DGRAM)
        self._udp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._udp_sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, 3)
        self._udp_sock.bind(self.ADDR)

        self.__sock_timeout = 10

    def _recv_broadcast(self):
        """接收解析广播包"""
        try:
            data, addr = self._udp_sock.recvfrom(self.BUFSIZE)
            # print('_recv_broadcast:', data, addr)
            self.rep_cast_ip_addr = addr
            msg = message_pb2.ControllerBroadcast()
            msg.ParseFromString(data)
            # print('recv msg', msg)
            self.controller_ip_addr = msg.ip_addr
            self.controller_rep_port = msg.terminal_port
            self.loc_xsub_port = msg.loc_xsub_port

            self._response_cast()
        except Exception as e:
            self.find_ctrller_flag = False
            print('_recv_broadcast:', str(e))
            print(traceback.format_exc())

    def _response_cast(self):
        """给控制器响应广播包"""
        msg = message_pb2.BroadcastResponse()
        msg.type = message_pb2.BroadcastResponse.TERMINAL_TYPE
        msg.ip_addr = self.terminal.global_local_ip_addr
        msg.mac_addr = self.terminal.global_local_mac_addr
        msg.host_name = self.terminal.global_local_hostname
        # print('_response_cast: ', msg)
        msg_str = msg.SerializeToString()
        try:
            ret = self._udp_sock.sendto(msg_str, self.rep_cast_ip_addr)
            # print('self._udp_sock.sendto ret:', ret)
            self.find_ctrller_flag = True
        except Exception as e:
            self.find_ctrller_flag = False
            print('_response_cast:%s' % str(e))
            print(traceback.format_exc())


class TermDataHandle(object):
    """
    TermDataHandle 终端接收controller数据处理类
    """

    def __init__(self, terminal, broad_cast):
        self.config_file_name = 'config.txt'
        self.config_file_update = ''
        self.terminal = terminal
        self.broad_cast = broad_cast

        self.context = CONTEXT
        self._socket_req = None
        self._req_socket_addr_port = None

        self.ctrller_connect_flag = False

        self.sequence = 0  # 发送心跳包的序列号
        self.config_error_string = ''
        self.sensor_config_change = ''

        self.thread = threading.Thread(target=self.thread_task, args=())
        self.thread.start()

    def thread_task(self):
        """
        线程主循环函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        self.setup_thread()
        while True:
            ctrller_find_status = self.broad_cast.find_ctrller_flag
            if ctrller_find_status is True and self.ctrller_connect_flag is False:
                self._req_socket_addr_port = 'tcp://' + self.broad_cast.controller_ip_addr + ':' + str(self.broad_cast.controller_rep_port)
                self.connect_controller()
            elif ctrller_find_status is False and self.ctrller_connect_flag is True:
                self.disconnect_controller()

            # 接收心跳包响应
            if self.ctrller_connect_flag is True:
                if self._socket_req.poll(50, zmq.POLLOUT):
                    self.send_heartbeat_request()
                    self.recv_response()

            time.sleep(1)

    def send_heartbeat_request(self):
        """对于终端来说，目前只有心跳请求"""

        req_msg = message_pb2.TerminalHeartbeatRequest()
        req_msg.sequence = self.sequence  # self.sequence
        self.sequence += 1
        req_msg.ok_status = True

        req_data = req_msg.SerializeToString()
        # print('send_heartbeat_request: ', req_msg)
        self._socket_req.send_multipart([self.terminal.global_local_mac_addr.encode(), b'TerminalHeartbeatRequest', req_data])
        # print('send_heartbeat_request send end')

    def recv_response(self):
        """
        接收响应
        """
        try:
            msg = self._socket_req.recv_multipart()
        except zmq.error.Again as err:
            print('recv_response Exception: ', err)
            print(traceback.format_exc())
            self.reconnect_controller()
            return
        # 处理msg
        self.handle_heartbeat_msg_rep(msg)

    def handle_heartbeat_msg_rep(self, msg):
        """
        处理终端控制器上返回的响应
        """
        if msg[0].decode() != 'TerminalHeartbeatResponse':
            return False

        rep_msg = message_pb2.TerminalHeartbeatResponse()
        rep_msg.ParseFromString(msg[1])
        # print('handle_heartbeat_msg_rep rep_msg: ', rep_msg)

    def setup_thread(self):
        """
        子线程初始操作函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        print('setup_thread...........', threading.current_thread())

    def connect_controller(self):
        """连接控制器，包req端口"""
        if self.ctrller_connect_flag is False:
            print('TermDataHandle connect_controller')
            self._socket_req = self.context.socket(zmq.REQ)
            self._socket_req.setsockopt(zmq.LINGER, 0)
            self._socket_req.setsockopt(zmq.REQ_CORRELATE, 1)
            self._socket_req.setsockopt(zmq.REQ_RELAXED, 1)
            self._socket_req.setsockopt(zmq.RCVTIMEO, 5000)
            self._socket_req.connect(self._req_socket_addr_port)
            self.ctrller_connect_flag = True

            self.sequence = 0
            time.sleep(0.5)

    def disconnect_controller(self):
        """
        断开与控制器的连接，req端口
        """
        if self.ctrller_connect_flag is True:
            print('TermDataHandle disconnect_controller')
            self._socket_req.disconnect(self._req_socket_addr_port)
            self._socket_req.close(linger=0)
            self.ctrller_connect_flag = False
            self.sequence = 0

    def reconnect_controller(self):
        print('TermDataHandle reconnect_controller')
        self.disconnect_controller()
        self.connect_controller()
            
            
if __name__ == '__main__':
    """"""
    terminal_list = []
    for i in range(0, 50):
        terminal = TerminalSimulator()
        term_broad_cast = TermBroadCast(terminal)
        term_data_handle = TermDataHandle(terminal, term_broad_cast)
        terminal_list.append(terminal)

    while True:
        pass