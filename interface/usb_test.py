#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/21 9:51
# @Author  : hedengfeng
# @Site    : 
# @File    : usb_test.py.py
# @Software: terminal
# @description: 

import sys
import usb.core

import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

LOG_FILE = 'can_data_error.log'


class CanLog(object):
    """
        日志功能类
    """
    mlogger = logging.getLogger('TestNewBases')
    mlogger.setLevel(logging.DEBUG)
    log_fmt = '%(asctime)s,%(thread)s:%(filename)s:%(lineno)d :%(message)s'
    formatter = logging.Formatter(log_fmt)

    # create a handler,use to write log file
    # log_file_handler = TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=7)
    log_file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=20)
    log_file_handler.setLevel(logging.WARN)

    # define format
    log_file_handler.setFormatter(formatter)

    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.formatter = formatter  # 也可以直接给formatter赋值

    # add file handler
    mlogger.addHandler(log_file_handler)
    mlogger.addHandler(console_handler)


class CanTest(object):
    def __init__(self):
        self.alive = False
        self.handle = None
        self.size = 8
        self.vid = 0x04d8
        self.pid = 0x0053
        self.dev = None
        self.ep_in = None
        self.ep_out = None
        self.old_data_list = None

        self.proto = CanProtocal()

    def start(self):
        """
        开始，打开usb设备
        """
        self.dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
        print(type(self.dev))
        if self.dev is not None:
            cfg = self.dev.get_active_configuration()
            print(cfg)
            # intf = cfg[(0, 0)]
            self.dev.set_configuration()
            self.ep_in = self.dev[0][(0, 0)][0].bEndpointAddress
            print('self.ep_in:', self.ep_in)
            self.ep_out = self.dev[0][(0, 0)][1].bEndpointAddress
            print('self.ep_out:', self.ep_out)
            self.size = self.dev[0][(0, 0)][1].wMaxPacketSize
            print('self.size:', self.size)
        # self.open()
        self.alive = True

    def read(self, size=64, timeout=0):
        """
        读取usb设备发过来的数据
        """
        data = self.dev.read(self.ep_out, size, timeout)
        try:
            data_list = data.tolist()
            return data_list
        except Exception as e:
            print('tolist Exception e:', e)
            return list()

    def run(self):
        loc_data_list = []
        while True:
            try:
                data_list = self.read()
                for i in range(0, 3):
                    # print(data_list)
                    if i == 0:
                        loc_data_list = data_list[14:22]
                    if i == 1:
                        loc_data_list = data_list[35:43]
                    if i == 1:
                        loc_data_list = data_list[56:64]
                    # print("loc_data_list data:", ['{:02x}'.format(i) for i in loc_data_list])

                    if self.proto.judge_check_sum(loc_data_list) is False:
                        CanLog.mlogger.warn('校验和出错...%s', '{}'.format(['{:02x}'.format(i) for i in data_list]))

                    self.proto.parse(loc_data_list)
            except Exception as e:
                print('run func Exception e:', e)
                break


class CanProtocal(object):
    def __init__(self):
        self.loc_data_list = None

        self.loctype = None
        self.sensor_id = None
        self.heading = None
        self.loc_x = None
        self.loc_y = None

    def parse(self,loc_data_list):
        # print("loc_data_list data:", ['{:02x}'.format(i) for i in loc_data_list])

        self.loctype = ((loc_data_list[3] & 0xC0) >> 6)
        self.sensor_id = ((loc_data_list[3] & 0x30) >> 4)
        self.heading = (loc_data_list[2] & 0xFF) + ((loc_data_list[3] << 8) & 0x0F00)
        self.loc_x = (loc_data_list[4] & 0x00FF) + ((loc_data_list[5] << 8) & 0xFF00) - 30000
        self.loc_y = (loc_data_list[6] & 0x00FF) + ((loc_data_list[7] << 8) & 0xFF00) - 30000
        # print('loctype:', self.loctype, 'sensor_id:', self.sensor_id, 'heading:',
        #       self.heading, 'loc_x:', self.loc_x, 'loc_y:', self.loc_y)

    @staticmethod
    def judge_check_sum(loc_data_list):
        check_sum = (loc_data_list[0] & 0x00FF) + ((loc_data_list[1] << 8) & 0xFF00)
        # print(check_sum)

        calc_check_sum = 0
        for i in range(2, 8, 2):
            calc_check_sum += (loc_data_list[i] & 0x00FF) + ((loc_data_list[i + 1] << 8) & 0xFF00)

        calc_check_sum = (calc_check_sum >> 16) + (calc_check_sum & 0xFFFF)
        calc_check_sum += calc_check_sum >> 16
        calc_check_sum = ~calc_check_sum & 0x0000FFFF
        # print('calc_check_sum:{:04x}'.format(calc_check_sum))
        if check_sum == calc_check_sum:
            return True
        else:
            print('check_sum:{0:02X},calc_check_sum:{1:02X}'.format(check_sum, calc_check_sum))
            return False


if __name__ == '__main__':
    # !/usr/bin/python
    # import sys
    # import usb.core
    #
    # find USB devices
    dev = usb.core.find(find_all=True)
    print(dev)
    # loop through devices, printing vendor and product ids in decimal and hex
    for cfg in dev:
        sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + '\n')
        sys.stdout.write('Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')

    # argv_list = sys.argv[1:]
    test = CanTest()
    test.start()
    test.run()
