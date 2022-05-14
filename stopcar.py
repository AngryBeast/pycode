import serial
import time

def getMsg(SendNum):
    msg = 'A' 
    for num in SendNum:
        print(num)
        if num >= 0:
            msg += '+'
        else:
            msg += '-'
            num = -num
        msg += chr(num + 41)
    msg += '\n'
    print(msg)
    return msg

ted = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
# SendNum = [40,40,40,40]
# msg = getMsg(SendNum)
# ted.write(msg.encode("gbk"))
# time.sleep(3)
#0.5S 90度
SendNum = [40,-20,50,-20]
msg = getMsg(SendNum)
ted.write(msg.encode("gbk"))
time.sleep(0.27)
SendNum = [0,0,0,0]
msg = getMsg(SendNum)
ted.write(msg.encode("gbk"))