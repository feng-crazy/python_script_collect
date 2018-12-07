#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re

import numpy
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from matplotlib.pyplot import *
from matplotlib import animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


from PyQt5.QtWidgets import QWidget,QApplication,QLabel,QDialog,QPushButton,QVBoxLayout,\
                            QHBoxLayout,QGridLayout,QLabel,QLineEdit,QMessageBox,QFileDialog       
from PyQt5.QtGui import QPainter,QColor,QFont,QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt,QThread,QObject,QTimer
from PyQt5.QtCore import *

import sys

##########################################################################################

class data_source(object):
    def __init__(self):
        self.data_list = []  # store data from file
        self.head_index = 0
        self.currend_index = 0
        self.data_x = []
        self.data_y = []
        self.LEN = 32
        
    # return:left_x[],left_y[],right_x[],right_y[],total_frame,current_frame
    #               left              right
    def reset(self):
        if self.data_list in ([],None):
            return None,None,None,None,None,None

        # left
        if self.data_list[0] in ([],None):
            return None,None,None,None,None,None
        if len(self.data_list[0]) != self.LEN + 1:
            return None,None,None,None,None,None

        self.head_index = 0
        self.currend_index = 0
        
        tmp = self.data_list[0]
        left_y = tmp[0:-1]
        tmp = len(left_y)
        left_x = [i for i in range(1,tmp + 1)]

        # right
        tmp = self.data_list[0]
        self.data_y = []
        self.data_y.append(tmp[-1])
        self.data_x = [1]

        return left_x,left_y,self.data_x,self.data_y,len(self.data_list),self.currend_index + 1
        

    # return:left_x[],left_y[],right_x[],right_y[],total_frame,current_frame
    #               left              right
    def prev(self):
        if self.data_list == []:
            return None,None,None,None,None,None
        
        if self.head_index > 0:
            self.head_index -= 1
        else:
            if self.currend_index > 0:
                self.currend_index -= 1
            else:
                return None,None,None,None,None,None
        if self.currend_index - self.head_index > self.LEN:
            self.currend_index = self.head_index + self.LEN
        tmp = len(self.data_list)
        if self.currend_index >= tmp:
            self.currend_index = tmp - 1

        # left
        tmp = self.data_list[self.currend_index]
        left_y = tmp[0:-1]
        tmp = len(left_y)
        left_x = [i for i in range(1,tmp + 1)]
        
        # right
        if self.currend_index - self.head_index >= self.LEN:
            tmp = self.head_index + 1
        else:
            tmp = self.head_index

        tmp = self.data_list[tmp : self.currend_index + 1]
        self.data_y = [i[-1] for i in tmp]
        tmp = len(self.data_y)
        self.data_x = [i for i in range(1,tmp + 1)]
    
        return left_x,left_y,self.data_x,self.data_y,len(self.data_list),self.currend_index + 1  
            

    # return:left_x[],left_y[],right_x[],right_y[],total_frame,current_frame
    #               left              right
    def next(self):
        if self.data_list == []:
            return None,None,None,None,None,None
        tmp = len(self.data_list)
        self.currend_index += 1
        if self.currend_index >= tmp:
            return None,None,None,None,None,None
        if self.currend_index - self.head_index > self.LEN:
            self.head_index = self.currend_index - self.LEN

        # left
        tmp = self.data_list[self.currend_index]
        left_y = tmp[0:-1]
        tmp = len(left_y)
        left_x = [i for i in range(1,tmp + 1)]

        # right
        if self.currend_index - self.head_index >= self.LEN:
            tmp = self.head_index + 1
        else:
            tmp = self.head_index

        tmp = self.data_list[tmp : self.currend_index + 1]
        self.data_y = [i[-1] for i in tmp]
        tmp = len(self.data_y)
        self.data_x = [i for i in range(1,tmp + 1)]
    
        return left_x,left_y,self.data_x,self.data_y,len(self.data_list),self.currend_index + 1  

    
    def read_file(self,file_name):
        #self.data_list = []

        data_tmp = []
        try:
            fd = open(file_name,'r')

            flag = 0
            tmp = []

            rule = re.compile(r'\ {1}\d+\.*\d+[a-z]{2}')

            for j,i in enumerate(fd):
                if flag == 1:
                    b = i.strip()
                    #---
                    ts = rule.findall(b)
                    if ts != []:
                        b = b.replace(ts[0],'')
                        b = b.strip()
                    #---
                    b = b.replace('  ',',')
                    b = b.replace(' ','')
                    b = b.split(',')
                    ##print(str(j) + ':',b)##

                    have_total = False
                    for n,m in enumerate(b):
                        if m[2] == '2':
                            have_total = True
                            tmp += b[0:n + 1]
                            #self.data_list.append(tmp)
                            data_tmp.append(tmp)
                            
                            tmp = []
                            tmp += b[n + 1:]

                            ##print('total:',m)##
                            break
                    if have_total == False:
                        tmp += b

                    #b = [int(m,16) for m in b]
                    ##print(str(j) + ':',b)
                        
                    #if j >= 21: 
                    #    break   
                    
                if '----' in i:
                    flag = 1
            fd.close()
        except:
            return None

        '''
        if self.data_list == []:
            return None

        for i,j in enumerate(self.data_list):
            try:
                self.data_list[i] = [int(m,16) for m in j]
            except:
                #print('data of file error')
                return None
    
        for i,j in enumerate(self.data_list):
            tmp = 0
            for m in j[0:-1]:
                tmp += m
            tmp = j[-1] - tmp
            if tmp < 0:
                return None
            self.data_list[i].insert(-1,tmp)
        return self.data_list
        '''

        if data_tmp == []:
            return None
        for i,j in enumerate(data_tmp):
            try:
                data_tmp[i] = [int(m,16) for m in j]
            except:
                #print('data of file error')
                return None
    
        for i,j in enumerate(data_tmp):
            tmp = 0
            for m in j[0:-1]:
                tmp += m
            tmp = j[-1] - tmp
            if tmp < 0:
                return None
            data_tmp[i].insert(-1,tmp)

        self.data_list = data_tmp
        return self.data_list


    
