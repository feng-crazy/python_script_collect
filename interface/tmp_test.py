#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/22 11:17
# @Author  : hedengfeng
# @Site    : 
# @File    : tmp_test.py
# @Software: terminal
# @description: 


def judge_check_sum(loc_data_list):
    check_sum = (loc_data_list[0] & 0x00FF) + ((loc_data_list[1] << 8) & 0xFF00)
    # print(check_sum)

    calc_check_sum = 0
    for i in range(2, 8, 2):
        calc_check_sum += (loc_data_list[i] & 0x00FF) + ((loc_data_list[i + 1] << 8) & 0xFF00)

    calc_check_sum = (calc_check_sum >> 16) + (calc_check_sum & 0xFFFF)
    calc_check_sum += calc_check_sum >> 16
    calc_check_sum = ~calc_check_sum & 0x0000FFFF
    print('calc_check_sum:{:04x}'.format(calc_check_sum))
    if check_sum == calc_check_sum:
        return True
    else:
        print('check_sum:{0:02X},calc_check_sum:{1:02X}'.format(check_sum, calc_check_sum))
        return False


data_list = [0x9f, 0x85, 0xff, 0x8f, 0x30, 0x75, 0x30, 0x75]

judge_check_sum(data_list)