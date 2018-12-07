#!/usr/bin/env python2

import os
from wifi import Cell, Scheme
import subprocess
import time




wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
sudo_mode = "sudo "


def wifi_connect(ssid, psk):
    # write wifi config to file
    f = open('wifi.conf', 'w')
    f.write('country=GB\n')
    f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
    f.write('update_config=1\n')
    f.write('\n')
    f.write('network={\n')
    f.write('    ssid="' + ssid + '"\n')
    f.write('    psk="' + psk + '"\n')
    f.write('}\n')
    f.close()

    cmd = 'mv wifi.conf ' + wpa_supplicant_conf
    cmd_result = ""
    cmd_result = os.system(cmd)
    print cmd + " - " + str(cmd_result)


    # restart wifi adapter
    cmd = sudo_mode + 'ifdown wlan0'
    cmd_result = os.system(cmd)
    print cmd + " - " + str(cmd_result)

    time.sleep(2)

    cmd = sudo_mode + 'ifup wlan0'
    cmd_result = os.system(cmd)
    print cmd + " - " + str(cmd_result)

    time.sleep(10)

    cmd = 'iwconfig wlan0'
    cmd_result = os.system(cmd)
    print cmd + " - " + str(cmd_result)

    cmd = 'ifconfig wlan0'
    cmd_result = os.system(cmd)
    print cmd + " - " + str(cmd_result)

    p = subprocess.Popen(['ifconfig', 'wlan0'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    out, err = p.communicate()

    ip_address = "<Not Set>"

    for l in out.split('\n'):
        if l.strip().startswith("inet addr:"):
            ip_address = l.strip().split(' ')[1].split(':')[1]

    return ip_address



def ssid_discovered():
    Cells = Cell.all('wlan0')

    wifi_info = 'Found ssid : \n'

    for current in range(len(Cells)):
        wifi_info +=  Cells[current].ssid + "\n"


    wifi_info+="!"

    print wifi_info
    return wifi_info

def main():
    ssid_discovered()
    
if __name__ == '__main__':
    main()
# else:
#     create_recv_thread()            
