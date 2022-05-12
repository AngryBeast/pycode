import threading
import time
from socket import *

class TCPrecv(threading.Thread):
    def __init__(self, threadname):
        threading.Thread.__init__(self, name='线程' + threadname)
        HOST = '192.168.8.249'
        PORT = 8888
        BUFSIZ = 1024
        ADDRESS = (HOST, PORT)
        tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        tcpClientSocket.connect(ADDRESS)


    def run(self):
        data, ADDR = tcpClientSocket.recvfrom(BUFSIZ)
        #if not data:
        print("服务器端响应：", data.decode('utf-8'))


if __name__ == "__main__":
    TCPThread = TCPrecv("TCP")
    TCPThread.start()