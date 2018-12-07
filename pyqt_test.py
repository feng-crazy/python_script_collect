#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget,QApplication,QLabel,QDialog,QPushButton,QVBoxLayout,QStackedWidget,
                            QHBoxLayout,QGridLayout,QLabel,QLineEdit,QRadioButton,QMessageBox,QFileDialog,QFrame)
from PyQt5.QtGui import QPainter,QColor,QFont,QIntValidator,QDoubleValidator,QPen,QColor,QPalette,QFont,QBrush,QLinearGradient
from PyQt5.QtCore import Qt,QThread,QObject,QTimer,QRect
from PyQt5.QtCore import *

from DXF import DataDXF


###################################################################################




###################################################################################
class My_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100,100,1400,800)
        self.setWindowTitle('...')
        #---------------------------------------
        self.area = PaintArea(self)
        self.priv_data = None
        #------------- 添加控件 ----------------
        #--------------- QLabel ----------------
        self.high_label =  QLabel('高度(cm):')
        self.index_label = QLabel('间隔(cm):')
        self.zoom_label =  QLabel('比    例:')
        
        self.base_msg_label =   QLabel('      基站信息:')
        self.X_label =          QLabel('   X坐标(cm):')
        self.Y_label =          QLabel('   Y坐标(cm):')
        self.base_high_label =  QLabel('基站高度(cm):')
        self.base_msg_label.setEnabled(False)
        self.X_label.setEnabled(False)
        self.Y_label.setEnabled(False)
        self.base_high_label.setEnabled(False)
        #-------------- QLineEdit --------------
        self.high_edit = QLineEdit()
        self.high_edit.setText(str(300))
        self.high_edit.setAlignment(Qt.AlignRight)
        self.high_edit.setMaxLength(6)
        self.high_edit.setValidator(QDoubleValidator(0,3000.0,5,self))
        
        self.index_edit = QLineEdit()
        self.index_edit.setText(str(300))
        self.index_edit.setAlignment(Qt.AlignRight)
        self.index_edit.setMaxLength(4)
        self.index_edit.setValidator(QIntValidator(0,1000,self))

        self.zoom_edit = QLineEdit()
        self.zoom_edit.setText(str(1.0))
        self.zoom_edit.setAlignment(Qt.AlignRight)
        self.zoom_edit.setMaxLength(5)
        self.zoom_edit.setValidator(QDoubleValidator(0.1,100.0,4,self))

        self.X_edit = QLineEdit()
        self.X_edit.setText(str(0))
        self.X_edit.setAlignment(Qt.AlignRight)
        self.X_edit.setMaxLength(7)
        self.X_edit.setValidator(QDoubleValidator(0,10000.0,5,self))
        self.X_edit.setEnabled(False)

        self.Y_edit = QLineEdit()
        self.Y_edit.setText(str(0))
        self.Y_edit.setAlignment(Qt.AlignRight)
        self.Y_edit.setMaxLength(7)
        self.Y_edit.setValidator(QDoubleValidator(0,10000.0,5,self))
        self.Y_edit.setEnabled(False)
        
        self.base_high_edit = QLineEdit()
        self.base_high_edit.setText(str(300))
        self.base_high_edit.setAlignment(Qt.AlignRight)
        self.base_high_edit.setMaxLength(6)
        self.base_high_edit.setValidator(QDoubleValidator(0,3000.0,5,self))
        self.base_high_edit.setEnabled(False)
        #---------- QPushButton ----------------
        self.open_button = QPushButton(self)
        self.open_button.setText('打开文件')
        self.open_button.clicked.connect(self.button_click)
        # self.open_button.setEnabled(False)

        self.cal_button = QPushButton(self)
        self.cal_button.setText('计算位置')
        self.cal_button.clicked.connect(self.button_click)
        self.cal_button.setEnabled(False)

        self.addr_button = QPushButton(self)
        self.addr_button.setText('计算地址')
        self.addr_button.clicked.connect(self.button_click)
        self.addr_button.setEnabled(False)

        self.ok_button = QPushButton(self)
        self.ok_button.setText('确定')
        self.ok_button.clicked.connect(self.button_click)
        self.ok_button.setEnabled(False)

        self.base_station_status = QRadioButton('设为基站')
        #self.base_station_status.setChecked(True)
        #self.base_station_status.toggled.connect(self.set_base_station)
        self.base_station_status.setEnabled(False)
        #-------------- 布局 -------------------
        # right layout
        rightlayout = QVBoxLayout()

        # high label,lineedit
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.high_label)
        tmp_layout.addWidget(self.high_edit)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)

        # index label,lineedit
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.index_label)
        tmp_layout.addWidget(self.index_edit)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)

        # zoom label,lineedit
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.zoom_label)
        tmp_layout.addWidget(self.zoom_edit)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)
        rightlayout.addStretch(1)

        # button
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.open_button)
        tmp_layout.addWidget(self.cal_button)
        tmp_layout.addWidget(self.addr_button)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)
        rightlayout.addStretch(1)

        # base station msg,base_station_status
        tmp_layout = QHBoxLayout()
        #tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.base_msg_label)
        tmp_layout.addWidget(self.base_station_status)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)

        # x label,lineedit
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.X_label)
        tmp_layout.addWidget(self.X_edit)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)

        # y label,lineedit
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.Y_label)
        tmp_layout.addWidget(self.Y_edit)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)

        # high label,lineedit
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.base_high_label)
        tmp_layout.addWidget(self.base_high_edit)
        tmp_layout.addStretch(1)
        rightlayout.addLayout(tmp_layout)

        # ok_button
        tmp_layout = QHBoxLayout()
        tmp_layout.addStretch(1)
        tmp_layout.addWidget(self.ok_button)
        tmp_layout.addStretch(2)
        rightlayout.addLayout(tmp_layout)

        rightlayout.addStretch(1)
        # main layout
        mainlayout = QGridLayout()
        mainlayout.setColumnStretch(0,5)            #设置第一列和第二列的比例为5:1
        mainlayout.setColumnStretch(1,1)
        mainlayout.addWidget(self.area,0,0,-1,1)    #位置一行一列,占4行1列(self.area,0,0,4,1)
        mainlayout.addLayout(rightlayout,0,1,-1,1)
        #---------------------------------------
        self.setLayout(mainlayout)


    def set_icon_status(self,status):
        if status == True:
            tmp = True
        else:
            tmp = False
        self.base_msg_label.setEnabled(tmp)
        self.X_label.setEnabled(tmp)
        self.Y_label.setEnabled(tmp)
        self.base_high_label.setEnabled(tmp)

        self.X_edit.setEnabled(tmp)
        self.Y_edit.setEnabled(tmp)
        self.base_high_edit.setEnabled(tmp)

        self.base_station_status.setEnabled(tmp)
        self.ok_button.setEnabled(tmp)


    def set_base_station(self,index,x,y,high,base_status):
        print('this is radio button')
        
        # store index of self.area.base_station
        if len(index) == 2:
            self.priv_data = index
        else:
            print('set_base_station index err')
            return
        
        # enable icon
        self.set_icon_status(True)
            
        # show x,y,high,base_status
        if base_status == True:
            self.base_station_status.setChecked(True)
        else:
            self.base_station_status.setChecked(False)

        self.X_edit.setText(str(x))
        self.Y_edit.setText(str(y))
        self.base_high_edit.setText(str(high))
        #
        if self.base_station_status.isChecked():
            print('checked')
        else:
            print('not check')



    def button_click(self):
        # high
        s = float(self.high_edit.text())
        print('high:',s)
        if 100 < s < 1000:
            self.area.high = s
        else:
            print('high input err')
            #self.area.high = 300

        # zoom
        s = float(self.zoom_edit.text())
        print('zoom:',s)
        if s > 0:
            self.area.value_zoom = s
        else:
            print('zoom input err')
            #self.area.value_zoom = 1
    
        tmp = self.sender()
        #-----------------------------
        if tmp != self.ok_button:
            # disable icon
            self.set_icon_status(False)
        #-----------------------------
        if tmp == self.open_button:
            print('open_button')
            try:
                tmp_file,tmp_type = QFileDialog.getOpenFileName(self,'打开文件','./','Text Files (*.dxf)')
                file = open(tmp_file,'r')
            except:
                print('open file err')
                return
            dxf = DataDXF(file)
            tmp = dxf.readDXF()
            #-----------------------------
            print('get_data')
            if self.area.get_data(tmp) == False:
                return
            
            self.cal_button.setEnabled(True)    # enable cal_button
            #-----------------------------
            self.area.update()
        elif tmp == self.cal_button:
            print('cal_button')
            try:
                index = float(self.index_edit.text())
            except:
                print('间隔 input err')
                index = 300.0
        
            print('index:',index)
            #-----------------------------
            '''
            try:
                file = open('./dxf_file/5.dxf','r')
            except:
                print('open file err')
                return
            dxf = DataDXF(file)
            tmp = dxf.readDXF()
            #-----------------------------
            print('get_data')
            if self.area.get_data(tmp) == False:
                return
            '''
            #---
            print('cal_point')
            if self.area.cal_point() == False:
                return
            #---
            print('cal_all_line')
            if self.area.cal_all_line(index) == False:
                return
            #---
            print('cal_device_XY')
            if self.area.cal_device_XY(index) == False:
                return
            #-----------------------------
            self.addr_button.setEnabled(True)    # enable cal_button
            self.area.update()
        elif tmp == self.addr_button:
            print('cal_addr')
            if self.area.cal_addr() == False:
                return
            #-----------------------------
            self.area.show_addr_flag = 1
            self.area.update()
        elif tmp == self.ok_button:
            print('ok_button')
            if self.priv_data == None:
                print('self.priv_data is None')
                return None
            
            x = float(self.X_edit.text())
            y = float(self.Y_edit.text())
            high = float(self.base_high_edit.text())
            if self.base_station_status.isChecked():
                base_status = True
            else:
                base_status = False
            if self.area.change_one_XY(self.priv_data,x,y,high,base_status) == False:
                return
            if self.area.cal_addr() == False:
                return
            #-----------------------------
            self.area.show_addr_flag = 1
            self.area.update()
            


