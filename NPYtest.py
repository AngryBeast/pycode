
import numpy as np 
# import scipy.optimize as opt


X = np.array([ 8.19, 2.72, 6.39, 8.71, 4.7 , 2.66, 3.78])
Y = np.array([ 7.01, 2.78, 6.47, 6.71, 4.1 , 4.23, 4.05])


SAMPLE_NUM = 7
A = np.stack((X, np.ones(SAMPLE_NUM)), axis=1)

b = np.array(Y).reshape((SAMPLE_NUM, 1))

theta, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
theta = theta.flatten()
a_ = theta[0]
b_ = theta[1]
print("拟合结果为: y={:.4f}*x+{:.4f}".format(a_, b_))

for i in X:
    print(i* a_ + b_)