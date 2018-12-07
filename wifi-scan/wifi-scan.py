#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os,sys,time

######################################################################
update_wifi = ('@&n','@&p')
#update_wifi = ('*+&%n','*+&%p')
# update_wifi = ('root-n','root-p')
psk = '11111111'

wifi_data = {'ssid':'','psk':''}

######################################################################
'''
add_wifi     = ('*+&#n%','*p&#@')
del_wifi     = ('*-&#d%','*p&#n')
update_wifi  = ('*+&#u%','*p&#@')
del_all_wifi = '-cc-#/#-*{*-&}&-%|%-@!@'
'''
######################################################################



################################ pro .conf file #########################################################
######################################################################
file_name = '/etc/wpa_supplicant/wpa_supplicant.conf'   # 'wpa.conf'
# file_name = 'wpa.conf'

file_tmp = './wifi-tmp.conf'

file_head = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'\
        'update_config=1\n'\
        'country=GB\n'

wifi_org = 'lingtrack-ap'
psk_org  = '123abcd123'

wifi_count_len = 10
######################################################################


def chmod_file(file_name):
    cmd = 'sudo chmod 666 ' + file_name
    os.system(cmd)

        
# read .conf file and return str 
def get_data(file_name):
    try:
        chmod_file(file_name)
        f = open(file_name,'r')
    except:
        return None

    data = f.read()
    f.close()
    
    data = data.split('\n')  # network 
    return data


# return [] of value is {'ssid':*,'psk':*}
def pro_data(data):
    wifi = []

    if data is None:
        return None
    
    #-- split ''
    data = [i.strip() for i in data if i is not '']
        
    '''
    #-- split '\t'
    for i in data:
        if '\t' in i:
            i = i.split('\t')
            i = i[1]
        print('data iii:',i) ###
    '''
    
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
            


'''            
# input:{},[]
def cal_data(ssid_data,data):
    default_wifi = {}
    default_wifi['ssid'] = wifi_org
    default_wifi['psk'] = psk_org
    
    print('cal_data data:') #
    for i in data:          #
        print(i)            #
    
    if default_wifi not in data:  # if data == []:
        data.insert(0,default_wifi)

    tmp = [i for i in data if i['ssid'] != args['ssid']]
    tmp.insert(1,ssid_data)

    data = tmp[0:wifi_count_len]

    print('cal_data tmp::')#
    for i in data:         #
        print(i)           #
        
    return data
'''    


# write .conf file
# input [] of value is {}
def write_data(data):
    global file_name
    global file_tmp
    
    if data is None or data == []:
        return
    
    context = file_head + '\n'
    count = len(data)
    for i in data:
        tmp = 'network={' + '\n'
        tmp += '\t' + 'ssid="' + i['ssid'] + '"\n'      # ssid
        tmp += '\t' + 'psk="' + i['psk'] + '"\n'        # psk
        tmp += '\t' + 'key_mgmt=WPA-PSK' + '\n'         # key_mgmt

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
        return

    #-----------
    #print('DO WIFI START ----------------------------------------') ###
    os.system('sudo ifconfig wlan0 down')
    time.sleep(1)
    #
    restart_wifi = ('sudo ifdown wlan0','sudo ifup wlan0')
    os.system(restart_wifi[0] + ' > ' + file_tmp)
    # time.sleep(6)
    os.system(restart_wifi[1] + ' > ' + file_tmp)
    # time.sleep(8)
    #
    os.system('sudo ifconfig wlan0 up')
    time.sleep(1)
    #print('DO WIFI FINISH ---------------------------------------') ###
    
    # os.system('sudo reboot')
    

################################ scan SSID #############################################################
def scan_wlan(file):
    cmd = 'iwlist wlan0 scan | grep ESSID'
    cmd += '> ' + file
    os.system(cmd)


# return:[] of ssid name
def get_essid(file):
    data = ''
    try:
        fd = open(file,'r')
    except:
        return None

    try:
        data = fd.read()
    except:
        fd.close()
        return None
    fd.close()

    data = data.split('\n')
    data = [i.strip() for i in data if i is not '']

    result = []
    for i,j in enumerate(data):
        if len(j) >= 7:
            result.append(j[7:-1])

    if result != []:
        return result
    else:
        return None