#################################################################################
class My_Window(QDialog):
    def __init__(self):
        super().__init__()

        #-----
        self.TIME_DEFAULT = '0.5'
        self.LEFT_MIN_DEFAULT = '70000'
        self.LEFT_MAX_DEFAULT = '80000'
        self.RIGHT_MIN_DEFAULT = '2400000'
        self.RIGHT_MAX_DEFAULT = '2500000'
        
        
        self.OPEN_FILE = '打开文件'
        self.PREV = '上一帧'
        self.NEXT = '下一帧'
        self.RESET = '复位'
        self.START = '自动'
        self.PAUSE = '暂停'
        self.TOTAL_LABEL = '总帧数:'
        self.CURRENT_LABEL = '当前帧:'
        self.FILE_NAME = 'a.txt' # 默认打开文件
        #-----
        self.status_flag = False # 状态

        self.left_x = []
        self.left_y = []
        self.right_x = []
        self.right_y = []
        self.total_frame = 0
        self.current_frame = 0

        #------------- 设置图形 --------------
        self.figure = plt.figure(figsize = (16,8),dpi = 100)  # (8,4)
        self.canvas = FigureCanvas(self.figure)

        self.ax1 = plt.subplot(121)
        self.ax2 = plt.subplot(122)

        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置显示中文
        plt.rcParams['axes.unicode_minus'] = False

        #------------- 设置组件 --------------
        #--------------- 标签 ---------------
        self.time_label = QLabel('时间间隔(s):')
        
        self.left_min_label = QLabel('挡板高度起始值:')
        self.left_max_label = QLabel('挡板高度最大值:')
        self.right_min_label = QLabel('周期高度起始值:')
        self.right_max_label = QLabel('周期高度最大值:')
        
        self.total = QLabel(self.TOTAL_LABEL)
        self.current = QLabel(self.CURRENT_LABEL)
        self.total_label = QLabel(' ' * 3 + str(self.total_frame))  #self.total_label.resize(30,10)
        self.current_label = QLabel(' ' * 3 + str(self.current_frame))
        #--------------- 文本框 ---------------
        self.open_edit = QLineEdit()        # 打开文件

        self.time_edit = QLineEdit()        # time
        self.time_edit.setText(self.TIME_DEFAULT)
        self.time_edit.setMaxLength(3)
        self.time_edit.setValidator(QDoubleValidator(0.1,100.0,3.0,self))
        self.time_edit.textChanged[str].connect(self.edit_change)
        
        self.left_min_edit = QLineEdit()    # 挡板高度起始值
        self.left_min_edit.setText(self.LEFT_MIN_DEFAULT)
        self.left_min_edit.setMaxLength(len(self.LEFT_MAX_DEFAULT))
        self.left_min_edit.setValidator(QIntValidator(0,200000,self))
        self.left_min_edit.textChanged[str].connect(self.edit_change)#?

        self.left_max_edit = QLineEdit()    # 挡板高度最大值
        self.left_max_edit.setText(self.LEFT_MAX_DEFAULT)
        self.left_max_edit.setMaxLength(len(self.LEFT_MAX_DEFAULT) + 1)
        self.left_max_edit.setValidator(QIntValidator(0,200000,self))
        self.left_max_edit.textChanged[str].connect(self.edit_change)#?

        self.right_min_edit = QLineEdit()   # 周期高度起始值
        self.right_min_edit.setText(self.RIGHT_MIN_DEFAULT)
        self.right_min_edit.setMaxLength(len(self.RIGHT_MAX_DEFAULT))
        self.right_min_edit.setValidator(QIntValidator(0,4000000,self))
        self.right_min_edit.textChanged[str].connect(self.edit_change)#?

        self.right_max_edit = QLineEdit()   # 周期高度最大值
        self.right_max_edit.setText(self.RIGHT_MAX_DEFAULT)
        self.right_max_edit.setMaxLength(len(self.RIGHT_MAX_DEFAULT) + 1)
        self.right_max_edit.setValidator(QIntValidator(0,4000000,self))
        self.right_max_edit.textChanged[str].connect(self.edit_change)#?
        #--------------- 按钮组件 ---------------
        self.open_button = QPushButton(self.OPEN_FILE)  # 打开文件

        self.prev = QPushButton(self.PREV)
        self.next = QPushButton(self.NEXT)
        self.reset = QPushButton(self.RESET)
        self.start_pause = QPushButton(self.START)

        self.open_button.clicked.connect(self.open_file)
        self.prev.clicked.connect(self.button_event)
        self.next.clicked.connect(self.button_event)
        self.reset.clicked.connect(self.button_event)
        self.start_pause.clicked.connect(self.button_event)

        #--------------- 布局 ---------------
        # 底部局部布局
        self.layout_bottom_1 = QGridLayout()    #
        self.layout_bottom_1.addWidget(self.open_button,1,1)
        self.layout_bottom_1.addWidget(self.open_edit,1,2)
        self.layout_bottom_1.addWidget(self.time_label,2,1)
        self.layout_bottom_1.addWidget(self.time_edit,2,2)
        
        self.layout_bottom_2 = QGridLayout()    #
        self.layout_bottom_2.addWidget(self.left_max_label,1,1)
        self.layout_bottom_2.addWidget(self.left_max_edit,1,2)
        self.layout_bottom_2.addWidget(self.left_min_label,2,1)
        self.layout_bottom_2.addWidget(self.left_min_edit,2,2)
        

        self.layout_bottom_3 = QGridLayout()    #
        self.layout_bottom_3.addWidget(self.right_max_label,1,1)
        self.layout_bottom_3.addWidget(self.right_max_edit,1,2)
        self.layout_bottom_3.addWidget(self.right_min_label,2,1)
        self.layout_bottom_3.addWidget(self.right_min_edit,2,2)
        

        self.layout_bottom_4 = QGridLayout()    #
        self.layout_bottom_4.addWidget(self.prev,1,1)
        self.layout_bottom_4.addWidget(self.next,1,2)
        self.layout_bottom_4.addWidget(self.reset,2,1)
        self.layout_bottom_4.addWidget(self.start_pause,2,2)

        self.layout_bottom_5 = QGridLayout()    # label:self.total_label,self.current_label
        self.layout_bottom_5.addWidget(self.total,1,1)
        self.layout_bottom_5.addWidget(self.current,2,1)
        self.layout_bottom_5.addWidget(self.total_label,1,2)
        self.layout_bottom_5.addWidget(self.current_label,2,2)

        # 底部布局
        self.bottom = QHBoxLayout()        # bottom
        self.bottom.addLayout(self.layout_bottom_1)     # self.bottom.addLayout(self.layout_op)
        self.bottom.addLayout(self.layout_bottom_2)     # self.bottom.addLayout(self.layout_label)
        self.bottom.addLayout(self.layout_bottom_3)                            
        self.bottom.addStretch(1)
        self.bottom.addLayout(self.layout_bottom_4)     # self.bottom.addLayout(self.layout_button)
        self.bottom.addStretch(3)
        self.bottom.addLayout(self.layout_bottom_5)     # self.bottom.addLayout(self.layout_label_f)
        self.bottom.addStretch(1)
        # 整体布局
        self.all = QVBoxLayout()           # all
        self.all.addWidget(self.canvas)
        self.all.addLayout(self.bottom)
        #
        self.setLayout(self.all)
        #------------ 设置定时器 -------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_draw_next)
        self.count = 0

        #-------------- get data -------------
        self.data = data_source()
        
        self.file_name = self.FILE_NAME
        tmp = self.data.read_file(self.file_name)
        if tmp != None:
            self.left_x,self.left_y,self.right_x,self.right_y,self.total_frame,self.current_frame =self.data.reset()
            if self.left_x != None and self.left_y != None and self.right_x != None and self.right_y != None and self.total_frame != None:
                self.open_edit.setText(self.file_name)
                self.total_label.setText(str(self.total_frame))     #显示总帧数
                self.current_label.setText(str(self.current_frame)) #显示当前帧
                self.show_data()
                self.status_flag = True # 设置状态

        if self.status_flag == False:
            self.total_label.setText(' ' * 3 + str(self.total_frame))     #显示总帧数
            self.current_label.setText(' ' * 3 + str(self.current_frame)) #显示当前帧
            self.show_data()  
        #--------------------------------------

    def edit_change(self,text):
        #print('edit:',text)
        #print('get:',self.left_min_edit.text())
        pass


    def open_file(self):
        #print('open file')#
        # get file name
        tmp_file,tmp_type = QFileDialog.getOpenFileName(self,'打开文件','./','Text Files (*.txt)')
        #print(tmp_file)#
        # read file
        tmp = self.data.read_file(tmp_file)
        if tmp != None:
            l_x,l_y,r_x,r_y,total_tmp,current_tmp =self.data.reset()
            if l_x != None and l_y != None and r_x != None and r_y != None and total_tmp != None:
                self.file_name = tmp_file
                self.left_x,self.left_y,self.right_x,self.right_y,self.total_frame,self.current_frame = l_x,l_y,r_x,r_y,total_tmp,current_tmp
                
                self.open_edit.setText(self.file_name)
                self.total_label.setText(str(self.total_frame))     #显示总帧数
                self.current_label.setText(str(self.current_frame)) #显示当前帧
                self.show_data()
                self.status_flag = True # 设置状态
            else:
                QMessageBox.warning(self,'提示','文件数据内容错误!',QMessageBox.Yes)
        else:
            QMessageBox.warning(self,'提示','文件数据内容错误!',QMessageBox.Yes)


    def button_event(self):
        #print('self.status_flag:',self.status_flag)##
        if self.status_flag == False:
            return
        
        ##print('botton_event:',tmp)
        ##print('left_min_edit:',self.left_min_edit.text())
        ##print('time_edit:',self.time_edit.text())

        tmp = self.sender().text()

        if tmp == self.PREV:    # '上一帧'
            #print(1)#
            self.left_x,self.left_y,self.right_x,self.right_y,self.total_frame,self.current_frame =self.data.prev()
            if self.left_x != None and self.left_y != None and self.right_x != None and self.right_y != None and self.total_frame != None:
                self.total_label.setText(str(self.total_frame))     #显示总帧数
                self.current_label.setText(str(self.current_frame)) #显示当前帧
                self.show_data()
                
        elif tmp == self.NEXT:  # '下一帧'
            #print(2)# 
            self.left_x,self.left_y,self.right_x,self.right_y,self.total_frame,self.current_frame =self.data.next()
            if self.left_x != None and self.left_y != None and self.right_x != None and self.right_y != None and self.total_frame != None:
                self.total_label.setText(str(self.total_frame))     #显示总帧数
                self.current_label.setText(str(self.current_frame)) #显示当前帧
                self.show_data()
                
        elif tmp == self.RESET: # '复位'
            #print(3)#
            self.start_pause.setText(self.START)
            self.timer.stop()   # 停止定时器
            
            self.left_x,self.left_y,self.right_x,self.right_y,self.total_frame,self.current_frame =self.data.reset()
            if self.left_x != None and self.left_y != None and self.right_x != None and self.right_y != None and self.total_frame != None:
                self.total_label.setText(str(self.total_frame))     #显示总帧数
                self.current_label.setText(str(self.current_frame)) #显示当前帧
                self.show_data()
                
        elif tmp == self.START: # '自动'
            #print(4)#
            # get time
            tmp = self.get_edit_time()
            if tmp == None:
                return
            
            #print('time:',tmp)##
            self.sender().setText(self.PAUSE)
            self.timer.start(tmp)  # 启动定时器
            
        elif tmp == self.PAUSE: # '暂停'
            #print(5)#
            self.sender().setText(self.START)
            self.timer.stop()   # 停止定时器


    def auto_draw_next(self):
        #print('auto')#
        
        self.left_x,self.left_y,self.right_x,self.right_y,self.total_frame,self.current_frame =self.data.next()
        #print('current_frame:',self.current_frame)#

        if self.left_x != None and self.left_y != None and self.right_x != None and self.right_y != None and self.total_frame != None:
            self.total_label.setText(str(self.total_frame))     #显示总帧数
            self.current_label.setText(str(self.current_frame)) #显示当前帧
            self.show_data()
        else: # to end
            #print('auto end')#
            self.start_pause.setText(self.START)
            self.timer.stop()   # 停止定时器
            

    #------------------------ 重载关闭窗口事件 --------------------------
    def closeEvent(self,event):
        self.timer.stop()   # 停止定时器

    #---------------------------- 获取高度-------------------------------
    # return: int
    def get_edit_high(self,edit_hight):
        tmp = None
        try:
            tmp = edit_hight.text()
            #print('get_edit_hight:',tmp) #
            tmp = int(tmp)
            if tmp < 0:
                QMessageBox.information(self,'提示','高度值输入错误',QMessageBox.Yes)
                return None            
        except:
            QMessageBox.information(self,'提示','高度值输入错误',QMessageBox.Yes)
            return None
        return tmp
    
    #-------------------------- 获取标签时间 -----------------------------
    # return: ms
    def get_edit_time(self):
        tmp = None
        try:
            tmp = self.time_edit.text()
            tmp = float(tmp)
            tmp = tmp * 1000
            tmp = int(tmp)
            if tmp <= 0:
                QMessageBox.information(self,'提示','时间输入错误',QMessageBox.Yes)
                return None            
        except:
            QMessageBox.information(self,'提示','时间输入错误',QMessageBox.Yes)
            return None
        return tmp


    #------------------------ 高度起始值 -------------------------
    def get_hight(self):
        
        tmp = self.left_min_edit.text()
        hight = 0
        try:
            hight = int(tmp) 
            if hight < 0:
                QMessageBox.information(self,'提示','高度起始值错误',QMessageBox.Yes)
                return None
        except:
            QMessageBox.information(self,'提示','高度起始值错误',QMessageBox.Yes)
            return None
        return hight

    #------------------------ show data:--------------------------
    #self.left_x
    #self.left_y
    #self.right_x
    #self.right_y
    #-------------------------------------------------------------
    def show_data(self):
        ##print(self.right_x,self.right_y)##
        ##print(self.right_x,self.right_y)##
                    
        if self.left_x == None or self.left_y == None:
            #print('reset button:data of left is None')
            return

        if self.right_x == None or self.right_y == None:
            #print('reset button:data of right is None')
            return

        if self.total_frame == None:
            return

        #--------- 计算标准差 ----------
        content = ''
        if self.left_y not in (None,[]):
            tmp = numpy.std(self.left_y,ddof = 1)
            tmp = round(tmp,3)  # 3位小数
            #content = 'Standard devication:' + str(tmp)
            content = u'标准差:' + str(tmp)

        #------ get ax1,ax2 high -------
        left_hight_min = self.get_edit_high(self.left_min_edit)
        left_hight_max = self.get_edit_high(self.left_max_edit)
        right_hight_min = self.get_edit_high(self.right_min_edit)
        right_hight_max = self.get_edit_high(self.right_max_edit)

        if left_hight_min == None or left_hight_max == None or right_hight_min == None or right_hight_max == None:
            return
        if left_hight_min >= left_hight_max or right_hight_min >= right_hight_max:
            QMessageBox.information(self,'提示','高度值大小有误',QMessageBox.Yes)
            return

        #----------- show ax1 ----------
        plt.sca(self.ax1)
        plt.cla() # 清除子图

        plt.xlim(0,33) # plt.xlim(1,32)
        plt.ylim(left_hight_min,left_hight_max)
        plt.xticks([i for i in range(1,32,2)])
        tmp = int((left_hight_max - left_hight_min) / 5)
        plt.yticks([i for i in range(left_hight_min,left_hight_max + tmp,tmp)])
                
        self.ax1.lines = [] # 清除子图
        plt.title(content)
        # self.lines = self.ax1.plot(self.x,self.y)     # plt.grid(True) # 显示网格线
        plt.xlabel(u'挡板')
        plt.ylabel(u'高度')
        plt.bar(self.left_x,self.left_y,width = 0.6,label = 'first line',color = 'g')

        #----------- show ax2 ----------
        plt.sca(self.ax2)
        plt.cla() # 清除子图

        plt.xlim(0,33) # plt.xlim(1,32)
        plt.ylim(right_hight_min,right_hight_max)
        plt.xticks([i for i in range(1,32,2)])
        tmp = int((right_hight_max - right_hight_min) / 5)
        plt.yticks([i for i in range(right_hight_min,right_hight_max + tmp,tmp)])

        self.ax2.lines = [] # 清除子图
        # self.lines = self.ax2.plot(self.x,self.y)            
        plt.xlabel(u'周期')
        plt.ylabel(u'高度')
        plt.plot(self.right_x,self.right_y,label = 'second line',color = 'r',marker = 'o')
        # 显示图形
        self.canvas.draw()
    

    def draw(self):
        ##print('self.sender:',self.sender().text())#
        
        self.x = [1,2,4]
        self.y = [15,17,14]
        #self.y = [i for i in range(32)]
        
        self.x2 = [1,2,3]
        self.y2 = [10,14,12]

        self.timer.stop()
        self.count = 0

        # show ax1
        plt.sca(self.ax1)

        plt.xlim(1,32)
        plt.xticks([i for i in range(1,32,2)])
        
        self.ax1.lines = [] # 清除子图
        plt.plot(self.x,self.y,label = 'first line',color = 'g',zorder = 1)

        # show ax2
        plt.sca(self.ax2)
        self.ax2.lines = [] # 清除子图
        plt.plot(self.x2,self.y2,label = 'second line',color = 'r')
        self.canvas.draw()

        # 启动定时器
        self.timer.start(1000)

        #
        #print('button get edit:',self.edit1.text())##

    def update_fig(self):
        self.y = [i + 0.2 for i in self.y]
        self.y2 = [i + 0.2 for i in self.y2]
        self.count += 1
        if self.count > 10:
            self.timer.stop()
        #print(self.y)#

        # show ax1
        plt.sca(self.ax1)
        self.ax1.lines = [] # 清除子图
        # self.lines = self.ax1.plot(self.x,self.y)
        plt.plot(self.x,self.y,label = 'first line',color = 'g')
        
        # show ax2
        plt.sca(self.ax2)
        self.ax2.lines = []
        plt.plot(self.x2,self.y2,label = 'second line',color = 'r')
        
        self.canvas.draw()
        





