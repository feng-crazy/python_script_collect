#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

# 文件名：    TerminalCheck
# 生成日期：    2018.1.1
# 作者：        何登锋
# 功能说明：
#     终端检验程序，检验某一个终端返回的结果，与实际的比较是否通过


from __future__ import print_function

from __future__ import absolute_import

import time, threading

import zmq

import argparse
import scanf
import math

ctx = zmq.Context()
socket = ctx.socket(zmq.SUB)
pos_x = 0
pos_y = 0


# 作者：何登锋，2018.1.1
# 功能描述：验证位置是否正确
# 参数说明：终端x坐标 终端y坐标 check_postion校验的位置
# 返回值：验证结果
def verify_postion(x, y, check_postion):
    diff_x = math.fabs(x - check_postion[0])
    diff_y = math.fabs(y - check_postion[1])

    # 	print('x:{0},y:{1},check_postion:{2}'.format(x,y,check_postion))
    # 	print('diff:{0},{1}'.format(x-check_postion[0],y-check_postion[1]))
    # 	print('diff_x:%f' %diff_x)
    # 	print('diff_y:%f' %diff_y)

    if (diff_x > 10.000 or diff_y > 10.000):
        print("postion verify failure")
        return False
    return True


# 作者：何登锋，2018.1.1
# 功能描述：验证频率是否正确，判断是否有丢帧的情况
# 参数说明：ts_同步时间， sensorId_传感器号，old_ts上一次的同步时间
# 返回值：验证结果	
def verify_ts(ts_, sensorId_, old_ts):
    diff_ts = ts_ - old_ts[sensorId_]
    old_ts[sensorId_] = ts_
    if (diff_ts > 250 and old_ts[sensorId_] != 0):
        print("数据存在丢帧 sensorId_ = ", sensorId_)
        return True, old_ts
    return True, old_ts


# 作者：何登锋，2018.1.1
# 功能描述：创建zmq的连接
# 参数说明：connect_addr连接的地址
# 返回值：无			
def create_zmq_connect(connect_addr):
    connect_to = connect_addr
    socket.setsockopt_string(zmq.SUBSCRIBE, 'Loc')
    connect_cmd = 'tcp://' + connect_to + ':6102'
    print('create_zmq_connect:' + connect_cmd)
    socket.connect(connect_cmd)


# 作者：何登锋，2018.1.1
# 功能描述：处理综合滤波位置的数据
# 参数说明：topic zmq接受消息类型,msg zmq收到的消息数据
# 返回值：综合滤波位置			
def handle_pos_data(topic, msg):
    if (str(topic)).find('robot filtered') < 0:
        # 		print('no find robot filtered Topic is: %s,'%topic)
        return -1, -1
    # 	print('   Topic: %s, msg:%s' % (str(topic), str(msg)))
    pos_x, pos_y, z, heading_, gamma_, theta_, ts_, bsIdx_, sensorId_ = scanf.scanf("%f %f %f %f %f %f %d %d %d",
                                                                                    str(msg));
    # 	print(pos_x, pos_y, z, heading_, gamma_, theta_, ts_, bsIdx_, sensorId_)
    # &x, &y, &z, &heading_, &gamma_, &theta_, &ts_, &bsIdx, &sensorId
    # 	print('x:%f y:%f'%(pos_x,pos_y))
    return pos_x, pos_y


# 作者：何登锋，2018.1.1
# 功能描述：处理同步时间数据
# 参数说明：topic zmq接受消息类型,msg zmq收到的消息数据
# 返回值：同步时间和传感器ID
def handle_ts_data(topic, msg):
    if (str(topic)).find('Loc raw') < 0:
        # 		print('no find robot filtered Topic is: %s,'%topic)
        return -1, -1
    # 	print('   Topic: %s, msg:%s' % (str(topic), str(msg)))
    pos_x, pos_y, z, heading_, gamma_, theta_, ts_, bsIdx_, sensorId_ = scanf.scanf("%f %f %f %f %f %f %d %d %d",
                                                                                    str(msg));
    return ts_, sensorId_


# 作者：何登锋，2018.1.1
# 功能描述：接受终端返回的数据，处理数据，验证数据
# 参数说明：connect_addr 终端的连接地址,check_postion校验的位置
# 返回值：成功返回tre，失败返回false
def verify_terminal(connect_addr, check_postion):
    create_zmq_connect(connect_addr)

    verify_result = False
    verify_success_cnt = 0
    old_ts = [0, 0]

    # 验证10,10次中有一次失败，即验证不通过
    for i in range(0, 10):
        topic, msg = socket.recv_multipart()
        x, y = handle_pos_data(topic, msg)
        if x != -1 and y != -1:
            print('recv_pos_data: x:%f y:%f' % (x, y))
            verify_ret = verify_postion(x, y, check_postion)
            if (verify_ret):
                verify_success_cnt += 1
            else:
                return False

        ts_, sensorId_ = handle_ts_data(topic, msg)
        if ts_ != -1 and sensorId_ != -1:
            verify_ret, old_ts = verify_ts(ts_, sensorId_, old_ts)
            if (verify_ret):
                verify_success_cnt += 1
            else:
                return False

    if (verify_success_cnt > 1):
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser(description="The location where the terminal address check terminal is placed.")

    parser.add_argument('-a', '--addr', type=str, default='192.168.0.112', help='connect address')
    parser.add_argument('-p', '--postion', nargs=2, type=float, default=0.0, help='verify postion ')
    # parser.set_defaults(args.addr='192.168.0.109', args.postion[0]=2, args.postion[1]=3)

    args = parser.parse_args()

    print(args.addr)

    if args.postion:
        print(args.postion[0], args.postion[1])

    verify_result = verify_terminal(args.addr, args.postion)
    print('verify_result:{0}'.format(verify_result))

    print("Done.")


# 	a,b,c = scanf.scanf("%o %x %d", "0123 0x123 123")
# 	print(a,b,c)


if __name__ == '__main__':
    main()
