# coding=utf-8
import pywt
import math
import numpy as np
import matplotlib.pyplot as plt
fs=1000 #采样频率
f1=50   #信号频率
f2=100  #信号频率
totalscale=256
t = np.arange(0,1,1.0/fs)
sig=np.sin(2*math.pi*f1*t)+np.sin(2*math.pi*f2*t)
wcf=pywt.central_frequency('morl') #计算小波中心频率
scale=np.arange(1,totalscale+1,1)     #生成1-256等差数列
cparam=2*wcf*totalscale
scale=cparam/scale           #计算尺度
frequencies = pywt.scale2frequency('morl',scale)#将尺度转换成频率
frequencies=frequencies*fs   #将频率变换成信号真实频率
cwtmatr, freqs = pywt.cwt(sig, scale, 'morl')#求连续小波系数
plt.ylabel('y')
plt.xlabel('x')
plt.pcolormesh(t,frequencies,abs(cwtmatr),vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
plt.colorbar()
plt.show()