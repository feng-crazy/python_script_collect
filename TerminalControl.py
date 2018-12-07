#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

# 文件名：    TerminalControl
# 生成日期：    2018.1.1
# 作者：        何登锋
# 功能说明：
#     终端控制程序，扫描当前网络中的终端，修改终端的配置文件，重启终端

from __future__ import print_function

from __future__ import absolute_import

import pexpect
import getpass

import socket, sys
from socket import *
import time, threading
import sys
import signal
import subprocess
import os
import argparse

SCAN = 'scan'
CONFIG = 'config'
AUTO = 'auto'
MANUAL = 'manual'
password = 'hdf654321'

HOST = ''
PORT = 1500
BUFSIZE = 1024

ADDR = (HOST, PORT)
dest = ('<broadcast>', PORT)

udpCliSock = socket(AF_INET, SOCK_DGRAM)
udpCliSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

AddrList = []


# 作者：何登锋，2018.1.1
# 功能描述：通过SCP发送配置文件给终端
# 参数说明：addr_list要发送的终端地址
# 返回值：无
def scp_config(addr_list):
    for addr_s in addr_list:
        # 发送命令
        scp_cmd = 'scp config.txt ' + 'pi@' + addr_s + ':/home/LT/bin/'
        print(scp_cmd)
        # 执行命令
        child = pexpect.spawn(scp_cmd, timeout=10)
        # 设置命令的预期结果
        index = child.expect(['password', 'yes', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print('scp_config expect:index=%d' % index)
            # 如果是password 就输出预期密码
            child.sendline(password)
            # 这句话真的很神奇，如果不加这句话，程序会执行，但是不执行copy，我无法解释
            child.read()
        elif index == 1:
            # 返回的预期结果是yes
            print('index=%d' % index)
            child.sendline('yes')
            child.expect('password:', timeout=30)
            child.sendline(password)
            # 这句话真的很神奇，如果不加这句话，程序会执行，但是不执行copy，我无法解释
            child.read()
        elif index == 2:
            # 超出预期
            print('pexpect.EOF')
        else:
            print('pexpect.TIMEOUT')


# 作者：何登锋，2018.1.1
# 功能描述：重启终端
# 参数说明：addr_list要重启的终端地址
# 返回值：无			
def restart_term(addr_list):
    # 只要config.txt有变动，终端就会自动重启，因此只传入一个空格
    remote_cmd = ' echo ' + '\' \'' + '>> /home/LT/bin/config.txt'
    for addr_s in addr_list:
        restart_cmd = 'ssh ' + 'pi@' + addr_s + remote_cmd
        print(restart_cmd)
        child = pexpect.spawn(restart_cmd, timeout=10)
        index = child.expect(['password', 'yes', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print('restart_term expect:index=%d' % index)
            child.sendline(password)
            # 这句话真的很神奇，如果不加这句话，程序会执行，但是不执行copy，我无法解释
            child.read()
        elif index == 1:
            print('index=%d' % index)
            child.sendline('yes')
            child.expect('password:', timeout=30)
            child.sendline(password)
            # 这句话真的很神奇，如果不加这句话，程序会执行，但是不执行copy，我无法解释
            child.read()
        elif index == 2:
            print('pexpect.EOF')
        else:
            print('pexpect.TIMEOUT')


# 作者：何登锋，2018.1.1
# 功能描述：扫描局域网中的终端
# 参数说明：SCAN 扫描命令
# 返回值：无				
def scan_lt_hub(data=SCAN):
    AddrList.clear()
    udpCliSock.sendto(data.encode(), dest)


# 作者：何登锋，2018.1.1
# 功能描述：运行手动线程，该线程的主要作用是人机交互的命令行界面控制
# 参数说明：无
# 返回值：无				
def run_manual_thread():
    while True:
        data = input('(please input scan,config,restart or exit)>')
        cmd_list = data.split();
        cmd_len = len(cmd_list)
        print(cmd_list, cmd_len)
        if cmd_len < 1:
            print('input arg not enough,please input scan,config,restart or exit!')
            continue

        if cmd_list[0] == SCAN:
            scan_lt_hub(data)

        elif cmd_list[0] == CONFIG:
            if cmd_len == 1:
                scp_config(AddrList)
            elif cmd_list[1] == 'all':
                scp_config(AddrList)
            else:
                input_adrr = []
                for i in range(1, cmd_len):
                    input_adrr.append(cmd_list[i])
                    print(cmd_list[i])
                scp_config(input_adrr)

        elif cmd_list[0] == 'restart':
            if cmd_len == 1:
                restart_term(AddrList)
            elif cmd_list[1] == 'all':
                restart_term(AddrList)
            else:
                input_adrr = []
                for i in range(1, cmd_len):
                    input_adrr.append(cmd_list[i])
                restart_term(input_adrr)

        elif cmd_list[0] == 'exit':
            udpCliSock.close()
            sys.exit()
            break
        else:
            print('please input scan,config,restart or exit!')
        time.sleep(1)


# 作者：何登锋，2018.1.1
# 功能描述：创建手动线程，该线程的主要作用是人机交互的命令行界面控制
# 参数说明：无
# 返回值：无	
def create_manual_thread():
    manual_thread = threading.Thread(target=run_manual_thread, name='ManualThread')
    manual_thread.setDaemon(True)
    manual_thread.start()


# 作者：何登锋，2018.1.1
# 功能描述：运行自动线程，该线程的主要作用是判断配置是否改变如果改变，发送给当前的每一个终端
# 参数说明：无
# 返回值：无		
def run_auto_thread():
    old_md5sum = subprocess.check_output("md5sum config.txt", shell=True)
    # print("old_md5sum: " + old_md5sum.decode())
    while True:
        now_md5sum = subprocess.check_output("md5sum config.txt", shell=True)
        # print("now_md5sum:" + now_md5sum.decode())
        if now_md5sum != old_md5sum:
            print("config.txt file is changed!")
            scan_lt_hub(SCAN)
            time.sleep(2)
            scp_config()
            old_md5sum = now_md5sum
        time.sleep(2)


# 作者：何登锋，2018.1.1
# 功能描述：创建自动线程，该线程的主要作用是判断配置是否改变如果改变，发送给当前的每一个终端
# 参数说明：无
# 返回值：无				
def create_auto_thread():
    auto_thread = threading.Thread(target=run_auto_thread, name='AutoThread')
    auto_thread.setDaemon(True)
    auto_thread.start()


# 作者：何登锋，2018.1.1
# 功能描述：运行接受线程，该线程的主要作用是接收网络每一个终端的UDP返回信息
# 参数说明：无
# 返回值：无		
def run_recv_thread():
    while True:
        data, ADDR = udpCliSock.recvfrom(BUFSIZE)
        if not data:
            break
        print('scan get data: ', data.decode())
        print('scan get addr: ', ADDR)
        AddrList.append(ADDR[0])


# 作者：何登锋，2018.1.1
# 功能描述：创建接受线程，该线程的主要作用是接收网络每一个终端的UDP返回信息
# 参数说明：无
# 返回值：无	
def create_recv_thread():
    recv_thread = threading.Thread(target=run_recv_thread, name='RecvThread')
    recv_thread.setDaemon(True)
    recv_thread.start()


# 作者：何登锋，2018.1.1
# 功能描述：信号量处理函数
# 参数说明：无
# 返回值：无	
def quit(signal_num, frame):
    print("you stop the threading")
    udpCliSock.close()
    sys.exit()


def main():
    try:
        signal.signal(signal.SIGINT, quit)
        signal.signal(signal.SIGTERM, quit)
        parser = argparse.ArgumentParser(description="Start terminal control, manual or automatic.")
        parser.add_argument('operation_opt', type=str, default='manual', choices=['auto', 'manual'],
                            help='choose manual or auto default auto')
        args = parser.parse_args()
        print(args.operation_opt)

        if (args.operation_opt == MANUAL):
            create_manual_thread()

        if (args.operation_opt == AUTO):
            create_auto_thread()

        create_recv_thread()
        while True:
            pass
    except Exception as error:
        print(str(error))
    print('%s thread end!' % (time.ctime()))
    udpCliSock.close()


if __name__ == '__main__':
    main()
# else:
# 	create_recv_thread()
