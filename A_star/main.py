# main.py
# 初始化open_set和close_set；
# 将起点加入open_set中，并设置优先级为0（优先级最高）；
# 如果open_set不为空，则从open_set中选取优先级最高的节点n：
    # 如果节点n为终点，则：
        # 从终点开始逐步追踪parent节点，一直达到起点；
        # 返回找到的结果路径，算法结束；
    # 如果节点n不是终点，则：
        # 将节点n从open_set中删除，并加入close_set中；
        # 遍历节点n所有的邻近节点：
            # 如果邻近节点m在close_set中，则：
                # 跳过，选取下一个邻近节点
            # 如果邻近节点m也不在open_set中，则：
                # 设置节点m的parent为节点n
                # 计算节点m的优先级
                # 将节点m加入open_set中
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle

import random_map
import a_star

plt.figure(figsize=(5, 5))

map = random_map.RandomMap() 

ax = plt.gca()
ax.set_xlim([0, map.size]) 
ax.set_ylim([0, map.size])

for i in range(map.size): 
    for j in range(map.size):
        if map.IsObstacle(i,j):
            rec = Rectangle((i, j), width=1, height=1, color='gray')
            ax.add_patch(rec)
        else:
            rec = Rectangle((i, j), width=1, height=1, edgecolor='gray', facecolor='w')
            ax.add_patch(rec)

rec = Rectangle((0, 0), width = 1, height = 1, facecolor='b')
ax.add_patch(rec) 

rec = Rectangle((map.size-1, map.size-1), width = 1, height = 1, facecolor='r')
ax.add_patch(rec) 

plt.axis('equal') 
plt.axis('off')
plt.tight_layout()
#plt.show()

a_star = a_star.AStar(map)
a_star.RunAndSaveImage(ax, plt) 