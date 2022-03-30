# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 17:57:35 2022

@author: physics-svc-mkdata
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize

ratio = [0.5046, 0.5051, 0.5083, 0.5115, 0.5129, 0.5170, 0.5202, 0.5235]
pressure = [419.3, 421.7, 436.9, 452.2, 458.8, 477.6, 492.0, 506.8]

def quadratic(x, a0, a1, a2):
    return a0 + a1*x + a2*x**2

coef, pcov = optimize.curve_fit(quadratic, ratio, pressure)

x = np.linspace(np.min(ratio), np.max(ratio), 100)

plt.figure()
plt.scatter(ratio, pressure)
plt.plot(x, quadratic(x, *coef))

print('fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(coef))