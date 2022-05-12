from socket import *
import numpy as np
import re



HOST = '127.0.0.1'
PORT = 12345
BUFSIZ = 1024
ADDRESS = (HOST, PORT)


tcpClientSocket = socket(AF_INET, SOCK_STREAM)
tcpClientSocket.connect(ADDRESS)



print('start')
count = 0
i = 0
while True:
    data, ADDR = tcpClientSocket.recvfrom(BUFSIZ)
    if not data:
        break
    print(data)

print("链接已断开！")
tcpClientSocket.close()
