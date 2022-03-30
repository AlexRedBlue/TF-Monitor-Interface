# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 14:50:03 2022

@author: physics-svc-mkdata
"""

import numpy as np
from scipy import interpolate


calibration_directory = r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration"
file_name = "\\08-20-08-26_rvt_calibration_main.dat"
R8_file_name = "\\R8_RT_Curve.dat"
calibration = np.loadtxt(calibration_directory+file_name, delimiter="\t", skiprows=1)
R8_calibration = np.loadtxt(calibration_directory+R8_file_name, delimiter="\t", skiprows=1)

import matplotlib.pyplot as plt
fig, ax = plt.subplots()


channel = 1

if channel == 1:
    R8_sorted = R8_calibration[:,0].argsort()
    R, T = R8_calibration[R8_sorted,0], R8_calibration[R8_sorted,1]
    tck = interpolate.splrep(R,T)
else:
    sorted_R = calibration[:, channel+1].argsort()
    R, T = calibration[sorted_R, channel+1], calibration[sorted_R, 0]
    tck = interpolate.splrep(R,T, s=2E4)
    

ax.scatter(R, T)
R = np.linspace(0.95*R.min(), 1.05*R.max(), 1000)
ax.plot(R, interpolate.splev(R,tck), color="red")
        