###########################################################################
####
# input:[],[]
def cal_data(result,data):
    global wifi_org     # lingtrack-ap
    global psk_org      # 123qwer123
    
    global update_wifi  # ('*+&%n','*+&%p')
    global psk          # 111111
    
    global wifi_data    # {'ssid':'','psk':''} 

    #print('------ cal_data -------') ###
    
    default_wifi = {}
    default_wifi['ssid'] = wifi_org
    default_wifi['psk'] = psk_org

    # from result get ssid or psk
    check_ssid = update_wifi[0]
    check_psk = update_wifi[1]

    result_wifi = []
    result_wifi.append(default_wifi)

    tmp_wifi = {}
    tmp = result[0]
    
    if tmp == 'ssid':
        #print(tmp) ###
        tmp = result[1].replace(check_ssid,'')
        if tmp != '' and tmp != wifi_org:
            if tmp != wifi_data['ssid']:
                # check name as ssid is exist
                for i in data:
                    if result[1] == i['ssid'] and i['psk'] == psk:
                        #print('ssid exist in .conf') ###
                        return
                
                tmp_wifi['ssid'] = result[1]
                tmp_wifi['psk'] = psk
                result_wifi.append(tmp_wifi)
                
                wifi_data['ssid'] = tmp   # if tmp != wifi_data['ssid']  ??
                wifi_data['psk'] = ''

                #print('tmp_wifi:',tmp_wifi)   ###
                #print('wifi_data:',wifi_data) ###
                
                if data is not None:
                    for i in data:
                        name = i['ssid']
                        if name != '':
                            if name != wifi_org and check_ssid not in name and check_psk not in name:
                                result_wifi.append(i)
                                break
                #--- write ---
                write_data(result_wifi)
                
                #print('result_wifi:')   ###
                #for i in result_wifi:   ###
                #    print(i)            ###
            else:
                #print('ssid exist') ###
                pass
            
    elif tmp == 'psk':
        #print(tmp) ###
        tmp = result[1].replace(check_psk,'')
        if tmp != '':
            # check password >= 8
            if len(tmp) < 8:
                #print('psk length < 8') ###
                return
        
            # check psk as ssid is exist
            for i in data:
                if result[1] == i['ssid'] and i['psk'] == psk:
                    #print('psk as ssid exist in .conf') ###
                    return
                    
            tmp_wifi['ssid'] = result[1]
            tmp_wifi['psk'] = psk
            result_wifi.append(tmp_wifi)
            #print('tmp_wifi:',tmp_wifi) ###

            # find ssid in data            
            if wifi_data['ssid'] != '':
                if wifi_data['ssid'] != wifi_org:
                    wifi_data['psk'] = tmp
                    result_wifi.append(wifi_data)
            else:
                if data is not None:
                    for i in data:
                        name = i['ssid']
                        if name != '':
                            if name != wifi_org and check_ssid not in name and check_psk not in name:
                                result_wifi.append(i)
                                break
            #--- write ---
            write_data(result_wifi)

            #print('wifi_data:',wifi_data) ###
            #print('result_wifi:')   ###
            #for i in result_wifi:   ###
            #    print(i)            ###
            #---
                    
                
    elif tmp == 'ssid-psk':
        # check psk as ssid is exist
        for i in data:
            if result[1] == i['ssid'] and i['psk'] == psk:
                #print('ssid,psk as ssid exist in .conf') ###
                return
                
        #print(tmp) ###
        tmp = result[1].replace(check_ssid,'')
        tmp = tmp.split(check_psk)
        #print(tmp)###

        if len(tmp) == 2:
            if tmp[0] != '' and len(tmp[1]) >= 8:
                if tmp[0] != wifi_org:
                    if tmp[0] == wifi_data['ssid'] and tmp[1] == wifi_data['psk']:
                        #print('ssid and psk exist') ###
                        pass
                    else:
                        tmp_wifi['ssid'] = result[1]
                        tmp_wifi['psk'] = psk
                        result_wifi.append(tmp_wifi)
                        
                        wifi_data['ssid'] = tmp[0]
                        wifi_data['psk'] = tmp[1]
                        result_wifi.append(wifi_data)

                        #print('tmp_wifi:',tmp_wifi) ###
                        #print('wifi_data:',wifi_data) ###
                        #--- write ---
                        write_data(result_wifi)
                        
                        #print('result_wifi:')   ###
                        #for i in result_wifi:   ###
                        #    print(i)            ###

'''
# input:str,[]
def pro_ssid(mothed,wifi):

    print('---- pro_ssid ----')#
    print(wifi)    #
    
    if mothed == 'name-wifi':
        print('name-wifi')
        pass
    elif mothed == 'psk-wifi':
        print('psk-wifi')
        pass
    elif mothed == 'update':
        print('update')
        pass
'''


### test
# tmp_update  = ['*+&%nAAABBBCCC','aaaa']
tmp_update  = ['*+&%p111222333','aaaa']
### test



# input [] as ssid
# return [] or None
def check_ssid(data):
    global update_wifi
    
    #print('--------- check_ssid ---------')###
    if data is None:
        return None
    
    check_ssid = update_wifi[0]
    check_psk = update_wifi[1]

    result = ['','']
    #--- ssid ---
    for i in data:
        if check_ssid in i and check_psk not in i:
            tmp = i.replace(check_ssid,'')
            if tmp != '':
                result[0] = 'ssid'
                result[1] = i
                #print('ssid-wifi:',result) ###
                return result
        
    #--- psk ---
    for i in data:
        if check_ssid not in i and check_psk in i:
            tmp = i.replace(check_psk,'')
            if tmp != '':
                result[0] = 'psk'
                result[1] = i
                #print('psk-wifi:',result) ###
                return result
                
    #--- ssid,psk ---
    for i in data:
        if check_ssid in i and check_psk in i:
            tmp = i.replace(check_ssid,'')
            tmp = tmp.split(check_psk)
            if len(tmp) == 2:
                if tmp[0] != '' and tmp[1] != '':
                    result[0] = 'ssid-psk'
                    result[1] = i
                    #print('ssid-psk-wifi:',result) ###
                    return result
    return None



