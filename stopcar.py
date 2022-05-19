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

def TurnAngle(self,angle):
    if (angle < 0):
        self.SendDuty(SendNumLeft)
    else:
        self.SendDuty(SendNumRight)
    if (abs(angle) < 45):
        time.sleep(abs(angle) * 0.00555)
    else:
        time.sleep(abs(angle) * 0.0061)

ted = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
# SendNum = [40,40,40,40]
# msg = getMsg(SendNum)
# ted.write(msg.encode("gbk"))
# time.sleep(3)
#0.5S 90度  0.27 45度  0.76  180度
SendNumLef = [40,-20,50,-20]
SendNumRight = [-20,40,-20,50]
msg = getMsg(SendNumLef)
ted.write(msg.encode("gbk"))
time.sleep(0.60)
SendNum = [0,0,0,0]
msg = getMsg(SendNum)
ted.write(msg.encode("gbk"))