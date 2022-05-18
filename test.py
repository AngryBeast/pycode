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
SendNumBack = [-40,-40,-40,-40]
SendNumSlow = [20,20,20,20]
SendNumGo = [40,40,40,40]

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

    def TurnAngle(self, angle):
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
        tempangle = math.atan2(dx1, dy1)
        tempangle = int(tempangle * 180/math.pi)
        return tempangle

    # def LeidaJudgeData(self):
    #     lock.acquire()
    #     # for i in range(60):
    #     #     print (i)
    #     #     print(np.where(deep_data > 60000))
    #         # print(deep_data[i])

    #     tempData = np.where(deep_data < 10000)
    #     #print(len(tempData[0]))
    #     for i in range(len(tempData[0])):
    #         # msg += '['+tempData[0][i]+','+tempData[1][i]+']'
    #         # print(msg)
    #         print(tempData[0][i],tempData[1][i])
        
    #     #print(np.where(deep_data > 60000))
    #     lock.release()

    # def LeidaJudgeData(self,MySerial, CarLoca, TargetLoca):
    #     lock.acquire()
    #     deep_data_step1 = np.where(deep_data < 10000,deep_data,0)          #数组切片取最中间，且排除异常值或不考虑值
    #     np.save("filename.npy",deep_data_step1)
    #     countPrecision = np.zeros((3,2),dtype = float)
    #     countPtp = np.zeros((3,2),dtype = int)
    #     for i in range(3):
    #         for j in range(2):
    #             tempData = deep_data_step1[20*i:20*(i+1),39+40*j:39+40*(j+1)]
    #             print('i',i,'j',j)
    #             #print(tempData)
    #             countPrecision[i][j] = np.mean(tempData)
    #             countPtp[i][j] = np.ptp(tempData)
    #     print(countPrecision)
    #     print(countPtp)
    #     lock.release()
    #     return

        #         if (countPrecision[i][j] < 300):
        #             #back
        #             MySerial.SendDuty(SendNumBack)
        #             time.leep(0.05)
        #             lock.release()
        #             print('need back')
        #             return 
        #         if (countPrecision[i][j] < 500 and countPrecision[i][j] > 300):
        #             if (self.CheakIfReach(CarLoca, TargetLoca, 0.3) == False):  #未接近目标 需要额外判断
        #                 tempDataLeft = deep_data_step1[0:40,:]
        #                 tempDataRight = deep_data_step1[120:160,:]
        #                 meanL = np.mean(tempDataLeft)
        #                 meanR = np.mean(tempDataRight)
        #                 if (meanL > meanR):
        #                     print('turn left')
        #                     MySerial.SendDuty(SendNumLeft)
        #                     time.sleep(0.27)
        #                     MySerial.SendDuty(SendNumSlow)
        #                     time.sleep(0.5)
        #                     MySerial.SendDuty(SendNumRight)
        #                     time.sleep(0.27)
        #                 else:
        #                     print('turn right')
        #                     MySerial.SendDuty(SendNumRight)
        #                     time.sleep(0.27)
        #                     MySerial.SendDuty(SendNumSlow)
        #                     time.sleep(0.5)
        #                     MySerial.SendDuty(SendNumLeft)
        #                     time.sleep(0.27)
        #                 lock.release()
        #                 return
        # lock.release()
        #time.sleep(10)

    def LeidaJudgeData(self,MySerial, CarLoca, TargetLoca):
        lock.acquire()
        deep_data_step1 = np.where(deep_data < 10000,deep_data,0)          #数组切片取最中间，且排除异常值或不考虑值
        # countPrecision = np.zeros((3,2),dtype = float)
        # countPtp = np.zeros((3,2),dtype = int)
        # for i in range(3):
        #     for j in range(2):
        #         tempData = deep_data_step1[20*i:20*(i+1),39+40*j:39+40*(j+1)]
        #         print('i',i,'j',j)
        #         #print(tempData)
        #         countPrecision[i][j] = np.mean(tempData)
        #         countPtp[i][j] = np.ptp(tempData)
        tempData = deep_data_step1[ 30:60 , 60:100]
        print(tempData)
        Precision = np.mean(tempData)
        print(Precision)

        if (Precision < 200):
            print('go back')
            MySerial.SendDuty(SendNumBack)
            time.sleep(0.3)
            lock.release()
            return 0
        if (Precision < 500):
            if self.CheakIfReach(CarLoca, TargetLoca, 0.4) == False:
                LeftData = deep_data_step1[30:60 , 30:60]
                LeftPrecision = np.mean(LeftData)
                RightData = deep_data_step1[30:60 , 100:130]
                RightPrecision = np.mean(RightData)
                if (LeftPrecision > RightPrecision):
                    MySerial.TurnAngle(-30)
                    print('T left')
                    lock.release()
                    return -30
                else:
                    MySerial.TurnAngle(30)
                   print('T Right')
                    lock.release()
                    return 30
        print('zhi zou')
        lock.release() 
        return 0

class MyQtThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Ser = MySerial()
        # self.TCPC = MyTCPClient('192.168.124.4')
        self.CarLocation = LocationStruct('car', 0.0, 0.0, 0.0)
        self.TargetLocation = LocationStruct('Target', 4.0, 4.0, 4.0)
        # self.StartLocation = LocationStruct('Start', 0.0, 0.0, 0.0)
        # self.RecvTargetFlag = False
        self.DataPro = MyDataProcess()
        self.angle = 0

    def run(self):
        while True:
            self.angle += self.DataPro.LeidaJudgeData(self.Ser, self.CarLocation, self.TargetLocation)
            time.sleep(0.1)



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
                    # if (tempNum == 9599):
                    #     print('done')

def main():
    threadQt = MyQtThread()
    if debugLeida == 1:
        threadTcp = MyTcpThread()
        threadTcp.start()
    threadQt.start()
    

if __name__ == '__main__':
    main()
