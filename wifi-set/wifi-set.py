#!/usr/bin/python3
# -*- coding:utf-8 -*-

import sys,os

file_name = '/etc/wpa_supplicant/wpa_supplicant.conf'   # 'wpa.conf'
# file_name = 'wpa.conf'

file_head = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'\
        'update_config=1\n'\
        'country=GB\n'

wifi_org = 'lingtrack-ap'
psk_org = '123abcd123'

wifi_count_len = 10

'''
def get_args():
    tmp = sys.argv
    data = ''
    
    if len(tmp) > 1:
        del tmp[0]
        for i in tmp:
            data += i + ' '
    else:
        return None

    #print('cmd data:',data)

    if data != '':
        return data
    else:
        return None
'''


def chmod_file(file_name):
    cmd = 'sudo chmod 666 ' + file_name
    os.system(cmd)


def get_args():
    args = {}
    
    tmp = sys.argv
    
    if tmp is None:
        print('have not args')
        sys.exit()

    if len(tmp) != 3:
        print('args error')
        sys.exit()
     
    #print('args:',tmp)

    del(tmp[0])

    data = tmp
    ssid = ''
    psk = ''
    for i in data:
        tmp = 'wifi='
        if tmp in i:
            tmp = i.split(tmp)
            if len(tmp) >= 2:
                ssid = tmp[1].strip()
            #print('arg ssid:',ssid)
            
        tmp = 'password='
        if tmp in i:
            tmp = i.split(tmp)
            if len(tmp) >= 2:
                psk = tmp[1].strip()
            #print('arg psk:',psk)

    if ssid == '' or psk == '':
        print('args error')
        sys.exit()

    if ssid == wifi_org:
        print('args error')
        sys.exit()

    args['ssid'] = ssid
    args['psk'] = psk
    return args

        

def get_data():
    try:
        chmod_file(file_name)
        f = open(file_name,'r')
    except:
        return None

    data = f.read()

    f.close()
    
    #print('file:',data)
    #-- split '\n'
    data = data.split('\n')  # network
    
    #for i in data:
    #    print('data i:',i)
    return data


def pro_data(data):
    wifi = []
    
    #-- split ''
    data = [i for i in data if i is not '']
    #for i in data:
    #    print('data ii:',i)

    #-- split '\t'
    for i in data:
        if '\t' in i:
            i = i.split('\t')
            i = i[1]
        #print('data iii:',i)
    #--
    ssid = ''
    psk = ''
    pre = ''
    for i in data:
        tmp = 'psk='
        if tmp in i:
            psk = i.split('"') # tmp
            if len(psk) >= 2:
                psk = psk[1]
            else:
                continue

            tmp = 'ssid='
            if tmp in pre:
                ssid = pre.split('"') # tmp
                if len(ssid) >= 2:
                    ssid = ssid[1]
                else:
                    continue
                
                #print('ssid:',ssid)
                #print('psk:',psk)
                tmp = {}
                tmp['ssid'] = ssid
                tmp['psk'] = psk
                wifi.append(tmp)

        pre = i
    
    return wifi
            
            

def cal_data(args,data):
    default_wifi = {}
    default_wifi['ssid'] = wifi_org
    default_wifi['psk'] = psk_org
    
    '''
    print('cal_data data:') #
    for i in data:          #
        print(i)            #
    '''
    
    if default_wifi not in data:  # if data == []:
        data.insert(0,default_wifi)

    tmp = [i for i in data if i['ssid'] != args['ssid']]
    tmp.insert(1,args)

    data = tmp[0:wifi_count_len]

    '''
    print('cal_data tmp::')#
    for i in data:         #
        print(i)           #
    '''
        
    return data
    

def write_data(data):
    context = file_head + '\n'

    count = len(data)
    for i in data:
        tmp = 'network={' + '\n'
        tmp += '\t' + 'ssid="' + i['ssid'] + '"\n'
        tmp += '\t' + 'psk="' + i['psk'] + '"\n'
        tmp += '\t' + 'key_mgmt=WPA-PSK' + '\n'

        if i['ssid'] == wifi_org:
            pri = len(data)
        else:
            pri = count
            count = count - 1
            
        tmp += '\t' + 'priority=' + str(pri) + '\n'
            
        tmp += '}' + '\n'

        context += tmp + '\n'

    #print('context:',context)
    
    try:
        chmod_file(file_name)
        f = open(file_name,'w+')
        f.write(context)
        f.close()
    except:
        pass
    

if __name__ == '__main__':
    args = get_args()
    #print('ssid psk:',args)
    #print('---------')          
    #--
    data = get_data()
    data = pro_data(data)
    #print('data:',data)
    #--
    #print('------')
    data = cal_data(args,data)
    #print('result:',data)
    #--
    write_data(data)

    







    
