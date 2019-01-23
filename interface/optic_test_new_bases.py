#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/14 10:59
# @Author  : hedengfeng
# @Site    : 
# @File    : spi_read_data.py
# @Software: terminal
# @description:
import sys

import spidev
import time


import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

LOG_FILE = 'test_new_bases.log'


class BasesLog(object):
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


class SpiReadData(object):
    def __init__(self, address_list):
        self.bases_address_list = []
        self.bases_address_dict = {}
        for i in address_list:
            bases = int(i)
            self.bases_address_list.append(bases)
            self.bases_address_dict[bases] = 1

        self.bases_address_list_len = len(self.bases_address_list)
        self.cur_address_index = 0
        self.old_ts = 0
        self.old_seq = 0

        bus = 0
        device = 0
        self.spi_dev = spidev.SpiDev()
        self.spi_dev.open(bus, device)
        self.spi_dev.mode = 0b11
        self.spi_dev.max_speed_hz = 2000000

    @staticmethod
    def getType(data):
        ftype = data[3] >> 4
        return ftype

    @staticmethod
    def getLength(data):
        len = (data[4] << 8) + data[5]
        return len

    @staticmethod
    def getSeq(data):
        seq = (data[6] << 8) + data[7]
        return seq

    @staticmethod
    def getTs(data):
        ts = (data[-10] << 40) + (data[-9] << 32) + (data[-8] << 24) + (data[-7] << 16) + (data[-6] << 8) + (data[-5])
        return ts

    @staticmethod
    def judgeCheckSum(data):
        check_sum = (data[-2] << 8) + data[-1]
        calc_check_sum = 0
        for i in range(0, len(data) - 2):
            calc_check_sum += data[i]
        calc_check_sum = calc_check_sum & 0xffff
        if check_sum != calc_check_sum:
            print('judgeCheckSum is error:', check_sum, calc_check_sum)
            print('judgeCheckSum is error:', ['{:02x}'.format(i) for i in data])
            return False
        return True

    @staticmethod
    def getBasesAddres(data):
        # print("spi read data:", ['{:02x}'.format(i) for i in data])
        address = data[-16:-14]
        # print('getBasesAddres:{:02x},{:02x}'.format(address[0], address[1]))
        return address[1]

    def run(self):
        spi_data = []
        while True:
            spi_data += self.spi_dev.readbytes(256)
            # print("spi read data:", ['{:02x}'.format(i) for i in spi_data])
            while len(spi_data) > 6:
                # 判断包头是否存在
                if spi_data[0:3] == [0xf8, 0xf4, 0xf2]:
                    pack_len = self.getLength(spi_data)
                    if pack_len > len(spi_data):
                        spi_data += self.spi_dev.readbytes(pack_len - len(spi_data))
                        continue

                    optic_data = spi_data[0:pack_len]

                    if self.judgeCheckSum(optic_data) is False:
                        for i in range(0, pack_len):
                            spi_data.pop(0)
                        continue

                    if self.getType(spi_data) != 0x00:  # 判断是否是光帧
                        for i in range(0, pack_len):
                            spi_data.pop(0)
                        continue

                    seq = self.getSeq(optic_data)
                    diff_seq = seq - self.old_seq
                    self.old_seq = seq

                    ts = self.getTs(optic_data)
                    diff_ts = ts - self.old_ts
                    self.old_ts = ts

                    bases_address = self.getBasesAddres(optic_data)

                    print('getBasesAddres {:02x}'.format(bases_address), 'ts:', ts, 'diff_ts:',
                          diff_ts, 'seq:', seq, 'diff_seq:', diff_seq)

                    if bases_address != self.bases_address_list[self.cur_address_index]:
                        if diff_seq != 1 or diff_ts > 40:
                            print('采集卡。。。丢帧')
                            for index in range(self.cur_address_index, self.bases_address_list.index(bases_address)):
                                self.bases_address_dict[self.bases_address_list[index]] = 1
                        else:
                            # 判断地址是否在列表中
                            if bases_address not in self.bases_address_list:
                                self.bases_address_list.insert(self.cur_address_index, bases_address)
                                BasesLog.mlogger.warn('有新的基站插入%f: %d', time.time(), bases_address)
                            else:
                                BasesLog.mlogger.warn('本次基站发光不一致%f: %d', time.time(), bases_address)

                        self.cur_address_index = self.bases_address_list.index(bases_address)

                        # print(self.cur_address_index, self.bases_address_list, self.bases_address_list_len)

                    self.cur_address_index += 1
                    self.bases_address_dict[bases_address] = 1
                    if self.cur_address_index >= self.bases_address_list_len:
                        self.cur_address_index = 0
                        # 列表中移除未发光的基站
                        for key in list(self.bases_address_dict.keys()):
                            # print(key, value)
                            if self.bases_address_dict[key] == 0:
                                self.bases_address_dict.pop(key)
                                self.bases_address_list.remove(key)
                                self.bases_address_list_len = len(self.bases_address_list)
                                BasesLog.mlogger.warn('本轮该基站未发光 移除列表 %f: %d', time.time(), key)
                            else:
                                self.bases_address_dict[key] = 0

                    for i in range(0, pack_len):
                        spi_data.pop(0)

                else:
                    spi_data.pop(0)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Please enter second parameters for base station address.")
        exit(0)

    argv_list = sys.argv[1:]
    test = SpiReadData(argv_list)
    test.run()