

# import serial
# import time
# import sys

# def main():
#     i = 0
#     while True:
#         i += 1
#         count = ser.write("Hello World".encode("gbk"))
#         #count = ser.inWaiting()
#         if count != 0:
#             recv = ser.read(count)
#             print("recv:" + recv)
#         ser.flushInput()
#         time.sleep(0.1)


# if __name__ == '__main__':
#     try:
#         ser = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
#         if ser.isOpen == False:
#             ser.open()
#         #ser.write(b"AG")
#         ser.write("AG".encode("gbk"))
#         #main()
#     except KeyboardInterrupt:
#         if ser != None:
#             ser.close()


# import serial

# ted = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
# ted.write("AS\n".encode("gbk"))

import serial
import time
import sys
import os

def main():
    i = 0
    while True:
        # msg = input()
        # msg += '\n'
        # ser.write(msg.encode("gbk"))
        # ser.flushInput()
        #time.sleep(1)
        # msg = input()
        # msg += '\n'
        # ser.write(msg.encode("gbk"))
        # ser.write("AG\n".encode("gbk"))
        # time.sleep(0.05)
        # ser.write("AS\n".encode("gbk"))
        # time.sleep(0.05)
        ser.flushInput()


if __name__ == '__main__':
    try:
        ser = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
        if ser.isOpen == False:
            ser.open()
        #ser.write(b"AG")
        ser.write("AS\n".encode("gbk"))
        main()
    except KeyboardInterrupt:
        if ser != None:
            ser.close()