class PaintArea(QWidget):
    def __init__(self,window):
        super().__init__()
        self.window = window
        self.initUI()


    def initUI(self):
        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.setMinimumSize(400,400)
        ############
        self.BK_color = Qt.blue
        self.BS_color = Qt.red
        self.POINT_WIDTH = 10
        self.value_zoom = 1.0

        self.show_addr_flag = 0
        ############
        self.high = 300     # base station high
        #self.point = []    # [[50,300],[250,50],[500,200],[450,500],[300,500]]
        self.line = []      # [[250,50,500,200],[500,200,450,500],[450,500,300,500],[300,500,50,300],[50,300,250,50]]
        #
        self.left_top = {'x':0,'y':0}
        self.right_bottom = {'x':0,'y':0}
        self.data = []          # store point msg
        self.base_station = []  # store basestation point


    def paintEvent(self,event):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()



    # set self.line
    # [[[x0,y0],[x1,y1]] # as 1 line,[],[]]
    def get_data(self,data):
        if data is None or len(data) == 0:
            print('get_data err')
            return False
        tmp = []
        for i in data:
            if len(i) == 2:
                if len(i[0]) == 2 and len(i[1]) == 2:
                    tmp.append(i)
                else:
                    return False
            else:
                return False
        if len(tmp) > 0:
            self.line = tmp                
            return True
        return False
                       


    # self.left_top,self.right_bottom from self.line
    def cal_point(self):
        x0 = 0
        y0 = 0
        x1 = 0
        y1 = 0
        if len(self.line) == 0:
            return False
        try:
            for i,j in enumerate(self.line):
                if len(j) != 2:
                    return False
                if i == 0:
                    x0 = j[0][0]
                    y0 = j[0][1]
                    x1 = j[1][0]
                    y1 = j[1][1]
                else:
                    if x0 > j[0][0]:
                        x0 = j[0][0]
                    if y0 > j[0][1]:
                        y0 = j[0][1]
                    if x1 < j[1][0]:
                        x1 = j[1][0]
                    if y1 < j[1][1]:
                        y1 = j[1][1]
        except:
            return False
        
        self.left_top['x'] = x0
        self.left_top['y'] = y0
        self.right_bottom['x'] = x1
        self.right_bottom['y'] = y1
        return True
                       
                
    # return:[[0,True/False],[,],[,]]
    # or None
    def cal_line(self,y):
        if len(self.line) == 0:
            return None
        #result = {'num':0,'x_l':0,'x_r':0}
        if y < self.left_top['y'] or y > self.right_bottom['y']:
            return None
        
        x1 = 0
        y1 = 0
        x2 = 0
        y2 = 0
        # result = []
        x = []

        for i in self.line:
            x1 = i[0][0]    #i[0]
            y1 = i[0][1]    #i[1]
            x2 = i[1][0]    #i[2]
            y2 = i[1][1]    #i[3]
            if y1 <= y <= y2 or y2 <= y <= y1:  # have
                #tmp = {}    # {'x':0,'y':y,'state':'valid'}
                index_x = x2 - x1
                index_y = y2 - y1
                
                tmp = None
                if index_y == 0:    # 0 degree,have 2 point(???)
                    if index_x == 0:
                        return None
                    if x1 > x2:
                        x1,x2 = x2,x1
                    #--------------------
                    flag = 0
                    for i in x:
                        if i[0] == x1:
                            i[1] = False
                            flag = 1
                            break
                    if flag == 0:
                        x.append([x1,False])
                    #    
                    flag = 0
                    for i in x:
                        if i[0] == x2:
                            i[1] = True
                            flag = 1
                            break
                    if flag == 0:
                        x.append([x2,True])
                    x = sorted(x,key = lambda s:s[0])
                    print('x1,x2:',x1,x2)###
                else:
                    if y == y1:
                        tmp = x1
                    elif y == y2:
                        tmp = x2
                    else:
                        tmp = x1 + int((index_x / index_y) * (y - y1))
                 
                if tmp != None:
                    flag = 0
                    for i in x:
                        if tmp == i[0]:
                            #i[1] = True
                            flag = 1
                    if flag == 0:
                        x.append([tmp,True])
                        x = sorted(x,key = lambda s:s[0])
        if len(x) == 0:
            return None
        
        x[-1][1] = False
        return x

    
    # set self.data
    # [{'y':0,'x_data':cal_line()} # as 1 line,{},{}]
    def cal_all_line(self,index):
        if len(self.line) == 0:
            return False
        
        tmp_y0 = self.left_top['y']
        tmp_y1 = self.right_bottom['y']

        if tmp_y0 >= tmp_y1:
            return False
        tmp_data = []
        while tmp_y0 <= tmp_y1:
            x = self.cal_line(tmp_y0)
            if x != None:
                print(x)###
                tmp = {}   
                tmp['y'] = tmp_y0
                tmp['x_data'] = x
                tmp_data.append(tmp)
            tmp_y0 += index
            
        if len(tmp_data) > 0:
            self.data = tmp_data
            return True
        return False
            

    # set self.base_station
    # [[{'x':0,'y':0,'color':**},{},{},{}]  # as 1 line points
    # []
    # []
    # []]
    def cal_device_XY(self,index):
        if len(self.data) == 0:
            print('self.data empty')
            return False
        size = self.size()
        length = size.width()

        tmp_all = []
        for i in self.data:
            if i == None:
                continue
            y = i['y']
            if len(i['x_data']) == 0:
                continue
            
            tmp_data = []
            start = i['x_data'][0][0]

            # before
            if start > 0:
                count = 0
                while count < start:
                    bs_point = {}
                    bs_point['x'] = count
                    bs_point['y'] = y
                    bs_point['color'] = self.BK_color
                    tmp_data.append(bs_point)
                    count += index
            else:
                count = 0
                
            if i['x_data'][0][1] == True:
                color = self.BS_color
            else:
                color = self.BK_color
        
            for m in i['x_data'][1:]:
                current = m[0]    
                while count < current:
                    bs_point = {}
                    bs_point['x'] = count
                    bs_point['y'] = y
                    if count == start:
                        bs_point['color'] = self.BK_color
                    else:
                        bs_point['color'] = color
                    tmp_data.append(bs_point)
                    count += index
                start = current
                
                if m[1] == True:
                    color = self.BS_color
                else:
                    color = self.BK_color
                    
            #if count <= current:
            color = self.BK_color
            bs_point = {}
            bs_point['x'] = count
            bs_point['y'] = y
            bs_point['color'] = color
            tmp_data.append(bs_point)
            tmp_all.append(tmp_data)

        if len(tmp_all) > 0:
            for i in tmp_all:
                for j in i:
                    j['high'] = self.high
                    
            self.base_station = tmp_all    
            print('len:',len(self.base_station))#
            for i in self.base_station:
                print(len(i))
            return True
        return False




    # change one of self.base_station
    # [[{'x':0,'y':0,'color':**},{},{},{}]  # as 1 line points
    # []
    # []
    # []]
    def change_one_XY(self,index,x,y,high,base_status):
        if len(index) != 2:
            print('index err')
            return False
        else:
            m,n = index

        if x < 0 or y < 0 or high < 0:
            return False

        if base_status == True:
            tmp = self.BS_color
        else:
            tmp = self.BK_color
        
        size = self.size()
        length = size.width()

        if len(self.base_station) == 0:
            print('self.base_station empty')
            return False

        try:
            if len(self.base_station) > m:
                if len(self.base_station[m]) > n:
                    self.base_station[m][n]['x'] = x
                    self.base_station[m][n]['y'] = y
                    self.base_station[m][n]['high'] = high
                    self.base_station[m][n]['color'] = tmp
                    return True
            return False
        except:
            return False
        


    # show points of base station from self.base_station
    def show_base_station(self,qp,index):
        if len(self.base_station) == 0:
            print('self.base_station empty')
            return
    
        pen = QPen(self.BK_color,index,Qt.DashLine)  # self.POINT_WIDTH
        color = self.BK_color
        pen.setColor(color)
        qp.setPen(pen)

        if self.value_zoom > 0:
            tmp = self.value_zoom
        else:
            tmp = 1
            
        for j in self.base_station:
            if len(j) == 0:
                continue
            for i in j:
                try:
                    x = i['x']
                    y = i['y']
                    if color != i['color']:
                        color = i['color']
                        pen.setColor(color)
                        qp.setPen(pen)
                    qp.drawPoint(x / tmp,y / tmp)
                except:
                    print('self.base_station err')
                    return
        ############
        pen = QPen(self.BS_color,1,Qt.DashLine)  # self.POINT_WIDTH
        #brush = QBrush(Qt.SolidPattern)
        brush = QLinearGradient(0,0,10,10)
        brush.setColorAt(0.0,Qt.white)
        brush.setColorAt(0.1,color)
        brush.setColorAt(1.0,Qt.yellow)

        #
        '''
        color = self.BS_color
        pen.setColor(color)
        qp.setBrush(brush)
        qp.setPen(pen)
        
        for j in self.base_station:
            if len(j) == 0:
                continue
            for i in j:
                try:
                    x = i['x']
                    y = i['y']
                    if i['color'] == self.BS_color:
                        ###
                        qp.drawEllipse(x / tmp - i['high'] / 2,y / tmp - i['high'] / 2,i['high'],i['high'])
                        ###
                except:
                    print('self.base_station err')
                    return
        '''


    # in self.base_station {}, add ['addr']
    def cal_addr(self):
        if len(self.base_station) == 0:
            print('self.base_station empty')
            return
        max_group = 7
        max_count = 31
        group = [0,1]
        count = [0,0]

        for j in self.base_station:
            if len(j) == 0:
                continue
            flag = 0            
            for m,n in enumerate(j):
                try:
                    if n['color'] == self.BS_color:
                        index = m % 2
                        n['addr'] = (count[index] & 0x1f) | ((group[index] << 5) & 0xe0)
                        flag = 1
                        if count[index] < max_count:
                            count[index] += 1
                        else:
                            group[index] = max(group) + 1
                            if group[index] > max_group:
                                print('base station address is over 255')
                                if min(group) == 0:
                                    group[index] = 1
                                else:
                                    group[index] = 0
                            count[index] = 0
                except:
                    print('self.cal_addr err')
                    return
            if flag == 1:
                group = list(reversed(group))
                count = list(reversed(count))



    # show self.base_station {}, ['addr']
    def show_addr(self,qp):
        if len(self.base_station) == 0:
            print('self.base_station empty')
            return
        print('show_addr')
        pen = QPen(self.BS_color,2,Qt.DashLine)  # self.POINT_WIDTH
        qp.setPen(pen)
        qp.setFont(QFont('Decorative',10))
        
        if self.value_zoom > 0:
            tmp = self.value_zoom
        else:
            tmp = 1
            
        for j in self.base_station:
            if len(j) == 0:
                continue
            
            for i in j:
                try:
                    if i['color'] == self.BS_color:
                        addr_str = i['addr']
                        addr_str = str((addr_str >> 5) & 0x07) + '-' + str(addr_str & 0x1f)
                        x = i['x'] / tmp
                        y = i['y'] / tmp + 5
                        if x > 0:
                            x -= 10
                        qp.drawText(QRect(x,y,40,16),Qt.AlignLeft,addr_str) # high is 16
                except:
                    print('self.show_addr err')
                    return
        

    
    
    def draw(self,qp):
        pen = QPen(Qt.black,3,Qt.SolidLine)
        qp.setPen(pen) # Qt.red
        size = self.size()
        #size.width()
        #size.height()
        print('size:',size)
        '''
        qp.drawPoint(30,20)
        pen.setStyle(Qt.DashLine)#DashLine,DashDotLine,DotLine,DashDotDotLine,CustomDashLine
        qp.setPen(pen)
        qp.drawLine(20,40,200,40)
        pen.setStyle(Qt.DashDotDotLine)
        pen.setColor(Qt.red)
        qp.setPen(pen)
        qp.drawRect(10,15,90,60)
        '''
        #############
        pen.setColor(Qt.blue)
        qp.setPen(pen)

        #--------------------- draw line -----------------
        if len(self.line) == 0:
            return

        if self.value_zoom > 0:
            tmp_zoom = self.value_zoom
        else:
            tmp_zoom = 1
        for i in self.line:
            if self.value_zoom > 0:
                qp.drawLine(i[0][0] / tmp_zoom,i[0][1] / tmp_zoom,i[1][0] / tmp_zoom,i[1][1] / tmp_zoom)

        ################
        pen.setColor(Qt.red)
        qp.setPen(pen)
        qp.drawLine(1300 - 100,900,1300 + 100,900)
        qp.drawLine(1300,900 - 100,1300,900 + 100)
        ################
        #------- self.left_top,self.right_bottom ---------
        self.cal_point()
        pen.setColor(Qt.red)
        qp.setPen(pen)
        qp.drawPoint(self.left_top['x'] / tmp_zoom,self.left_top['y'] / tmp_zoom)
        qp.drawPoint(self.right_bottom['x'] / tmp_zoom,self.right_bottom['y'] / tmp_zoom)
            
        #-------------- show_base_station ----------------
        self.show_base_station(qp,self.POINT_WIDTH)
            
        #------------------- cal addr --------------------
        if self.show_addr_flag == 1:
            #self.cal_addr()
            self.show_addr(qp)  # show addr
            self.show_addr_flag = 0

        

    def mousePressEvent(self,event):
        #print('press',event.x(),event.y(),event.pos())##
        x = event.x()
        y = event.y()

        if self.value_zoom > 0:
            tmp = self.value_zoom
        else:
            tmp = 1
            
        try:
            if len(self.base_station) == 0:
                return
            for m,j in enumerate(self.base_station):
                if len(j) == 0:
                    continue
                for n,i in enumerate(j):
                    if abs(x - i['x'] / tmp) <= self.POINT_WIDTH / 2 and abs(y - i['y'] / tmp) <= self.POINT_WIDTH / 2:
                        color = i['color']
                        if color == self.BK_color:
                            tmp = False
                        else:
                            tmp = True
                        index = (m,n)
                        self.window.set_base_station(index,i['x'],i['y'],i['high'],tmp)
                        break
        except:
            return
        #-----------------------------
        print('cal_addr')
        if self.cal_addr() == False:
            return
        self.show_addr_flag = 1
        self.update()
                
        
    
    #def mouseReleaseEvent(self,event):
    #   print('release',event.x(),event.y(),event.pos())


    




if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_window = My_Window()
    my_window.show()
    sys.exit(app.exec_())

    












'''
self.setMouseTracking(False)

def paintEvent(self.event):
    

def mouseMoveEvent(self.event):
    pos_tmp = (event.pos().x(), event.pos().y())
    self.update()
'''



