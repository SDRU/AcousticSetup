# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 11:05:17 2022

@author: BLOG
"""

import numpy as np
import matplotlib.pyplot as plt

path = "C:/Users/BLOG/Desktop/Carlo/Test1/test_012.lvm"

# with open(path) as f:
data=np.loadtxt(path)
plt.plot(data[:,1])
    