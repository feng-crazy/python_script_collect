#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/10/15 11:06
# @Author  : hedengfeng
# @Site    : 
# @File    : pusle_recv_test.py
# @Software: EAI_test
# @description: 

import zmq


if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    socket.setsockopt_string(zmq.SUBSCRIBE, 'eai')

    socket.connect("tcp://127.0.0.1:6105")

    try:
        while True:
            topic, msg = socket.recv_multipart()
            print('   Topic: %s, msg:%s' % (str(topic), msg))
        # print('%x' % msg)
    except KeyboardInterrupt:
        pass
    print("Done.")