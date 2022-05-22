# import math
# def JudgeDirection( x0,y0,x1,y1):
#     dx1 = x1 - x0
#     dy1 = y1 - y0
#     TempAngle = math.atan2(abs(dy1), abs(dx1))
#     # TempAngle = math.atan2(abs(dx1), abs(dy1))
#     TempAngle = int(TempAngle * 180/math.pi)
#     print('x1',dx1,'y1',dy1,'temp:',TempAngle)
#     if dx1 > 0:  #目标点在车的第
#         if dy1 < 0:
#             angle = 90 + TempAngle
#         if dy1 >= 0:
#             angle = 90 - TempAngle
#     if dx1 < 0: #目标点在1 4象限
#         if dy1 < 0:
#             angle = -180 + TempAngle
#         if dy1 >= 0:
#             angle = -90 + TempAngle


#     return angle
# #print(JudgeDirection(0,0,-1,-3))
# print('60 ',JudgeDirection(0,0,-1,1.73))
# print('30 ',JudgeDirection(0,0,-1,1.73/ 3))


a = 120
b = 180
temp = (a - b) / 2
print (a - temp)