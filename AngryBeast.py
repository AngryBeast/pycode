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
SendNumBack = [-20,-20,-20,-20]
SendNumSlow = [20,20,20,20]
SendNumGo = [40,40,40,40]
SendNumStop = [0,0,0,0]
debugLeida = 1
debugCar = 1
avoidFlag = 0

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
        if debugCar == 1:
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
        print('turn ',angle)
        if (angle < 0):
            self.SendDuty(SendNumLeft)
        else:
            self.SendDuty(SendNumRight)
        if (abs(angle) < 91):
            time.sleep(abs(angle) * 0.00555)
        else:
            if abs(angle) < 145:
                time.sleep(abs(angle) * 0.00444)
            else:
                time.sleep(abs(angle) * 0.00422)


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
        self.MoveDataX = np.array([])
        self.MoveDataY = np.array([])

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

    # def CheakIfReach(self, CarLoca, TargetLoca, precision = 0.10): #判断是否到达Targe
    #     if abs(CarLoca.x - TargetLoca.x) > precision:
    #         return False
    #     if abs(CarLoca.y - TargetLoca.y) > precision:
    #         return False
    #     return True
    def CheakIfReach(self, CarLoca, TargetLoca, precision = 0.10): #判断是否到达Targe
        if (CarLoca.x - TargetLoca.x)**2 + (CarLoca.y - TargetLoca.y)**2 < precision ** 2:
            return True
        return False

    
    def CheakAngleLegal(self, Angle):
        if Angle > 180:
            Angle = 180 - Angle
        if Angle < -180:
            Angle = -180 - Angle
        return Angle

    def JudgeDirection(self, CarLoca, TargetLoca):
        dx1 = TargetLoca.x - CarLoca.x
        dy1 = TargetLoca.y - CarLoca.y
        TempAngle = math.atan2(abs(dy1), abs(dx1))
        # TempAngle = math.atan2(abs(dx1), abs(dy1))
        TempAngle = int(TempAngle * 180/math.pi)
        #print('x1',dx1,'y1',dy1,'temp:',TempAngle)
        if dx1 > 0:  
            if dy1 < 0:
                angle = 90 + TempAngle      #4
            if dy1 >= 0:
                angle = 90 - TempAngle      #1
        if dx1 < 0: 
            if dy1 < 0:
                angle = -180 + TempAngle    #3
            if dy1 >= 0:
                angle = -90 + TempAngle     #2
        print(angle)
        return angle

    def CheackIfNeedTurn(self, TargetAngle, NowAngle):
        if abs(TargetAngle - NowAngle) > 10:
            if abs(TargetAngle) + abs(NowAngle) > 180:
                if TargetAngle * NowAngle < 0:
                    if TargetAngle < 0:
                        return -360 - TargetAngle + NowAngle
                    if NowAngle < 0:
                        return -360 - NowAngle + TargetAngle
            return TargetAngle - NowAngle
        else:
            return 0


    def ClearLineFitData(self):
        self.MoveDataX = np.array([])
        self.MoveDataY = np.array([])

    def lineFit(self, per, ptpNum, CarLoca):
        #print('lineFit size',self.MoveDataX.size)
        if self.MoveDataX.size != per:
            self.MoveDataX = np.append(self.MoveDataX,CarLoca.x)
            self.MoveDataY = np.append(self.MoveDataY,CarLoca.y)
        else:
            self.MoveDataX = np.delete(self.MoveDataX, 0)
            self.MoveDataY = np.delete(self.MoveDataY, 0)
            self.MoveDataX = np.append(self.MoveDataX,CarLoca.x)
            self.MoveDataY = np.append(self.MoveDataY,CarLoca.y)
            print('x ptp', np.ptp(self.MoveDataX))
            print('y ptp', np.ptp(self.MoveDataY))
            # if np.ptp(self.MoveDataX) > ptpNum or np.ptp(self.MoveDataY) > ptpNum:
            if np.ptp(self.MoveDataX) > ptpNum or np.ptp(self.MoveDataY) > ptpNum:
                avoidFlag = 0
                print('x',self.MoveDataX)
                print('y',self.MoveDataY)
                A = np.stack((self.MoveDataX, np.ones(per)), axis=1)
                b = np.array(self.MoveDataY).reshape((per, 1))
                theta, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
                theta = theta.flatten()
                k = theta[0]
                b_ = theta[1]
                #print("拟合结果为: y={:.4f}*x+{:.4f}".format(k, b_))
                angle = abs(np.degrees(np.arctan(k)))
                #print("计算出结果为",angle)
                if self.MoveDataX[per- 1] < self.MoveDataX[0]:
                    if self.MoveDataY[per- 1] < self.MoveDataY[0]:
                        angle = -180 + angle
                    if self.MoveDataY[per- 1] >= self.MoveDataY[0]:
                        angle = -90 + angle
                if self.MoveDataX[per- 1] >= self.MoveDataX[0]:
                    if self.MoveDataY[per- 1] < self.MoveDataY[0]:
                        angle = 90 + angle
                    if self.MoveDataY[per- 1] >= self.MoveDataY[0]:
                        angle = 90 - angle
                return float(angle)

    def LeidaJudgeData(self,MySerial, CarLoca, TargetLoca):
        lock.acquire()
        #print('process acq')
        deep_data_step1 = np.where(deep_data < 10000,deep_data,0)          #数组切片取最中间，且排除异常值或不考虑值
        if np.mean(deep_data_step1) > 30:#防止数组为空的状态
            for i in range(2):
                tempData = deep_data_step1[ 20:35 , 50 + 30*i:80 + 30*i]
                #print(tempData)
                Precision = np.mean(tempData)
                CheackStop = np.argwhere(tempData==0)
                print(Precision)

                if (Precision < 500 or CheackStop.size > 350):
                #if Precision < 300:
                    avoidFlag = 1
                    print('back')
                    self.ClearLineFitData()
                    lock.release()
                    MySerial.SendDuty(SendNumBack)
                    #print('back release')
                    time.sleep(0.3)
                    MySerial.SerialSendData('S')
                    time.sleep(1)
                    return 0
                if (Precision < 700):
                    if self.CheakIfReach(CarLoca, TargetLoca, 0.3) == False:
                        avoidFlag = 1
                        LeftData = deep_data_step1[20:35 , 20:50]
                        LeftPrecision = np.mean(LeftData)
                        RightData = deep_data_step1[20:35 , 110:140]
                        RightPrecision = np.mean(RightData)
                        if (LeftPrecision > RightPrecision):
                            lock.release()
                            #print('turnL release')
                            MySerial.TurnAngle(-30)
                            #print('T left')
                            self.ClearLineFitData()
                            # MySerial.SendDuty(SendNumSlow)
                            # time.sleep(0.2)
                            return -30
                        else:
                            lock.release()
                            #print('turnR release')
                            MySerial.TurnAngle(30)
                            #print('T Right')
                            self.ClearLineFitData()
                            # MySerial.SendDuty(SendNumSlow)
                            # time.sleep(0.2)
                            return 30
            #print('zhi zou')
        #print('Go release')
        lock.release() 
        return 0


class MyQtThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Ser = MySerial()
        self.TCPC = MyTCPClient('192.168.124.4')
        #self.TCPC = MyTCPClient('192.168.43.61')
        self.CarLocation = LocationStruct('car', 0.0, 0.0, 0.0)
        self.TargetLocation = LocationStruct('Target', 0.0, 0.0, 0.0)
        self.RecvTargetFlag = False
        self.DataPro = MyDataProcess()
        self.angle = 0

    def run(self):
        self.Ser.SerialSendData('S')
        while True:
            reciveData = self.TCPC.TCPreceiveData()     #接收激光雷达TCP数据
            #print(reciveData)
            self.angle = self.DataPro.CheakAngleLegal(self.angle)   #判断当前角度是否可逆转符号
            if self.DataPro.UpdateLocation(reciveData, self.CarLocation, self.TargetLocation) == True: 
                #返回TRUE 代表 Target改变
                self.RecvTargetFlag = True
                self.DataPro.ClearLineFitData()
            


            
            if self.RecvTargetFlag == True:         #已接收到目的地坐标
                if self.DataPro.CheakIfReach(self.CarLocation, self.TargetLocation,0.2) == True:
                    #判断是否到达目标点 已到达为True
                    self.Ser.SerialSendData('S')
                    self.RecvTargetFlag = False
                    print('arrive')
                else:
                    needAngle = self.DataPro.JudgeDirection(self.CarLocation, self.TargetLocation)
                    self.CarLocation.printSelfData()
                    
                    #获取前进所需角度
                    #print('now',self.angle,'need',needAngle)

                        
                    #print(needAngle)
                    #根据位置到目标的斜率判断是否需要转向
                    TempAngle =  self.DataPro.CheackIfNeedTurn(needAngle, self.angle)
                    if (TempAngle != 0)  and (avoidFlag == 0) :
                        self.Ser.TurnAngle(TempAngle)          #旋转所需角度
                        self.angle = needAngle
                        self.DataPro.ClearLineFitData()
                    
                    GoAngle = self.DataPro.lineFit(7,0.1,self.CarLocation)
                    #直线拟合 判断当前行进方向的真实角度
                    if GoAngle != None:
                        print('Go',GoAngle)
                        if abs(self.angle - GoAngle) < 30:
                            testAngle = (self.angle - GoAngle) / 2
                            TempAngle =  self.DataPro.CheackIfNeedTurn(self.angle,GoAngle - testAngle)
                            if (TempAngle != 0):         #修正前进角度
                                self.Ser.TurnAngle(TempAngle)          
                                self.angle = GoAngle
                                self.DataPro.ClearLineFitData()

                    if debugLeida == 1:
                        #print('judge leida')
                        tempAngle = self.DataPro.LeidaJudgeData(self.Ser, self.CarLocation, self.TargetLocation)
                        #判断是否有障碍物需要进行避障
                        if tempAngle != 0:
                            self.angle += tempAngle
                            self.DataPro.ClearLineFitData()
                            # self.Ser.SendDuty(SendNumSlow)
                            # time.sleep(0.5)
                    self.Ser.SendDuty(SendNumSlow)
            time.sleep(0.05)    
            
            



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
            lock.acquire()
            #print('qcquire')
            for num in revstr:
                floatnum = re.findall(r"\d+\.?\d*",num)
                if (len(floatnum) == 2):
                    
                    tempNum = int(floatnum[0])
                    deep_data[int(tempNum/160)][tempNum%160] = floatnum[1]
                    lastNum = tempNum
                    
                    # if (tempNum == 9599):
                    #     print('done')
            #print('getData release')
            lock.release()
            time.sleep(0.05)
            
def main():
    threadQt = MyQtThread()
    if debugLeida == 1:
        threadTcp = MyTcpThread()
        threadTcp.start()
    threadQt.start()
    

if __name__ == '__main__':
    main()
