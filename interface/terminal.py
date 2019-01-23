#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/6/25 15:58
# @Author  : hedengfeng
# @Site    :
# @File    : terminal.py
# @Software: LT_controller
import asyncio
import os
import select
import shutil
import signal
import subprocess
# import fcntl
import sys
import threading
import time
import traceback
from socket import *

# import psutil
import scanf
import zmq
from configobj import ConfigObj

from utility import message_pb2
from utility.NetWorkInfo import NetWorkInfo
from utility.Mlogging import MLog
from eventbus.EventBus import EventBus
from eventbus.MThread import MThread
from eventbus.EventTarget import EventTarget
from eventbus.EventClient import EventClient
from utility.LTCommon import LTEventType

global_local_ip_addr = '127.0.0.1'  # 该值并不可靠 所以直接给127.0.0.1
global_local_mac_addr = NetWorkInfo.get_mac_addr('wlan0')  # 默认获取无线网卡mac地址
global_local_hostname = NetWorkInfo.get_host_name()


class TermDeamon(EventTarget):
    """
    TermDeamon
    """

    def __init__(self):
        super(TermDeamon, self).__init__(self)

        self.context = EventBus.CONTEXT

        self.data_hub_process = None
        self.loc_engine_process = None

        self.old_md5sum = None

        self._socket_sub_imu = None
        self._sub_imu_addr_port = 'tcp://localhost:6100'
        self.data_hub_connect_flag = False
        self.term_exit_flag = False

        self.old_sensor_num = -1

        # self.config_file_name = 'config.txt'  #
        # self.config_obj = ConfigObj(self.config_file_name, encoding='UTF8')

        self._init_lt_process()

        self.subscribe(LTEventType.EVENT_RESTART_TERMIANL_BIN, self)
        self.subscribe(LTEventType.EVENT_RESTART_TERMIANL_SYSTEM, self)
        self.subscribe(LTEventType.EVENT_UPDATE_TERMINAL_BIN, self)
        self.subscribe(LTEventType.EVENT_START_CALIBRATION, self)
        self.subscribe(LTEventType.EVENT_STOP_CALIBRATION, self)
        self.subscribe(LTEventType.EVENT_RUNTIME_CHECK, self)
        self.subscribe(LTEventType.EVENT_SYSTEM_TIME_1, self)

    def _init_lt_process(self):
        self.judge_process()
        # self.data_hub_process = subprocess.Popen('./DataHub -c config.txt > /dev/null &', shell=True,
        #                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print('_init_lt_process(self) data_hub_process:', self.data_hub_process)

        # todo：read 函数会阻塞直到DataHub执行完毕，所以必须要在上层来保证config的正确
        # return_str = self.data_hub_process.stdout.read().decode()
        # print('_init_lt_process return_str:', return_str)
        #
        # if return_str.find('Failed initializing from file') != -1:  # 配置文件出错
        #     event = LTEventType.EVENT_CONFIG_FILE_ERROR
        #     event_content = return_str.encode()
        #     self.publish_event(event, event_content)
        #     MLog.mlogger.info(return_str)

        # self.loc_engine_process = subprocess.Popen('./LocEngine -c config.txt > /dev/null &', shell=True,
        #                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print('_init_lt_process(self) loc_engine_process:', self.loc_engine_process)
        # return_str = self.loc_engine_process.stdout.read().decode()
        # print('_init_lt_process return_str:', return_str)

        self.old_md5sum = subprocess.check_output("md5sum config.txt", shell=True)
        # print("old_md5sum: " + self.old_md5sum.decode())

    def event_handle(self, event, event_content):
        """
        事件处理函数，该函数可以理解为纯虚函数，MsgTarget子类必须要实现
        """
        # print('TermDeamon event handle ', event, event_content)
        if event == LTEventType.EVENT_SYSTEM_TIME_1:  # 每秒处理任务
            self._handle_md5sum()
            self.judge_process()

        elif event == LTEventType.EVENT_RESTART_TERMIANL_BIN:
            self.handle_term_bin_restart()

        elif event == LTEventType.EVENT_RESTART_TERMIANL_SYSTEM:
            print('TermDeamon event handle ', event, event_content)
            self.handle_term_system_restart()

        elif event == LTEventType.EVENT_UPDATE_TERMINAL_BIN:
            print('TermDeamon event handle ', event, event_content)
            self.handle_update_term_bin(event_content.decode())

        elif event == LTEventType.EVENT_START_CALIBRATION:
            print('TermDeamon event handle ', event, event_content)
            self.handle_enter_calibration()

        elif event == LTEventType.EVENT_STOP_CALIBRATION:
            print('TermDeamon event handle ', event, event_content)
            self.handle_exit_calibration()

        elif event == LTEventType.EVENT_RUNTIME_CHECK:
            print('TermDeamon event handle ', event, event_content)
            self.handle_runtime_check()

    def handle_term_bin_restart(self):
        print('handle_term_bin_restart')
        subprocess.Popen('killall LocEngine', shell=True)
        print('old loc_engine_process.pid:', self.loc_engine_process.pid)
        # end_str = self.loc_engine_process.stdout.read()  # read 会阻塞
        # MLog.mlogger.info(end_str)

        subprocess.Popen('killall DataHub', shell=True)
        # end_str = self.data_hub_process.stdout.read()
        # MLog.mlogger.info(end_str)

        time.sleep(0.2)

        self.data_hub_process = subprocess.Popen('./DataHub -c config.txt > /dev/null &', shell=True)
        # stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # todo：read 函数会阻塞直到DataHub执行完毕，所以必须要在上层来保证config的正确
        # error_str = self.data_hub_process.stdout.read()
        # MLog.mlogger.info(error_str)
        # if error_str.find('Failed initializing from file'):  # 配置文件出错
        #     event = LTEventType.EVENT_CONFIG_FILE_ERROR
        #     event_content = error_str.encode()
        #     self.publish_event(event, event_content)

        self.loc_engine_process = subprocess.Popen('./LocEngine -c config.txt > /dev/null &', shell=True)
        # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('new loc_engine_process.pid:', self.loc_engine_process.pid)
        # error_str = self.loc_engine_process.stdout.read()
        # MLog.mlogger.info(error_str)

    def handle_term_system_restart(self):
        print('handle_term_system_restart')
        """重启系统"""
        subprocess.Popen('sudo reboot', shell=True)
        # stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def handle_update_term_bin(self, update_url):
        print('handle_update_term_bin')
        # todo: 更新服务器没有搭建，暂时不写
        pass

    def handle_enter_calibration(self):
        print('handle_enter_calibration')
        time.sleep(0.2)  # 休眠一下等待config_template.txt磁盘同步
        subprocess.Popen('killall LocEngine', shell=True)
        # end_str = self.loc_engine_process.stdout.read()
        # MLog.mlogger.info(end_str)

        time.sleep(0.02)

        self.loc_engine_process = subprocess.Popen('./LocEngine -c config_template.txt', shell=True)
        # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # error_str = self.loc_engine_process.stdout.read()
        # MLog.mlogger.info(error_str)

    def handle_exit_calibration(self):
        print('handle_exit_calibration')
        subprocess.Popen('killall LocEngine', shell=True)
        # end_str = self.loc_engine_process.stdout.read()
        # MLog.mlogger.info(end_str)

        time.sleep(0.02)

        self.loc_engine_process = subprocess.Popen('./LocEngine -c config.txt > /dev/null &', shell=True)
        # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # error_str = self.loc_engine_process.stdout.read()
        # MLog.mlogger.info(error_str)

    def handle_runtime_check(self):
        print('handle_runtime_check')
        subprocess.Popen('killall LocEngine', shell=True)

        subprocess.Popen('killall DataHub', shell=True)

        time.sleep(0.2)

        self.data_hub_process = subprocess.Popen('./DataHub -c config.txt -d 0 | grep -F "[" > datahub.check &', shell=True)

        self.loc_engine_process = subprocess.Popen('./LocEngine -c config.txt -d 0 | grep -F "[" > locengine.check &', shell=True)

        time.sleep(1.5)

        self.handle_term_bin_restart()

        event = LTEventType.EVENT_RUNTIME_CHECK_FINISH
        event_content = bytes()
        self.publish_event(event, event_content)

    def deamon_run(self):
        # # print('deamon_run....')
        # if self.term_exit_flag is True:
        #     if self.data_hub_connect_flag is True:
        #         self._socket_sub_imu.disconnect(self._sub_imu_addr_port)
        #         self._socket_sub_imu.close(linger=0)
        #         self.data_hub_connect_flag = False
        #     return
        self.connect_data_hub()
        self.recv_imu_data()
        self.disconnect_data_hub()

    def judge_process(self):
        """判断DataHub和LocEngine是否存在"""
        # data_hub_exist_flag = False
        # loc_engine_exist_flag = False
        # pid_list = psutil.pids()
        # for pid in pid_list:
        #     if psutil.Process(pid).name() == 'DataHub':
        #         data_hub_exist_flag = True
        #
        #     elif psutil.Process(pid).name() == 'LocEngine':
        #         loc_engine_exist_flag = True

        process_info = subprocess.check_output("ps -fe | grep -e DataHub -e LocEngine| grep -v grep || true", shell=True).decode()

        if 'DataHub' not in process_info:
            # if data_hub_exist_flag is not True:
            MLog.mlogger.info('DataHub is not exist start DataHub')
            self.data_hub_process = subprocess.Popen('./DataHub -c config.txt > /dev/null &', shell=True)
            # stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if 'LocEngine' not in process_info:
            # if loc_engine_exist_flag is not True:
            MLog.mlogger.info('LocEngine is not exist start DataHub')
            self.loc_engine_process = subprocess.Popen('./LocEngine -c config.txt > /dev/null &', shell=True)
            # stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _handle_md5sum(self):
        now_md5sum = subprocess.check_output("md5sum config.txt", shell=True)
        # print("now_md5sum:" + now_md5sum.decode())
        if now_md5sum != self.old_md5sum:
            MLog.mlogger.info("config.txt file is changed!")
            self.handle_term_bin_restart()
            self.old_md5sum = now_md5sum

    def connect_data_hub(self):
        """连接Datahub"""
        if self.data_hub_connect_flag is False:
            self._socket_sub_imu = self.context.socket(zmq.SUB)
            self._socket_sub_imu.setsockopt(zmq.RCVTIMEO, 3000)
            self._socket_sub_imu.connect(self._sub_imu_addr_port)
            self._socket_sub_imu.setsockopt_string(zmq.SUBSCRIBE, 'Imu')
            self.data_hub_connect_flag = True

    def disconnect_data_hub(self):
        if self.data_hub_connect_flag is True:
            self._socket_sub_imu.disconnect(self._sub_imu_addr_port)
            self._socket_sub_imu.close(linger=0)
            self.data_hub_connect_flag = False

    def reconnect_data_hub(self):
        self.disconnect_data_hub()
        self.connect_data_hub()

    def recv_imu_data(self):
        if self.data_hub_connect_flag is True:
            if self._socket_sub_imu.poll(20):
                try:
                    topic, msg = self._socket_sub_imu.recv_multipart()
                    # print(topic, msg)
                    self.handle_imu_data(msg)
                except zmq.error.Again as err:
                    MLog.mlogger.warn('Exception:%s', err)
                    MLog.mlogger.warn(traceback.format_exc())
                    self.reconnect_data_hub()
        else:
            time.sleep(0.1)

    def handle_imu_data(self, msg):
        """判断imu的sensor配置"""
        sensor_num = msg[3] & 0xf0
        if sensor_num != self.old_sensor_num and self.old_sensor_num != -1:
            event = LTEventType.EVENT_SENSOR_HOT_PLUG
            event_content = (global_local_hostname + ' sensor change number:' + str(sensor_num)).encode()
            self.publish_event(event, event_content)
        self.old_sensor_num = sensor_num

    def exit(self):
        pass
        # self.term_exit_flag = True
        # if self.loc_engine_process is not None:
        #     subprocess.Popen('killall LocEngine', shell=True)
        #     self.loc_engine_process = None
        # if self.data_hub_process is not None:
        #     subprocess.Popen('killall DataHub', shell=True)
        #     self.data_hub_process = None

    def __del__(self):
        self.unsubscribe(LTEventType.EVENT_RESTART_TERMIANL_BIN, self)
        self.unsubscribe(LTEventType.EVENT_RESTART_TERMIANL_SYSTEM, self)
        self.unsubscribe(LTEventType.EVENT_UPDATE_TERMINAL_BIN, self)
        self.unsubscribe(LTEventType.EVENT_START_CALIBRATION, self)
        self.unsubscribe(LTEventType.EVENT_STOP_CALIBRATION, self)
        self.unsubscribe(LTEventType.EVENT_RUNTIME_CHECK, self)
        self.subscribe(LTEventType.EVENT_SYSTEM_TIME_1, self)
        super(TermDeamon, self).__del__()


