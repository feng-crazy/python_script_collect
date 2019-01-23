#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/8/27 9:15
# @Author  : hedengfeng
# @Site    : 
# @File    : scp_terminal.py
# @Software: terminal
# @description:
import re
import pexpect
# import pexpect
import sys
import paramiko


password = 'hdf654321'


def cp_terminal(ip_addr):

    # 发送命令
    scp_cmd = 'scp terminal.py DataHub LocEngine' + ' pi@' + ip_addr + ':/home/LT/Bin/'
    # scp_cmd = 'scp terminal.py' + ' pi@' + ip_addr + ':/home/LT/Bin/'
    print(scp_cmd)

    # 执行命令
    child = pexpect.spawn(scp_cmd, timeout=10)
    # 设置命令的预期结果
    index = child.expect(['password', 'yes', pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print('scp_config expect:index=%d' % index)
        # 如果是password 就输出预期密码
        child.sendline(password)
        # child 是一个子进程，scp的过程需要时间，父进程不能太快结束，
        # 所以用read来阻塞父进程，如果不read程序会执行，但是不执行copy
        child.read()
    elif index == 1:
        # 返回的预期结果是yes
        print('index=%d' % index)
        child.sendline('yes')
        child.expect('password:', timeout=30)
        child.sendline(password)
        # child 是一个子进程，scp的过程需要时间，父进程不能太快结束，
        # 所以用read来阻塞父进程，如果不read程序会执行，但是不执行copy
        child.read()
    elif index == 2:
        # 超出预期
        print('pexpect.EOF')
    else:
        print('pexpect.TIMEOUT')


def cp_dir(ip_addr):
    # 发送命令
    scp_cmd = 'scp -r eventbus utility ' + 'pi@' + ip_addr + ':/home/LT/Bin/'
    print(scp_cmd)

    # 执行命令
    child = pexpect.spawn(scp_cmd, timeout=10)
    # 设置命令的预期结果
    index = child.expect(['password', 'yes', pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print('scp_config expect:index=%d' % index)
        # 如果是password 就输出预期密码
        child.sendline(password)
        # child 是一个子进程，scp的过程需要时间，父进程不能太快结束，
        # 所以用read来阻塞父进程，如果不read程序会执行，但是不执行copy
        child.read()
    elif index == 1:
        # 返回的预期结果是yes
        print('index=%d' % index)
        child.sendline('yes')
        child.expect('password:', timeout=30)
        child.sendline(password)
        # child 是一个子进程，scp的过程需要时间，父进程不能太快结束，
        # 所以用read来阻塞父进程，如果不read程序会执行，但是不执行copy
        child.read()
    elif index == 2:
        # 超出预期
        print('pexpect.EOF')
    else:
        print('pexpect.TIMEOUT')


def connect_ssh(ip_addr):
    if judge_ip_addr(ip_addr) is not True:
        return

    ssh = paramiko.SSHClient()

    # 这行代码的作用是允许连接不在know_hosts文件中的主机。
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_addr, username='pi', password='hdf654321')

    stdin, stdout, stderr = ssh.exec_command('sh /home/LT/Bin/lt kill')
    print(stdout.readlines())


def scp_file(addr_s):
    ssh = paramiko.SSHClient()

    # 这行代码的作用是允许连接不在know_hosts文件中的主机。
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(addr_s, username='pi', password='hdf654321')

    stdin, stdout, stderr = ssh.exec_command('sh /home/LT/Bin/lt kill')
    print(stdout.readlines())

    cp_terminal(addr_s)
    cp_dir(addr_s)

    stdin, stdout, stderr = ssh.exec_command('sh /home/LT/Bin/lt start')
    print(stdout.readlines())

    ssh.close()


def judge_ip_addr(ip_str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip_str):
        return True
    else:
        return False


def main():
    print(type(sys.argv))
    ip_addr_list = sys.argv[1:]
    print('ip_addr_list:', ip_addr_list)
    for addr_s in ip_addr_list:
        if not judge_ip_addr(addr_s):
            print('not is ip_addr:', addr_s)
            continue
        scp_file(addr_s)

    while True:
        data = input('please input scp id addr:')
        if data == 'q':
            break
        elif judge_ip_addr(data):
            scp_file(data)


if __name__ == '__main__':
    main()