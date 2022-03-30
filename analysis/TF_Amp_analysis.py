# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 12:22:58 2022

@author: alexd
"""
import numpy as np
# import pandas as pd
# import glob
# import os

import matplotlib.pyplot as plt
from matplotlib import cm
# from matplotlib.colors import ListedColormap, LinearSegmentedColormap
# from matplotlib.colors import Normalize
# from matplotlib.widgets import Button
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 288

# import time
from datetime import datetime

# from scipy.optimize import curve_fit

from analysis import getInfo as info

cooldown_dates = {
        "cooldown_1": ["06-29", "07-14"],
        "cooldown_2": ["07-29", "08-17"],
        "cooldown_3": ["08-20", "08-26"],
        # "cooldown_4": ["08-25-2021", "12-31-2021"],
        "cooldown_4": ["10-02-2021", "12-31-2021"],
        # "cooldown_4": ["08-25-2021", "08-31-2021"],
        "cooldown_5": ["01-14-2022", "01-14-2022"]
        }

tf_name="Cell_TFT"
time_period = "cooldown_4"

time_0 = info.get_timestamp_from_day((cooldown_dates[time_period])[0])
time_1 = info.get_timestamp_from_day((cooldown_dates[time_period])[1], end_of_day=1)

# tf_width = self.tf_data['x:Width, Hz'].to_numpy()
# tf_frequency = self.tf_data['x:Frequency, Hz'].to_numpy()

# %%
print(info.get_directory("TFT_data\\{}\\fits".format(tf_name), time_period))
tf_data = info.import_tf_data_from_directory(info.get_directory("TFT_data\\{}\\fits".format(tf_name), time_period), 
                                             verbose=False)

# Time, s	Temperature, K	Drive Votlage, V	 x:Frequency, Hz	x:Amplitude, V	x:Width, Hz	x:Phase, Rad	x:Background intercept, V	x:Background slope, dV/df	x:Background quadratic, d2V/d2f	y:Frequency, Hz	y:Amplitude, V	y:Width, Hz	y:Phase, Rad	y:Background intercept, V	y:Background slope, dV/df	y:Background quadratic, d2V/d2f


tf_width = tf_data['y:Width, Hz'].to_numpy()
tf_frequency = tf_data['y:Frequency, Hz'].to_numpy()
tf_amp = tf_data["y:Amplitude, V"].to_numpy()
tf_drive = tf_data["Drive Votlage, V"].to_numpy()
tf_temp = tf_data["Temperature, K"].to_numpy()


tf_time = tf_data['# Time, s'].to_numpy()
tf_index_list = [idx for idx, val in enumerate(tf_time) if (val > time_0 and val < time_1)]
tf_time = tf_time - time_0

# only include time from time_0 to time_1
tf_time_ind = np.logical_and(tf_time>0, tf_time<time_1-time_0)
tf_time = tf_time[tf_time_ind]
tf_width = np.abs(tf_width[tf_time_ind])
tf_frequency = np.abs(tf_frequency[tf_time_ind])
tf_amp = np.abs(tf_amp[tf_time_ind])
tf_drive = tf_drive[tf_time_ind]
tf_temp = tf_temp[tf_time_ind]

tf_amp = tf_amp/tf_drive

# sort by time start to end
tf_sort_idx = tf_time.argsort()
tf_time=tf_time[tf_sort_idx]
tf_width=tf_width[tf_sort_idx]
tf_frequency=tf_frequency[tf_sort_idx]
tf_amp = tf_amp[tf_sort_idx]
tf_drive = tf_drive[tf_sort_idx]
tf_temp = tf_temp[tf_sort_idx]


# %%

# Time, s	ratio	Voltage, V	, Temperature, K
# print(info.get_directory("MCT_data", time_period))

mct_data = info.import_MCT_data_from_directory(info.get_directory("MCT_data", time_period),
                                               verbose=False)
# print(mct_data.columns)
# mct_temp = (self.mct_data["Temperature, K"])[1:].to_numpy(dtype=float)
mct_time = (mct_data["Time, s"])[1:].to_numpy(dtype=float)
mct_volt = (mct_data["Voltage, V"])[1:].to_numpy(dtype=float)
mct_ratio = (mct_data["Ratio"])[1:].to_numpy(dtype=float)

from tuning_fork.mct import MCT_V2Tv
mct_temp = MCT_V2Tv(Vin=mct_volt, ratio=mct_ratio)[0]

# only include time from time_0 to time_1
mct_time_index = np.logical_and(mct_time>time_0, mct_time<time_1)

mct_time = mct_time[mct_time_index] - time_0
mct_temp = mct_temp[mct_time_index]
mct_volt = mct_volt[mct_time_index]
mct_ratio = mct_ratio[mct_time_index]

# sort by time start to end
mct_sort_time_idx = mct_time.argsort()

mct_time = mct_time[mct_sort_time_idx]
mct_temp = mct_temp[mct_sort_time_idx]
mct_volt = mct_volt[mct_sort_time_idx]
mct_ratio = mct_ratio[mct_sort_time_idx]

mct_interp_temp = np.interp(tf_time, mct_time, mct_temp)

# %%

# fig, ax = plt.subplots(4, sharex=True)
# # ax_00 = ax[0].loglog(tf_amp*1E6/1E4, tf_frequency/tf_width, 'o', markersize=2,
# #              c=mct_interp_temp, cmap="inferno")
# # ax[1].loglog(tf_amp*1E6/1E4, tf_frequency/1000, 'o', markersize=2,
# #              c=mct_interp_temp, cmap="inferno")
# # ax[2].loglog(tf_amp*1E6/1E4, tf_width, 'o', markersize=2, 
# #              c=mct_interp_temp, cmap="inferno")

# cT = np.logical_and(tf_temp>0, tf_temp<0.050)

# ax_00 = ax[0].scatter(tf_amp[cT]*1E6/1E4, tf_frequency[cT]/tf_width[cT], s=2,
#              c=tf_temp[cT], cmap="inferno")
# ax[1].scatter(tf_amp[cT]*1E6/1E4, tf_frequency[cT]/1000, s=2,
#              c=tf_temp[cT], cmap="inferno")
# ax[2].scatter(tf_amp[cT]*1E6/1E4, tf_width[cT], s=2, 
#              c=tf_temp[cT], cmap="inferno")
# ax[3].scatter(tf_amp[cT]*1E6/1E4, tf_temp[cT], s=2, 
#              c=tf_temp[cT], cmap="inferno")

# plt.colorbar(ax_00, ax=ax, label='T, K')



# ax[0].set_title("TF Amplitude vs Q")
# ax[0].set_ylabel("Q")
# ax[1].set_ylabel("$f_0$ (khz)")
# ax[2].set_ylabel("$\Delta f$ (hz)")
# ax[2].set_xlabel("Amplitude I (nA)")

# ax[1].set_xlim([0.008779640386913328, 0.16922834927484093])

# # ax[1].set_xlim([0.0033213493745403028, 5872.190498979155])
# # ax[1].set_ylim([31.93086873392946, 32.93436914279749])

# for plot in ax:
#     plot.set_xscale("log")
#     plot.set_yscale("log")
#     plot.grid(True, which="both")
    
# # ax[3].set_xscale("log")
# ax[3].set_yscale("linear")
    

# %%

fig, ax = plt.subplots(2, sharex=True)
ax[0].plot(tf_time/24/3600, tf_temp-mct_interp_temp, 'o', markersize=2,)
ax[0].set_ylim([-2, 26])
ax[1].plot(tf_time/24/3600, tf_temp, 'o', markersize=2, label='TFT')
ax[1].plot(tf_time/24/3600, mct_interp_temp, 'o', markersize=2, label="MCT")
ax[1].set_ylim([0, 26])

ticks = ax[1].get_xticks()
xlabels = []
for idx, val in enumerate(ax[1].get_xticks()):
    xlabels.append(info.get_start_date(int(val*24*3600+time_0))[0].strftime("%m-%d-%y"))

ax[1].set_xticks(ticks[1:-1])
ax[1].set_xticklabels(xlabels[1:-1])

ax[1].set_xlabel("Time, day")
ax[0].set_ylabel("$\Delta$T, K")
ax[1].set_ylabel("T, K")
ax[0].set_title("TFT - MCT (10-02-2021)")
ax[1].legend()
