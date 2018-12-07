#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

from __future__ import print_function

from __future__ import absolute_import
 
import zmq
 
if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    #socket.setsockopt(zmq.SUBSCRIBE, '')
    # Python3 Note: Use the below line and comment
    # the above line out 
    socket.setsockopt_string(zmq.SUBSCRIBE, 'Imu')

    socket.connect("tcp://127.0.0.1:6100")

	
    try:
        while True:
            topic, msg = socket.recv_multipart()
            print('   Topic: %s, msg:%s' % (str(topic), msg))
			# print('%x' % msg)
    except KeyboardInterrupt:
        pass
    print("Done.")
	
    # while True:
        # #msg = socket.recv()
        # # Python3 Note: Use the below line and comment
        # # the above line out        
        # msg = socket.recv_string()
        # print(msg)