#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

from __future__ import print_function

from __future__ import absolute_import

from configobj import ConfigObj

def main():
    config = ConfigObj('config.ini',encoding='UTF8')
    print(config['LT_HUB_ADDR'])
    print(config['BS_IDS'])
    print(config['BS_INGROUP_ADDRS'])
    print(config['BS_LOCATIONS'])
    config['LT_HUB_ADDR'] = '192.168.0.112'
    config.write()
    print(config['LT_HUB_ADDR'])

if __name__ == '__main__':
    main()
    
#     import configparser    
#     cf = configparser.ConfigParser()
#     cf.read('config.ini')
#     # 返回所有的section
# #     s = cf.sections()
# #     print ('section:', s)
# #     
# #     o = cf.options("LT_CONFIG")
# #     print ('BS_IDS:', o)
# #     
# #     v = cf.items("LT_CONFIG")
# #     print ('LT_CONFIG:', v)
#     
#     bs_ids = cf.get("LT_CONFIG", "BS_IDS")    
#     bs_freqs = cf.get("LT_CONFIG", "BS_FREQS")    
#     bs_ingroup_addrs = cf.get("LT_CONFIG", "BS_INGROUP_ADDRS")    
#     bs_locations = cf.get("LT_CONFIG", "BS_LOCATIONS")  
#     #bs_start_angles = cf.get("BS_START_ANGLES",default=None)
#     
#     print("bs_ids",bs_ids)
#     print("bs_freqs",bs_freqs)
#     print("bs_ingroup_addrs",bs_ingroup_addrs)
#     print("bs_locations",bs_locations)
#     #print("bs_start_angles",bs_start_angles)