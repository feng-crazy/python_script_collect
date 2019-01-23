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


class SpiReadData(object):
    def __init__(self):

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
        address = data[-15:-14]
        # print('getBasesAddres:{:02x},{:02x}'.format(address[0], address[1]))
        return address[0]

    def run(self):
        spi_data = []
        while True:
            spi_data += self.spi_dev.readbytes(128)
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

                    if self.getType(optic_data) != 0x00:  # 判断是否是光帧
                        for i in range(0, pack_len):
                            spi_data.pop(0)
                        continue

                    ts = self.getTs(optic_data)
                    diff_ts = ts - self.old_ts
                    self.old_ts = ts

                    if diff_ts > 40:
                        print('采集卡。。。丢帧 ts:', ts, 'diff_ts:', diff_ts)

                    for i in range(0, pack_len):
                        spi_data.pop(0)

                else:
                    spi_data.pop(0)


if __name__ == '__main__':

    test = SpiReadData()
    test.run()