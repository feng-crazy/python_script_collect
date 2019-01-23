#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/14 17:08
# @Author  : hedengfeng
# @Site    : 
# @File    : serial_read_data.py
# @Software: terminal
# @description: 


import serial
import wiringpi
import time


class SerialReadData(object):
    def __init__(self):
        self.serial_dev = serial.Serial('/dev/ttyAMA0', 38400, timeout=0.5)

        wiringpi.wiringPiSetup()
        wiringpi.pinMode(6, 1)
        wiringpi.digitalWrite(6, 0)

        wiringpi.pinMode(8, 1)
        wiringpi.digitalWrite(8, 0)

    @staticmethod
    def getType(data):
        return data[1]

    @staticmethod
    def getLength(data):
        return data[2]

    @staticmethod
    def judgeCheckSum(data):
        # print('judgeCheckSum:', ['{:02x}'.format(i) for i in data], len(data))
        check_sum = data[-2]
        calc_check_sum = 0
        for i in range(2, 3 + data[2]):
            calc_check_sum += data[i]
        calc_check_sum = calc_check_sum & 0xff
        if check_sum != calc_check_sum:
            # print('check_sum:', check_sum, 'calc_check_sum:', calc_check_sum)
            return False
        return True

    @staticmethod
    def getBasesAddres(data):
        return data[4]

    def run(self):
        bases_data = []
        optic_ctrl_flag = False
        while True:
            if self.serial_dev.inWaiting() < 5:
                time.sleep(0.001)
                continue
            serial_data = self.serial_dev.read(8)
            # print('serial_data:', serial_data, len(serial_data))
            bases_data += list(serial_data)
            print('bases_data:', ['{:02x}'.format(i) for i in bases_data], len(bases_data))

            while len(bases_data) > 3:
                # 判断包头是否存在
                if bases_data[0] == 0xaa:
                    if self.getType(bases_data) != 0xf6:  # 判断是否是发光控制帧
                        print('data is not optic control data')
                        optic_ctrl_flag = False
                    else:
                        optic_ctrl_flag = True

                    pack_len = self.getLength(bases_data)
                    data_len = pack_len + 5
                    if data_len > len(bases_data):
                        bases_data += self.serial_dev.read(data_len - len(bases_data))
                        print('bases_data:', ['{:02x}'.format(i) for i in bases_data], len(bases_data))

                    if self.judgeCheckSum(bases_data[0:data_len]) is False:
                        print('check sum is error')
                        for i in range(0, data_len):
                            bases_data.pop(0)
                        continue

                    if optic_ctrl_flag is True:
                        bases_address = self.getBasesAddres(bases_data)
                        print('getBasesAddres {:02x}'.format(bases_address))

                    for i in range(0, data_len):
                        bases_data.pop(0)

                else:
                    bases_data.pop(0)


if __name__ == '__main__':
    test = SerialReadData()
    test.run()