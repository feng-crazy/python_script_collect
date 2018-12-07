#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

from __future__ import print_function

from __future__ import absolute_import

import subprocess
from sys import stdout


def main():
    print('start....')
    #TerminalCheck.py -a 192.168.0.109 -p 0 0
#     proc = subprocess.Popen('python3 TerminalCheck.py -a 192.168.0.109 -p 0 0'
#                             ,stdin=subprocess.PIPE, stdout=subprocess.PIPE,
#                              stderr=subprocess.PIPE,shell=True)
    
#     proc = subprocess.Popen('python3 TerminalCheck.py -a 192.168.0.109 -p 0 0'
#                         ,shell=True)
#     print('haha')
#     while True:
#         output, usrerror = proc.communicate(timeout=2)
#         print(output)
                
    
    proc1 = subprocess.Popen('python3 call_sub.py'
                            ,stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,shell=True)
    exe_result1 = proc1.stdout.read()
    print("mdsb:" + exe_result1.decode())
    
    now_md5sum = subprocess.check_output("md5sum config.txt",shell=True)
    print("now_md5sum:" + now_md5sum.decode())
    
if __name__ == '__main__':
    main()