class TermBroadCast(MThread, EventTarget):
    """
    terminal BroadCast Response
    接收udp广播包，响应广播，与控制器建立连接
    """
    HOST = ''
    PORT = NetWorkInfo.UDP_BROADCAST_PORT
    BUFSIZE = 4068
    ADDR = (HOST, PORT)

    controller_rep_port = None
    loc_xsub_port = None
    controller_ip_addr = None

    def __init__(self, thread_name):
        self.thread_name = thread_name

        self.rep_cast_ip_addr = None

        self.ctrller_connected = False

        # 该类构造父类必须要最后
        MThread.__init__(self, self, thread_name)

    def thread_task(self):
        """
        线程主循环函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        # 循环接收控制器广播包
        readable, writeable, exceptional = select.select([self._udp_sock], [self._udp_sock], [self._udp_sock],
                                                         self.__sock_timeout)
        for self._udp_sock in readable:
            self._recv_broadcast()

    def setup_thread(self):
        """
        子线程初始操作函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        EventTarget.__init__(self, self)  # 该父类的构造必须是要再该线程执行中,最开始执行
        print('setup_thread...........', threading.current_thread(), self.thread_name)
        self.event_handle_sleep = 0.5
        self.thread_loop_sleep = 0.5
        self._init_udp_socket()

        self.subscribe(LTEventType.EVENT_NETWORK_DISCONNECT, self)
        self.subscribe(LTEventType.EVENT_NETWORK_CONNECTED, self)

    def event_handle(self, event, event_content):
        """
        事件处理函数，该函数可以理解为纯虚函数，MsgTarget子类必须要实现
        """
        if event == LTEventType.EVENT_NETWORK_DISCONNECT:
            self.ctrller_connected = False

        elif event == LTEventType.EVENT_NETWORK_CONNECTED:
            self.ctrller_connected = True

    def _init_udp_socket(self):
        self.context = EventBus.CONTEXT

        self._udp_sock = socket(AF_INET, SOCK_DGRAM)
        self._udp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._udp_sock.bind(TermBroadCast.ADDR)

        self.__sock_timeout = 200

        self.local_ip_addr = global_local_ip_addr

    def _recv_broadcast(self):
        """接收解析广播包"""
        try:
            data, ctrller_addr = self._udp_sock.recvfrom(TermBroadCast.BUFSIZE)
            # print('_recv_broadcast:', data, addr)
            self.rep_cast_ip_addr = ctrller_addr
            msg_parse = message_pb2.ControllerBroadcast()
            msg_parse.ParseFromString(data)
            # print('recv msg', msg)
            msg_parse.ip_addr = ctrller_addr[0]  # 获取可靠的地址

            msg = msg_parse.SerializeToString()
            self._response_cast(msg)
        except Exception as e:
            MLog.mlogger.warn('_recv_broadcast:', str(e))
            MLog.mlogger.warn(traceback.format_exc())

    def _response_cast(self, msg):
        """给控制器响应广播包"""
        if self.ctrller_connected:  # 如果已经连接上控制器就不响应广播了
            return

        # 获取所有网卡ip地址
        local_ip_addr_list = NetWorkInfo.get_all_ip_addr()
        # 判断ip 是否和控制器ip在同一个网段
        ret = NetWorkInfo.judge_ip_network_segment(local_ip_addr_list, self.rep_cast_ip_addr[0])
        if ret is not False:
            self.local_ip_addr = ret
        else:
            return

        msg_pack = message_pb2.BroadcastResponse()
        msg_pack.type = message_pb2.BroadcastResponse.TERMINAL_TYPE
        msg_pack.ip_addr = self.local_ip_addr
        msg_pack.mac_addr = global_local_mac_addr
        msg_pack.host_name = global_local_hostname
        # print('_response_cast: ', msg)
        msg_str = msg_pack.SerializeToString()
        try:
            ret = self._udp_sock.sendto(msg_str, self.rep_cast_ip_addr)
            # print('self._udp_sock.sendto ret:', ret)
            self._send_find_ctrller_event(msg)
        except Exception as e:
            MLog.mlogger.warn('_response_cast:%s' % str(e))
            MLog.mlogger.warn(traceback.format_exc())

    def _send_find_ctrller_event(self, msg):
        """发送找到控制器事件"""
        print('TermBroadCast _send_find_ctrller_event')
        event = LTEventType.EVENT_FIND_CONTROLLER
        event_content = msg
        self.publish_event(event, event_content)

    # def exit(self):
    #     super().exit()
    #     self._udp_sock.close()

    def __del__(self):
        self.unsubscribe(LTEventType.EVENT_NETWORK_DISCONNECT, self)  # 订阅之后必须在析构处取消订阅
        self.unsubscribe(LTEventType.EVENT_NETWORK_CONNECTED, self)
        super(TermBroadCast, self).__del__()


