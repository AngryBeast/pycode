#from socket import *
import socket
import serial
import time
import re
import threading
import time
import numpy as np
import random
import math


deep_data = np.zeros((60,160),dtype = int)
lock = threading.Lock()
SendNumLeft = [40,-20,50,-20]
SendNumRight = [-20,40,-20,50]

debugLeida = 1

#串口发送类
class MySerial:
    def __init__(self):
        try:
            self.ser = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
            if self.ser.isOpen == False:
                self.ser.open()
        except KeyboardInterrupt:
            if self.ser != None:
                self.ser.close()

    def SerialSendData(self,str): #发送数据
        str += '\n'
        strData = str.encode("gbk")
        self.ser.write(strData)
    
    def SendDuty(self,SendData): #发送占空比 SendData为数组
        if len(SendData) == 4:
            msg = 'A' 
            for num in SendData:
                if num >= 0:
                    msg += '+'
                else:
                    msg += '-'
                    num = -num
                msg += chr(num + 41)
            self.SerialSendData(msg)

    def TurnAngle(self,angle):
        if (angle < 0):
            self.SendDuty(SendNumLeft)
        else:
            self.SendDuty(SendNumRight)
        time.sleep(abs(angle) * 0.00555)


#TCP连接， 接收TCP消息
class MyTCPClient:
    def __init__(self,ip,port=8888):
        ADDRESS = (ip, port)
        self.BUFSIZ = 1024
        self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClientSocket.connect(ADDRESS)

    def TCPreceiveData(self): #接收数据，保存在data中
        data, ADDR = self.tcpClientSocket.recvfrom(self.BUFSIZ)
        if not data:
            print('error')
        return data.decode('utf-8')
    
    def SendData(self,msg):
        self.tcpClientSocket.sendall(msg)


#坐标数据类
class LocationStruct:
    def __init__(self,name,x,y,z):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
    
    def printSelfData(self):
        print('name:%s, X:%f, Y:%f, Z:%f' %(self.name,self.x, self.y ,self.z))

#对数据进行处理
class MyDataProcess:
    def __init__(self):
        self = self

    def UpdateLocation(self, Recvdata, CarLoca, TargetLoca):
        if Recvdata.find('T:') != -1: #目标坐标信息
            x = re.findall(r'-?\d+\.?\d*',Recvdata)
            if TargetLoca.name == 'Target':
                TargetLoca.x = float(x[0])
                TargetLoca.y = float(x[1])
                TargetLoca.z = float(x[2])
                #TargetLoca.printSelfData()
            return True
        if Recvdata.find('D:') != -1: #标签坐标信息
            x = re.findall(r"-?\d+\.?\d*",Recvdata)
            if CarLoca.name == 'car':
                CarLoca.x = float(x[0])
                CarLoca.y = float(x[1])
                CarLoca.z = float(x[2])
                #CarLoca.printSelfData()
            return False

        if Recvdata.find('S') != -1:
            TargetLoca.x = CarLoca.x
            TargetLoca.y = CarLoca.y
            TargetLoca.z = CarLoca.z
            return False

    def CheakIfReach(self, CarLoca, TargetLoca, precision = 0.10): #判断是否到达Targe
        if abs(CarLoca.x - TargetLoca.x) > precision:
            return False
        if abs(CarLoca.y - TargetLoca.y) > precision:
            return False
        return True
    
    def JudgeDirection(self, CarLoca, TargetLoca):
        dx1 = TargetLoca.x - CarLoca.x
        dy1 = TargetLoca.y - CarLoca.y
        angle = math.atan2(dx1, dy1)
        angle = int(angle * 180/math.pi)
        return angle

    def LeidaJudgeData(self):
        lock.acquire()
        for i in range(60):
            print(deep_data[i])
        lock.release()


class MyQtThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Ser = MySerial()
        self.TCPC = MyTCPClient('192.168.124.4')
        self.CarLocation = LocationStruct('car', 0.0, 0.0, 0.0)
        self.TargetLocation = LocationStruct('Target', 0.0, 0.0, 0.0)
        self.StartLocation = LocationStruct('Start', 0.0, 0.0, 0.0)
        self.RecvTargetFlag = False
        self.DataPro = MyDataProcess()
        self.angle = 0

    def run(self):
        self.Ser.SerialSendData('S')
        while True:
            reciveData = self.TCPC.TCPreceiveData()
            #print(reciveData)
            if self.DataPro.UpdateLocation(reciveData, self.CarLocation, self.TargetLocation) == True: #返回TRUE 代表 Target改变
                self.CarLocation.printSelfData()
                self.StartLocation = self.CarLocation
                self.RecvTargetFlag = True
            self.CarLocation.printSelfData()
            self.TargetLocation.printSelfData()
            if self.DataPro.CheakIfReach(self.CarLocation, self.TargetLocation,0.2) == True:     #已到达Target
                self.Ser.SerialSendData('S')
                self.StartLocation = self.CarLocation
                self.RecvTargetFlag = False

            else:
                #进行路径规划
                #发送小车路径指令
                if self.RecvTargetFlag == True:
                    print('not reach')
                    needAngle = self.DataPro.JudgeDirection(self.CarLocation, self.TargetLocation)
                    print(needAngle)
                    if (abs(needAngle - self.angle) > 5):
                        self.Ser.TurnAngle(needAngle - self.angle)
                        self.angle = needAngle
                    
                    if debugLeida == 1:
                        self.DataPro.LeidaJudgeData()
                    SendNum = [40,40,40,40]
                    tempData = [20,20,20,20]
                    self.Ser.SendDuty(tempData)



class MyTcpThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        ADDRESS = ('127.0.0.1', 12345)
        self.BUFSIZ = 102400
        # self.deep_data = np.zeros((60,160),dtype = int)
        self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClientSocket.connect(ADDRESS)

    def run(self):
        while True:
            data, ADDR = self.tcpClientSocket.recvfrom(self.BUFSIZ)
            if not data:
                break
            revstr = data.decode().split('!')

            for num in revstr:
                floatnum = re.findall(r"\d+\.?\d*",num)
                if (len(floatnum) == 2):
                    lock.acquire()
                    tempNum = int(floatnum[0])
                    deep_data[int(tempNum/160)][tempNum%160] = floatnum[1]
                    lastNum = tempNum
                    lock.release()
                    if (tempNum == 9599):
                        print('done')

def main():
    threadQt = MyQtThread()
    if debugLeida == 1:
        threadTcp = MyTcpThread()
        threadTcp.start()
    threadQt.start()
    

if __name__ == '__main__':
    main()
