# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 15:48:51 2022

@author: physics-svc-mkdata
"""
import numpy as np
import matplotlib.pyplot as plt
from analysis import getInfo
from scipy.optimize import curve_fit

directory = r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\archive-data\data\select_data"
fname = r"\silver-NS_TFT_2022-01-13_9.dat"
# fname = r"\silver-NS_TFT_2022-01-14_22.dat"


tf_data = np.loadtxt(directory+fname, delimiter='\t')

# %%

# time0 = getInfo.get_start_date()

select_time = np.logical_and(tf_data[:,0]>(456164.6-24)*3600, tf_data[:,0]<(456164.9-24)*3600) # 1-14

def fit_func(t, a0, a1):
    return a0+a1*t


popt, pcov = curve_fit(fit_func, tf_data[select_time,0]-(tf_data[select_time,0])[0], np.log(tf_data[select_time, 1]-0.0935))


# %%

plt.figure()
# plt.plot(tf_data[:,0], tf_data[:, 5], 'o')
plt.plot(tf_data[select_time,0]-(tf_data[select_time,0])[0], tf_data[select_time, 1]-0.0935, 'o', markersize=5, mfc='none')
plt.plot(tf_data[select_time,0]-(tf_data[select_time,0])[0], np.exp(fit_func(tf_data[select_time,0]-(tf_data[select_time,0])[0], *popt)))
# plt.plot(tf_data[select_time,0]-(tf_data[select_time,0])[0], np.log(tf_data[select_time, 1]-0.0935), 'o', markersize=5, mfc='none')
# plt.plot(tf_data[select_time,0]-(tf_data[select_time,0])[0], fit_func(tf_data[select_time,0]-(tf_data[select_time,0])[0], *popt))
plt.title("Tau: {:.1f} s".format(-1/popt[1]))
print("tau", -1/popt[1])