class TermDataHandle(MThread, EventTarget):
    """
    TermDataHandle 终端接收controller数据处理类
    """

    def __init__(self, thread_name):
        self.config_file_name = 'config.txt'
        self.config_file_update = ''
        self.thread_name = thread_name

        self.context = EventBus.CONTEXT
        self._socket_req = None
        self._req_socket_addr_port = None

        self.ctrller_connect_flag = False

        self.wait_rep_flag = False
        self.wait_rep_count = 0

        self.sequence = 0  # 发送心跳包的序列号
        self.config_error_string = ''
        self.sensor_config_change = ''
        self.data_hub_check_info = ''
        self.loc_engine_check_info = ''
        self.controller_broadcast_msg = b''
        # 该类构造父类必须要最后
        MThread.__init__(self, self, thread_name)

    def thread_task(self):
        """
        线程主循环函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        # 接收心跳包响应
        if self.ctrller_connect_flag is True and self.wait_rep_flag is True:
            if self._socket_req.poll(200):  # 0.2秒
                self.recv_response()

    def send_heartbeat_request(self):
        """对于终端来说，目前只有心跳请求"""

        req_msg = message_pb2.TerminalHeartbeatRequest()
        req_msg.sequence = self.sequence  # self.sequence
        req_msg.ok_status = True
        except_status = message_pb2.TerminalExceptStatus()
        except_status.mac_addr = global_local_mac_addr

        if self.config_error_string != '':  # CONFIG_ERROR
            print('self.config_error_string:', self.config_error_string)
            req_msg.ok_status = False
            except_status.config_error = True
            except_status.except_detail.extend([self.config_error_string])
            self.config_error_string = ''

        if self.sensor_config_change != '':  # SENSOR_CHANGE if 顺序要找protobuf里面的排列来
            print('self.sensor_config_change:', self.sensor_config_change)
            req_msg.ok_status = False
            except_status.sensor_change = True
            except_status.except_detail.extend([self.sensor_config_change])
            self.sensor_config_change = ''

        if self.data_hub_check_info != '':
            # print('self.data_hub_check_info:', self.data_hub_check_info)
            req_msg.ok_status = False
            except_status.data_hub_check_info = self.data_hub_check_info
            self.data_hub_check_info = ''

        if self.loc_engine_check_info != '':
            # print('self.loc_engine_check_info:', self.loc_engine_check_info)
            req_msg.ok_status = False
            except_status.loc_engine_check_info = self.loc_engine_check_info
            self.loc_engine_check_info = ''

        if not req_msg.ok_status:
            print('req_msg.except_status_detail.CopyFrom(except_status)')
            req_msg.except_status_detail.CopyFrom(except_status)

        req_data = req_msg.SerializeToString()
        # print('send_heartbeat_request: ', req_msg)
        try:
            self._socket_req.send_multipart([global_local_mac_addr.encode(), b'TerminalHeartbeatRequest', req_data])
            self.wait_rep_flag = True
        except zmq.error.Again as err:
            MLog.mlogger.warn('Terminal send_heartbeat_request Exception: ', err)
            MLog.mlogger.warn(traceback.format_exc())
            self.reconnect_controller()

        # print('send_heartbeat_request send end')

    def recv_response(self):
        """
        接收响应
        """
        try:
            msg = self._socket_req.recv_multipart()
        except zmq.error.Again as err:
            MLog.mlogger.warn('recv_response Exception: ', err)
            MLog.mlogger.warn(traceback.format_exc())
            self.reconnect_controller()
            return
        # 处理msg
        self.handle_heartbeat_msg_rep(msg)
        self.wait_rep_flag = False

    def handle_heartbeat_msg_rep(self, msg):
        """
        处理终端控制器上返回的响应
        """
        if msg[0].decode() != 'TerminalHeartbeatResponse':
            return False

        rep_msg = message_pb2.TerminalHeartbeatResponse()
        rep_msg.ParseFromString(msg[1])
        # print('handle_heartbeat_msg_rep rep_msg: ', rep_msg)

        if self.sequence != rep_msg.sequence:
            MLog.mlogger.info('response pack error,not terminal response %d,%d', self.sequence, rep_msg.sequence)
            self.sequence = rep_msg.sequence

        if self.sequence >= 2147483647:  # sys.maxsize = 9223372036854775807 因此不能用
            self.sequence = 1
        if self.sequence == 0:
            # 发送连接上控制器事件
            event = LTEventType.EVENT_NETWORK_CONNECTED
            event_content = self.controller_broadcast_msg
            self.publish_event(event, event_content)
        self.sequence += 1

        if rep_msg.status.code != message_pb2.ResponseStatus.OK:  # todo:还有一些响应状态未处理
            MLog.mlogger.info('controller return error, code:{},{}'.format(rep_msg.status.code, rep_msg.status.detail))
            # self.disconnect_controller()

        # elif rep_msg.status.code == message_pb2.ResponseStatus.NETWORK_FAILURE:
        #         self.disconnect_controller()
        #
        # elif rep_msg.status.code == message_pb2.ResponseStatus.TERMINAL_NOTFOUND:
        #         self.disconnect_controller()

        if rep_msg.event.event == message_pb2.UpdateEvent.CONFIG_UPDATE:
            self.config_file_update = rep_msg.event.detail
            print('handle_heartbeat_msg_rep message_pb2.UpdateEvent.CONFIG_UPDATE:')
            if self.config_file_update != '':
                with open(self.config_file_name, 'w', encoding='utf-8') as f:
                    f.write(self.config_file_update)
                    # os.fsync(f)  # 不能用 会卡死

                # event = LTEventType.EVENT_RESTART_TERMIANL_BIN  # 修改配置自动重启
                # event_content = bytes()
                # self.publish_event(event, event_content)

        if rep_msg.HasField('action_request_from_gui'):
            act_msg = rep_msg.action_request_from_gui
            print('act_msg: ', act_msg)
            if act_msg.type == message_pb2.TerminalActionRequest.RESTART_HOST:
                event = LTEventType.EVENT_RESTART_TERMIANL_SYSTEM
                event_content = bytes()
                self.publish_event(event, event_content)

            elif act_msg.type == message_pb2.TerminalActionRequest.RESTART_BIN:
                event = LTEventType.EVENT_RESTART_TERMIANL_BIN
                event_content = bytes()
                self.publish_event(event, event_content)

            elif act_msg.type == message_pb2.TerminalActionRequest.UPDATE_BIN:
                event = LTEventType.EVENT_UPDATE_TERMINAL_BIN
                event_content = rep_msg.update_url.encode()
                self.publish_event(event, event_content)

            elif act_msg.type == message_pb2.TerminalActionRequest.START_CALIBRATION:
                self.handle_fixed_act()

            elif act_msg.type == message_pb2.TerminalActionRequest.STOP_CALIBRATION:
                event = LTEventType.EVENT_STOP_CALIBRATION
                event_content = bytes()
                self.publish_event(event, event_content)

            elif act_msg.type == message_pb2.TerminalActionRequest.RUNTIME_CHECK:
                event = LTEventType.EVENT_RUNTIME_CHECK
                event_content = bytes()
                self.publish_event(event, event_content)

    def setup_thread(self):
        """
        子线程初始操作函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        print('setup_thread...........', threading.current_thread(), self.thread_name)
        EventTarget.__init__(self, self)  # 该父类的构造必须是要再该线程执行中

        self.event_handle_sleep = 0.5
        self.thread_loop_sleep = 0.1

        self.subscribe(LTEventType.EVENT_FIND_CONTROLLER, self)
        self.subscribe(LTEventType.EVENT_SENSOR_HOT_PLUG, self)
        self.subscribe(LTEventType.EVENT_CONFIG_FILE_ERROR, self)
        self.subscribe(LTEventType.EVENT_RUNTIME_CHECK_FINISH, self)
        self.subscribe(LTEventType.EVENT_SYSTEM_TIME_1, self)

    def event_handle(self, event, event_content):
        """
        事件处理函数，该函数可以理解为纯虚函数，MsgTarget子类必须要实现
        """
        # print('TermDataHandle event handle:', event, event_content)
        if event == LTEventType.EVENT_FIND_CONTROLLER:
            # print('_req_socket_addr_port: ', self._req_socket_addr_port)
            self.connect_controller(event_content)

        elif event == LTEventType.EVENT_SENSOR_HOT_PLUG:
            print('TermDataHandle event handle:', event, event_content)
            self.sensor_config_change = event_content.decode()

        elif event == LTEventType.EVENT_CONFIG_FILE_ERROR:
            print('TermDataHandle event handle:', event, event_content)
            self.config_error_string = event_content.decode()

        elif event == LTEventType.EVENT_RUNTIME_CHECK_FINISH:
            with open('datahub.check', 'r', encoding='utf-8') as f:
                for i in range(0, 20):
                    self.data_hub_check_info += f.readline()

            with open('locengine.check', 'r', encoding='utf-8') as f:
                for i in range(0, 20):
                    self.loc_engine_check_info += f.readline()

        elif event == LTEventType.EVENT_SYSTEM_TIME_1:
            if self.wait_rep_flag is False and self.ctrller_connect_flag is True:
                if self._socket_req.poll(200, zmq.POLLOUT):
                    self.send_heartbeat_request()
                    self.wait_rep_count = 0
            elif self.ctrller_connect_flag is True and self.wait_rep_flag is True:
                self.wait_rep_count += 1
                if self.wait_rep_count >= 15:  # 15秒没有收到响应就说明网络异常了
                    MLog.mlogger.info('wait_rep_count >= 5 disconnect_controller')
                    self.disconnect_controller()

    # def exit(self):
    #     super().exit()
    #     self.disconnect_controller()

    def __del__(self):
        self.unsubscribe(LTEventType.EVENT_FIND_CONTROLLER, self)
        self.unsubscribe(LTEventType.EVENT_SENSOR_HOT_PLUG, self)
        self.unsubscribe(LTEventType.EVENT_CONFIG_FILE_ERROR, self)
        self.unsubscribe(LTEventType.EVENT_RUNTIME_CHECK_FINISH, self)
        self.unsubscribe(LTEventType.EVENT_SYSTEM_TIME_1, self)
        super(TermDataHandle, self).__del__()

    def connect_controller(self, msg):
        """连接控制器，包req端口"""

        if self.ctrller_connect_flag is False:
            self.controller_broadcast_msg = msg
            msg_parse = message_pb2.ControllerBroadcast()
            msg_parse.ParseFromString(msg)

            self._req_socket_addr_port = 'tcp://' + msg_parse.ip_addr + ':' \
                                         + str(msg_parse.terminal_port)

            print('TermDataHandle connect_controller')
            self._socket_req = self.context.socket(zmq.REQ)
            self._socket_req.setsockopt(zmq.LINGER, 0)
            self._socket_req.setsockopt(zmq.REQ_CORRELATE, 1)
            self._socket_req.setsockopt(zmq.REQ_RELAXED, 1)
            self._socket_req.setsockopt(zmq.RCVTIMEO, 5000)
            self._socket_req.setsockopt(zmq.SNDTIMEO, 5000)
            self._socket_req.connect(self._req_socket_addr_port)
            self.ctrller_connect_flag = True
            self.wait_rep_flag = False
            self.wait_rep_count = 0
            self.sequence = 0
            time.sleep(0.5)
            self.start()

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
            self.wait_rep_flag = False
            self.wait_rep_count = 0
            event = LTEventType.EVENT_NETWORK_DISCONNECT
            event_content = bytes()
            self.publish_event(event, event_content)
            self.stop()

    def reconnect_controller(self):
        print('TermDataHandle reconnect_controller')
        self.disconnect_controller()
        self.connect_controller()

    def handle_fixed_act(self):
        print('TermDataHandle handle_fixed_act:')
        # 拷贝config.txt到config_template.txt
        shutil.copyfile(self.config_file_name, 'config_template.txt')
        config_obj = ConfigObj('config_template.txt', encoding='UTF8')
        # 将基站坐标和初始角还原
        bs_loc_list = config_obj['BS_LOCATIONS']
        for i in range(0, len(bs_loc_list)):
            if i % 3 == 0:
                bs_loc_list[i] = '0'
            elif i % 3 == 1:
                bs_loc_list[i] = '0'
            elif i % 3 == 2:
                bs_loc_list[i] = '300'
        config_obj['BS_LOCATIONS'] = bs_loc_list

        angle_list = config_obj['BS_START_ANGLES']
        if type(angle_list) == list:
            for i in range(0, len(angle_list)):
                angle_list[i] = '0'
        elif type(angle_list) == str:
            angle_list = '0'
        config_obj['BS_START_ANGLES'] = angle_list

        config_obj.write()

        event = LTEventType.EVENT_START_CALIBRATION
        event_content = bytes()
        self.publish_event(event, event_content)