'''
# input [] as ssid
def check_ssid_beifen(data):
    global update_wifi
    global wifi_data
    global check_ssid
    global check_psk
    global psk

    print('--------- check_ssid ---------')###
    if data is None:
        return None
    
    check_ssid = update_wifi[0]
    check_psk = update_wifi[1]
    tmp_wifi_data = {}

    #--- ssid ---
    for i in data:
        if check_ssid in i and check_psk not in i:
            tmp_wifi_data['ssid'] = i
            tmp_wifi_data['psk'] = psk

            tmp = i.replace(check_ssid,'')
            if tmp != '':
                wifi_data['ssid'] = tmp
                wifi_data['psk'] = ''
    
                print('name-wifi:',tmp_wifi_data)    ###
                pro_ssid('name-wifi',tmp_wifi_data) # ssid as wifi
            return #break
        
    #--- psk ---
    for i in data:
        if check_ssid not in i and check_psk in i:
            tmp_wifi_data['ssid'] = i
            tmp_wifi_data['psk'] = psk
            
            tmp = i.replace(check_psk,'')
            if tmp != '':
                print('psk-wifi:',tmp_wifi_data)   ###
                pro_ssid('psk-wifi',tmp_wifi_data) # psk as wifi
                
                if wifi_data['ssid'] != '':
                    wifi_data['psk'] = tmp

                    print('ssid-psk-wifi:',wifi_data)    ###
                    pro_ssid('ssid-psk-wifi',wifi_data)    # update wifi
            return #break

    #--- ssid,psk ---
    for i in data:
        if check_ssid in i and check_psk in i:
            tmp = i.replace(check_ssid,'')
            tmp = tmp.split(check_psk)
            if len(tmp) == 2:
                if tmp[0] != '' and tmp[1] != '':
                    wifi_data['ssid'] = tmp[0]
                    wifi_data['psk'] = tmp[1]
                    
                    print('ssid-psk-wifi:',wifi_data)    ###
                    pro_ssid('ssid-psk',wifi_data)
            return #break

    
    print('check_add')#
    #--- check add
    flag = True
    for i in add_wifi:
        if i not in data:
            flag = False
            break
    if flag is True:
        tmp = data.replace(add_wifi[0],'')
        tmp = tmp.split(add_wifi[1])
        if len(tmp) == 2:
            wifi_data['ssid'] = tmp[0]
            wifi_data['psk'] = tmp[1]
            if wifi_data['ssid'] != '' and wifi_data['psk'] != '':
                pro_ssid('add',wifi_data)
            return

    print('check_del')#
    #--- check del
    flag = True
    for i in del_wifi:
        if i not in data:
            flag = False
            break
    if flag is True:
        tmp = data.replace(del_wifi[0],'')
        tmp = tmp.replace(del_wifi[1],'')
        if tmp != '':
            wifi_data['ssid'] = tmp
            wifi_data['psk'] = ''
            pro_ssid('del',wifi_data)
            return

    print('check_del_all')#
    # check del_all
    if data == del_all_wifi:
        wifi_data['ssid'] = ''
        wifi_data['psk'] = ''
        pro_ssid('del_all',wifi_data)
        return
'''

#################################################################################

if __name__ == '__main__':
    # print('DO WIFI START ----------------------------------------') ###
    restart_wifi = ('sudo ifdown wlan0','sudo ifup wlan0')
    os.system(restart_wifi[1] + ' > ' + file_tmp)
    time.sleep(1)
    os.system('sudo ifconfig wlan0 up')
    time.sleep(1)
    # print('DO WIFI FINISH ---------------------------------------') ###
    #--------------------------------------------------------------------    
    
    # scan wlan0 and get ssid
    file_wifi_scan = 'wifi-scan.conf'

    while True:
        '''
        tmp = input('please input:')###
        tmp_update[0] = tmp         ###
        if tmp == 'q':              ###
            sys.exit()              ###
        if tmp == '':               ###
            continue                ###
        '''
        
        scan_wlan(file_wifi_scan)
        ssid_list = get_essid(file_wifi_scan)

        if ssid_list is not None:
            result = check_ssid(ssid_list)     # tmp_update
            
            if result is not None:
                if len(result) == 2:
                    #--- operation .conf file ---
                    # get ssid,psk from .conf
                    data = get_data(file_name)
                    data = pro_data(data)
                    data = cal_data(result,data)
                    #print('-------- done --------------------------------')  ###
                    #
            
                
        time.sleep(10) # 10 s
        #------------
        # data = get_data(file_name)
        # data = pro_data(data)
        # cal_data(ssid_data,data)

    


    