if __name__ == '__main__':
    ###
    #read_file(file_name)
    '''
    file_name = '1.txt'
    data = data_source()
    tmp = data.read_file(file_name)
    '''
    ###
    
    ######################################################################

    app = QApplication(sys.argv)
    my_window = My_Window()
    my_window.show()
    sys.exit(app.exec_())
    
    ######################################################################
    '''
    x = [1,2,3]
    y = [15,17,14]
    x2 = [1,2,3]
    y2 = [10,14,12]
    plt.figure(figsize=(6,4))       #plt.figure(1)       #定义图片
    plt.subplot(121)    #定义子图
    plt.plot(x,y,label='first line')

    plt.subplot(122)
    plt.plot(x2,y2,label='second line')

    #plt.bar([1,3,5],y,label='first bar',color='r')
    #plt.bar([2,4,6],y2,label='second bar',color='g')
    
    plt.axis([0,20,9,20])# 坐标轴的度量

    plt.title('graph')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()

    plt.show()
    '''


    '''
    #print('len:',len(tmp))
    #print(tmp[-1])

    a,b,c,d = data.reset()
    #print('r:')
    #print('left_x:',a)
    #print('left_y:',b)
    #print('right_x:',c)
    #print('right_y:',d)

    flag = True
    while flag:
        a,b,c,d = data.next()
        if a == None:
            #print('e:')
            #print('left_x:',m)
            #print('left_y:',n)
            #print('right_x:',i)
            #print('right_y:',j)
            flag = False
        m,n,i,j = a,b,c,d

    #print('prev:')
    flag = True
    while flag:
        a,b,c,d = data.prev()
        if a == None:
            #print('1:')
            #print('left_x:',m)
            #print('left_y:',n)
            #print('right_x:',i)
            #print('right_y:',j)
            flag = False
        m,n,i,j = a,b,c,d
        
    
    #print('read over')
    '''


    
            #----------- QMessageBox -----------
            #tmp = QMessageBox.warning(self,'提示','请打开文件',QMessageBox.Yes)
            ##print(tmp)
            #tmp = QMessageBox.information(self,'提示','请打开文件',QMessageBox.Yes)
            ##print(tmp)
            #----------- QFileDialog -----------
            # 打开文件框
            #f_name,f_tpye = QFileDialog.getOpenFileName(self,'打开文件','./','Text Files (*.txt)')
            ##print(f_name)
            #----------------------------------- 


    