str_loc_type = {
    b'Loc raw': message_pb2.Location.LOC_SENSOR_RAW,
    b'Loc sensor filtered': message_pb2.Location.LOC_SENSOR_FILTERED,
    b'Loc robot filtered': message_pb2.Location.LOC_ROBOT_FILTERED,
    b'Loc sensor filtered noimu': message_pb2.Location.LOC_SENSOR_FILTERED_NOIMU,
    b'Loc robot filtered noimu': message_pb2.Location.LOC_ROBOT_FILTERED_NOIMU,
    b'Loc raw unregistered bs': message_pb2.Location.LOC_SENSOR_RAW_UNREGISTERED_BS,
    b'Loc sensor filtered0': message_pb2.Location.LOC_SENSOR_FILTERED0,
    b'Loc sensor filtered1': message_pb2.Location.LOC_SENSOR_FILTERED1,
}


class PublishLoc(MThread, EventTarget):
    """
    PublishLoc 负责发布位置的类
    """

    def __init__(self, thread_name):
        self.thread_name = thread_name

        self.context = EventBus.CONTEXT
        self._socket_pub_loc = None
        self._pub_loc_addr_port = 'tcp://'
        self._socket_sub_loc = None
        self._sub_loc_addr_port = 'tcp://localhost:6102'

        self.ctrller_connect_flag = False

        self.loc_engine_connect_flag = False
        self.loc_engine_no_data_count = 0  # 用来监视Loc Engine 解析数据是否正常

        # 该类构造父类必须要最后
        MThread.__init__(self, self, thread_name)

    def thread_task(self):
        """
        线程主循环函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        # 接收LocEngine的数据
        if self.loc_engine_connect_flag is True:
            self.recv_loc_data()
        else:
            time.sleep(0.5)

    def setup_thread(self):
        """
        子线程初始操作函数，该函数可以理解为纯虚函数，MThread子类必须要实现
        """
        print('setup_thread...........', threading.current_thread(), self.thread_name)
        EventTarget.__init__(self, self)  # 该父类的构造必须是要再该线程执行中,最开始执行
        self.event_handle_sleep = 1.2
        self.thread_loop_sleep = 0.01
        self.connect_loc_engine()

        self.subscribe(LTEventType.EVENT_NETWORK_CONNECTED, self)
        self.subscribe(LTEventType.EVENT_NETWORK_DISCONNECT, self)
        # self.subscribe(LTEventType.EVENT_SYSTEM_TIME_1, self)

    def event_handle(self, event, event_content):
        """
        事件处理函数，该函数可以理解为纯虚函数，MsgTarget子类必须要实现
        """
        # print('Public Loc event handle:', event, event_content)
        if event == LTEventType.EVENT_NETWORK_CONNECTED:
            self.connect_controller(event_content)

        elif event == LTEventType.EVENT_NETWORK_DISCONNECT:
            self.disconnect_controller()

        # elif event == LTEventType.EVENT_SYSTEM_TIME_1:
        #     if self.loc_engine_connect_flag is True:
        #         self.loc_engine_no_data_count += 1
        #         if self.loc_engine_no_data_count == 100:
        #             self.loc_engine_no_data_count = 0  # 100 秒没有收到位置数据了
        #             # self.publish_event(LTEventType.EVENT_RESTART_TERMIANL_BIN, b'')

    # def exit(self):
    #     super().exit()
    #     self.disconnect_controller()
    #     self.disconnnect_loc_engine()

    def __del__(self):
        self.unsubscribe(LTEventType.EVENT_NETWORK_CONNECTED, self)
        self.unsubscribe(LTEventType.EVENT_NETWORK_DISCONNECT, self)
        # self.unsubscribe(LTEventType.EVENT_SYSTEM_TIME_1, self)
        super(PublishLoc, self).__del__()

    def connect_loc_engine(self):
        """连接LocEngine"""
        if self.loc_engine_connect_flag is False:
            print('publish loc connect_loc_engine:', self._sub_loc_addr_port)
            self._socket_sub_loc = self.context.socket(zmq.SUB)
            self._socket_sub_loc.setsockopt(zmq.RCVTIMEO, 3000)
            self._socket_sub_loc.connect(self._sub_loc_addr_port)
            self._socket_sub_loc.setsockopt_string(zmq.SUBSCRIBE, 'Loc')
            self.loc_engine_connect_flag = True

    def disconnnect_loc_engine(self):
        if self.loc_engine_connect_flag is True:
            print('publish loc reconnect_loc_engine:', self._sub_loc_addr_port)
            self._socket_sub_loc.disconnect(self._sub_loc_addr_port)
            self._socket_sub_loc.close(linger=0)
            self.loc_engine_connect_flag = False

    def reconnect_loc_engine(self):
        self.disconnnect_loc_engine()
        self.connect_loc_engine()

    def recv_loc_data(self):
        """接收LocEngine的位置数据"""
        while self._socket_sub_loc.poll(20):  # 20毫秒不能太高，因为位置频率很高，会陷入死循环，一直为true
            try:
                topic, msg = self._socket_sub_loc.recv_multipart()
                if msg is not None:
                    self.loc_engine_no_data_count = 0
                if self.ctrller_connect_flag is True:
                    self.publish_loc_data(topic, msg)
            except zmq.error.Again as err:
                MLog.mlogger.warn('Exception:%s', err)
                MLog.mlogger.warn(traceback.format_exc())
                self.reconnect_loc_engine()

    def publish_loc_data(self, topic, msg):
        """
        发布位置数据到控制器
        """
        if topic not in str_loc_type or msg is None:
            print('str_loc_type not in str_loc_type or msg is None:', topic, msg)
            return

        try:
            x, y, z, heading, gamma, theta, ts, bs_index, sensor_id \
                = scanf.scanf("%f %f %f %f %f %f %f %d %d", msg.decode())
            location = message_pb2.Location()

            location.type = str_loc_type[topic]
            location.coordinates.x = x
            location.coordinates.y = y
            location.coordinates.z = z
            location.heading = heading
            location.gamma = gamma
            location.theta = theta
            location.ts = ts
            location.bs_index = bs_index
            location.sensor_id = sensor_id
            location.sensor_channel_id = 0
            location.terminal_id = global_local_mac_addr
            # print('publish_loc_data:', location)
            msg_topic = b'Location'
            msg_content = location.SerializeToString()
            try:
                if self._socket_pub_loc.poll(500, zmq.POLLOUT):
                    self._socket_pub_loc.send_multipart([msg_topic, msg_content])
            except zmq.error.Again as err:
                MLog.mlogger.warn('Exception:%s', err)
                MLog.mlogger.warn(traceback.format_exc())
                self.reconnect_controller()
        except Exception as err:
            MLog.mlogger.warn('Exception err: %s,%s', err, msg.decode())
            return

    def connect_controller(self, msg):
        """连接控制器，XSUB端口"""
        if self.ctrller_connect_flag is False:
            msg_parse = message_pb2.ControllerBroadcast()
            msg_parse.ParseFromString(msg)

            self._pub_loc_addr_port = 'tcp://' + msg_parse.ip_addr + ':' + str(
                msg_parse.loc_xsub_port)
            print('publish loc connect_controller:', self._pub_loc_addr_port)
            self._socket_pub_loc = self.context.socket(zmq.PUB)
            self._socket_pub_loc.setsockopt(zmq.SNDTIMEO, 3000)
            self._socket_pub_loc.connect(self._pub_loc_addr_port)
            self.ctrller_connect_flag = True

    def disconnect_controller(self):
        """
        断开与控制器的连接，XSUB端口
        """
        if self.ctrller_connect_flag is True:
            print('publish loc disconnect_controller:', self._pub_loc_addr_port)
            self._socket_pub_loc.disconnect(self._pub_loc_addr_port)
            self._socket_pub_loc.close(linger=0)
            self.ctrller_connect_flag = False

    def reconnect_controller(self):
        self.disconnect_controller()
        self.connect_controller()


class Terminal(object):
    """终端类"""
    def __init__(self):
        self.judge_terinal_exit()
        self.register_signal()
        self.terminal_exit_flag = False
        self.publish_loc = None
        self.term_data_handle = None
        self.term_broad_cast = None
        self.lt_daemon = None
        self.debug_mode = False

        argv_list = sys.argv[1:]
        if len(argv_list) > 0 and argv_list[0] == '-d':
            self.debug_mode = True

        self.eventbus = EventBus()
        self.main_event_client = EventClient()

        main_loop = asyncio.get_event_loop()
        tasks = [self.system_initialize(), self.main_task_handle(), self.system_timer()]

        future = asyncio.wait(tasks)

        main_loop.run_until_complete(future)

        main_loop.close()

    def judge_terinal_exit(self):
        process_count = subprocess.check_output("ps -fe | grep terminal.py |grep -v grep | wc -l", shell=True).decode()
        if process_count != '1\n':
            print('Terminal has exist, This process exit:', process_count)
            exit(0)

    async def system_timer(self):
        """
        发布系统的每一秒的定时事件
        """
        await asyncio.sleep(1)  # 先sleep 1秒之后才发
        old_time = time.time()
        while True:
            try:
                current_time = time.time()
                time_diff = current_time - old_time
                if time_diff >= 1.0:
                    # print('system_timer current_time:', current_time)
                    event = LTEventType.EVENT_SYSTEM_TIME_1
                    event_content = bytes()
                    self.main_event_client.publish_event(event, event_content)
                    old_time = current_time
            except Exception as err:
                MLog.mlogger.warn('Exception as err:%s', err)
                MLog.mlogger.warn(traceback.format_exc())

            await asyncio.sleep(0.1)

            if self.terminal_exit_flag:
                # print('system_timer exit....')
                break
        return

    async def main_task_handle(self):
        """
        主线程的消息客户端事件处理
        """
        # print('main_task_handle: ', threading.get_ident())
        while True:
            try:
                if self.main_event_client is not None:
                    # print('main_task_handle event_client.handle_event')
                    self.main_event_client.handle_event()
            except Exception as err:
                MLog.mlogger.warn('Exception as err:%s', err)
                MLog.mlogger.warn(traceback.format_exc())
            await asyncio.sleep(0.01)

            if self.terminal_exit_flag:
                self.main_event_client.client_close()
                # print('main_task_handle exit....')
                break
        return

    async def system_initialize(self):
        try:
            self.publish_loc = PublishLoc('publish loc')
            self.publish_loc.start()

            self.term_data_handle = TermDataHandle('term data handle thread')
            self.term_data_handle.start()

            self.term_broad_cast = TermBroadCast('term broad cast')
            self.term_broad_cast.start()

            await asyncio.sleep(2)  # LocEngine和DataHub 延迟一点启动
            if not self.debug_mode:
                self.lt_daemon = TermDeamon()
            else:
                return
        except Exception as err:
            MLog.mlogger.warn('Exception as err:%s', err)
            MLog.mlogger.warn(traceback.format_exc())

        while True:
            try:
                if self.lt_daemon is not None:
                    self.lt_daemon.deamon_run()
                    await asyncio.sleep(2)
            except Exception as err:
                MLog.mlogger.warn('Exception as err:%s', err)
                MLog.mlogger.warn(traceback.format_exc())

            if self.terminal_exit_flag:
                # print('system_initialize exit....')
                break
        return

    def signal_handler(self, signum, frame):
        print('Received signal: ', signum)
        # traceback.print_stack()
        self.terminal_exit_flag = True
        self.publish_loc.exit()
        self.term_data_handle.exit()
        self.term_broad_cast.exit()
        if self.lt_daemon is not None:
            self.lt_daemon.exit()

    def register_signal(self):
        signal.signal(signal.SIGHUP, self.signal_handler)  # 1
        signal.signal(signal.SIGINT, self.signal_handler)  # 2
        signal.signal(signal.SIGQUIT, self.signal_handler)  # 3
        signal.signal(signal.SIGABRT, self.signal_handler)  # 6
        signal.signal(signal.SIGTERM, self.signal_handler)  # 15
        signal.signal(signal.SIGSEGV, self.signal_handler)  # 11


if __name__ == '__main__':
    """"""
    try:
        terminal = Terminal()
        os._exit(0)
    except Exception as err:
        MLog.mlogger.warn('Exception as err:%s', err)
        MLog.mlogger.warn(traceback.format_exc())