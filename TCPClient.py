from socket import *
import numpy as np
import re



HOST = '127.0.0.1'
PORT = 12345
BUFSIZ = 1024
ADDRESS = (HOST, PORT)

point_cloud_dataType = np.dtype([('num',int),('x',float),('y',float),('z',float)])
point_cloud_data = np.zeros((9600),dtype = point_cloud_dataType)

for i in range(9600):
    point_cloud_data[i][0] = i
    i += 1

tcpClientSocket = socket(AF_INET, SOCK_STREAM)
tcpClientSocket.connect(ADDRESS)



print('start')
count = 0
i = 0
while True:
    data, ADDR = tcpClientSocket.recvfrom(BUFSIZ)
    if not data:
        break
    # revstr = data.decode().split('!')
    # for num in revstr:
    #     floatnum = re.findall(r"\d+\.?\d*",num)
    #     if (len(floatnum) == 4):
    #         tempNum = int(floatnum[0])
    #         if (tempNum == point_cloud_data[tempNum][0]):
    #             count += 1
    #             resultx = float(floatnum[1])
    #             resulty = float(floatnum[2])
    #             resultz = float(floatnum[3])
    #             point_cloud_data[tempNum] = (tempNum, resultx, resulty, resultz)

    #             # point_cloud_data[tempNum] = np.array([tempNum, resultx,resulty, resultz])           
    #             # point_cloud_data[tempNum][1] = float(floatnum[1]) 
    #             # point_cloud_data[tempNum][2] = float(floatnum[2]) 
    #             # point_cloud_data[tempNum][3] = float(floatnum[3]) 

    #             if (count == 9599):
    #                 i+=1
    #                 count = 0
    #                 print(i,'done')
    #         else:
    #             count = 0
    #     else:
    #         print('loss')

print("链接已断开！")
tcpClientSocket.close()
