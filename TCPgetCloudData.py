import socket
import serial
import time
import re
import threading
import time
import numpy as np
import random

class MyTcpThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        ADDRESS = ('127.0.0.1', 12345)
        point_cloud_dataType = np.dtype([('num',int),('x',float),('y',float),('z',float)])
        self.BUFSIZ = 102400
        self.point_cloud_data = np.zeros((9600),dtype = point_cloud_dataType)
        self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClientSocket.connect(ADDRESS)
        for i in range(9600):
            self.point_cloud_data[i][0] = i
            i += 1

    def run(self):
        count = 0
        i = 0
        while True:
            data, ADDR = self.tcpClientSocket.recvfrom(self.BUFSIZ)
            if not data:
                break
            revstr = data.decode().split('!')
            for num in revstr:
                floatnum = re.findall(r"\d+\.?\d*",num)
                if (len(floatnum) == 4):
                    tempNum = int(floatnum[0])
                    if (tempNum == self.point_cloud_data[tempNum][0]):
                        count += 1
                        resultx = float(floatnum[1])
                        resulty = float(floatnum[2])
                        resultz = float(floatnum[3])
                        self.point_cloud_data[tempNum] = (tempNum, resultx, resulty, resultz)
                        #将数据传递出去？
                        if (count == 9599):
                            i+=1
                            count = 0
                            print(i,'done')
                            #print(self.point_cloud_data[random.randint(0,9599)])

                    else:
                        count = 0
                else:
                    i = i
                    #print('loss')

def main():
    threadQt = MyQtThread()
    threadTcp = MyTcpThread()
    threadTcp.start()
    threadQt.start()
    

if __name__ == '__main__':
    main()
