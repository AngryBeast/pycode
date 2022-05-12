

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
# ted.write("Hello World".encode("gbk"))
# ted.read(11)

import serial
import time
import sys

def main():
    i = 0
    while True:
        ser.write("AG\n".encode("gbk"))
        ser.flushInput()
        time.sleep(1)


if __name__ == '__main__':
    try:
        ser = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
        if ser.isOpen == False:
            ser.open()
        #ser.write(b"AG")
        ser.write("AG\n".encode("gbk"))
        main()
    except KeyboardInterrupt:
        if ser != None:
            ser.close()