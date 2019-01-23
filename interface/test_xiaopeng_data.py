#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/7 10:54
# @Author  : hedengfeng
# @Site    : 
# @File    : test_xiaopeng_data.py
# @Software: terminal
# @description:
import sys


class CanDataTest(object):
    def __init__(self, data_list):
        self.loc_data_list = [int(i, 16) for i in data_list]
        print(self.loc_data_list)

    def parse(self):
        if self.judge_check_sum() is False:
            print('check sum is false')
            return

        loctype = ((self.loc_data_list[3] & 0xC0) >> 6)
        sensor_id = ((self.loc_data_list[3] & 0x30) >> 4 )
        heading = (self.loc_data_list[2] & 0xFF) + ((self.loc_data_list[3] << 8) & 0x0F00)
        loc_x = (self.loc_data_list[4] & 0x00FF) + ((self.loc_data_list[5] << 8) & 0xFF00) - 30000
        loc_y = (self.loc_data_list[6] & 0x00FF) + ((self.loc_data_list[7] << 8) & 0xFF00) - 30000
        print('loctype:', loctype, 'sensor_id:', sensor_id, 'heading:', heading, 'loc_x:', loc_x, 'loc_y:', loc_y)

    def judge_check_sum(self):
        check_sum = (self.loc_data_list[0] & 0x00FF) + ((self.loc_data_list[1] << 8) & 0xFF00)
        # print(check_sum)

        calc_check_sum = 0
        for i in range(2, 8, 2):
            calc_check_sum += (self.loc_data_list[i] & 0x00FF) + ((self.loc_data_list[i+1] << 8) & 0xFF00)

        calc_check_sum = (calc_check_sum >> 16) + (calc_check_sum & 0xFFFF)
        calc_check_sum += calc_check_sum >> 16
        calc_check_sum = ~calc_check_sum & 0x0000FFFF
        print('calc_check_sum:{:04x}'.format(calc_check_sum))
        if check_sum == calc_check_sum:
            return True
        else:
            print('check_sum:{0:02X},calc_check_sum:{1:02X}'.format(check_sum, calc_check_sum))
            return False


if __name__ == '__main__':
    if len(sys.argv) < 8:
        print("Please enter second parameters for data.")
        exit(0)

    argv_list = sys.argv[1:]
    test = CanDataTest(argv_list)
    test.parse()