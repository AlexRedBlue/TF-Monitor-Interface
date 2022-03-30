# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 13:08:55 2022

@author: alexd
"""

import numpy as np
from matplotlib import pyplot as plt
from analysis import getInfo as info
import matplotlib as mpl 

user = "physics-svc-mkdata"
if user == "alexd":
    mpl.rcParams['figure.dpi'] = 300 
else:
    mpl.rcParams['figure.dpi'] = 100

time_period='cooldown_4'
# connected_tf = "Cell_TFT"
connected_tf = "Cell_TFT"
cooldown_dates = {
        "cooldown_1": ["06-29-2021", "07-14-2021"],
        "cooldown_2": ["07-29-2021", "08-17-2021"],
        "cooldown_3": ["08-20-2021", "08-26-2021"],
        # "cooldown_4": ["08-25-2021", "12-31-2021"],
        "cooldown_4": ["10-01-2021", "10-26-2021"],
        # "cooldown_4": ["08-25-2021", "08-31-2021"],
        "cooldown_5": ["01-11-2022", "01-18-2022"],
        "cooldown_5-demag": ["01-18-2022", "01-21-2022"]
        # "cooldown_5": ["01-22-2022", "01-28-2022"]
        }

time_0 = info.get_timestamp_from_day((cooldown_dates[time_period])[0])
time_1 = info.get_timestamp_from_day((cooldown_dates[time_period])[1], end_of_day=1)

# tf_width = self.tf_data['x:Width, Hz'].to_numpy()
# tf_frequency = self.tf_data['x:Frequency, Hz'].to_numpy()

directory = r"C:\Users\{}\Documents\GitHub\data-monitoring\archive-data\data\{}".format(user, time_period)

# TF Import

tf_data = info.import_tf_data_from_directory(directory+r"\TFT_data\{}\fits".format(connected_tf), verbose=True)
mct_data = info.import_MCT_data_from_directory(directory+r"\MCT_data", verbose=True)


# %% 
channel = "x"

tf_width = tf_data[channel+':Width, Hz'].to_numpy()
tf_frequency = tf_data[channel+':Frequency, Hz'].to_numpy()
tf_amp = tf_data[channel+':Amplitude, V'].to_numpy()
tf_phase = tf_data[channel+':Phase, Rad'].to_numpy()
# x:Background intercept, V	x:Background slope, dV/df	x:Background quadratic, d2V/d2f	y:Frequency, Hz	y:Amplitude, V	y:Width, Hz	y:Phase, Rad	y:Background intercept, V	y:Background slope, dV/df	y:Background quadratic, d2V/d2f
tf_a0_bgrd = tf_data[channel+':Background intercept, V'].to_numpy()
tf_a1_bgrd = tf_data[channel+':Background slope, dV/df'].to_numpy()
tf_a2_bgrd = tf_data[channel+':Background quadratic, d2V/d2f'].to_numpy()


tf_time = tf_data['# Time, s'].to_numpy()
tf_index_list = [idx for idx, val in enumerate(tf_time) if (val > time_0 and val < time_1)]

tf_time_ind = np.logical_and(tf_time>time_0, tf_time<time_1)
tf_time=tf_time[tf_time_ind]
tf_width=tf_width[tf_time_ind]
tf_frequency=tf_frequency[tf_time_ind]
tf_amp = tf_amp[tf_time_ind]
tf_phase = tf_phase[tf_time_ind]
tf_a0_bgrd = tf_a0_bgrd[tf_time_ind]
tf_a1_bgrd = tf_a1_bgrd[tf_time_ind]
tf_a2_bgrd = tf_a2_bgrd[tf_time_ind]

tf_time = tf_time - time_0

sort_time_idx = tf_time.argsort()
tf_time=tf_time[sort_time_idx]
tf_width=tf_width[sort_time_idx]
tf_frequency=tf_frequency[sort_time_idx]
tf_amp = tf_amp[sort_time_idx]
tf_phase = tf_phase[sort_time_idx]
tf_a0_bgrd = tf_a0_bgrd[sort_time_idx]
tf_a1_bgrd = tf_a1_bgrd[sort_time_idx]
tf_a2_bgrd = tf_a2_bgrd[sort_time_idx]

# %%

# MCT Import
# "Time, s", "Ratio", "Voltage, V", "Temperature, K"

mct_temp = (mct_data["Temperature, K"])[1:].to_numpy(dtype=float)
mct_time = (mct_data["Time, s"])[1:].to_numpy(dtype=float)

mct_volt = (mct_data["Voltage, V"])[1:].to_numpy(dtype=float)
mct_ratio = (mct_data["Ratio"])[1:].to_numpy(dtype=float)

# from tuning_fork.mct import MCT_V2Tv
# mct_temp = MCT_V2Tv(Vin=mct_volt, ratio=mct_ratio)[0]

mct_time_index = np.logical_and(mct_time>time_0, mct_time<time_1)

mct_time = mct_time[mct_time_index] - time_0
mct_temp = mct_temp[mct_time_index]

mct_temp_idx = np.logical_and(mct_temp>0, mct_temp<.35)
mct_time = mct_time[mct_temp_idx]
mct_temp = mct_temp[mct_temp_idx]

# %%
    
from tuning_fork import TF_visc
if connected_tf == "Cell_TFT":
    TF_visc.foVac_commFork = 32776.8 # Cell
    meff_factor = 1
elif connected_tf == "silver-NS_TFT":
    TF_visc.foVac_commFork = 32852.0 # Silver
    meff_factor = 0.78
    # meff_factor = 1
mvac = 0.24267*TF_visc.rhoq*TF_visc.L*TF_visc.W*TF_visc.T
TF_visc.mvac = mvac * meff_factor


# tf_temp = TF_visc.Meas_Temp(tf_width, tf_frequency)       
# fig, ax = plt.subplots(1,1)
# ax.plot(tf_time/3600/24, tf_temp*1E3, 'o', markersize=2, label="TF_Temp")
# ax.plot(mct_time/3600/24, mct_temp*1E3, 'o', markersize=2, label="MCT_Temp")
# ax.set_ylabel("Temp, mK")
# ax.set_xlabel("Time, days")
# ax.set_title(str(meff_factor)+ " TF Mass" )
# ax.legend()
# ax.grid(True)

# %%


# fig, ax = plt.subplots(2,1)
# ax[0].plot(mct_time, mct_temp, 'o', markersize=2, label="MCT_Temp")
# ax[1].plot(tf_time, tf_frequency, 'o', markersize=2, color='coral', label="TF_Freq")
# # ax.plot(mct_time/3600/24, mct_temp*1E3, 'o', markersize=2, label="MCT_Temp")
# ax[1].set_xlabel("Time, s")
# ax[0].set_ylabel("Temp, K")
# ax[1].set_ylabel("Freq, hz")
# ax[0].set_title("Frequency vs Temp (MCT)")
# ax[0].legend()
# for subplot in ax:
#     subplot.grid(True)


# %% 

sort_ind = mct_time.argsort()
mct_interp_temp = np.interp(tf_time, mct_time[sort_ind], mct_temp[sort_ind]) * 1E3 # mK


# %%

# fig, ax = plt.subplots(1,1)
# # scatter, = ax.loglog(mct_interp_temp, tf_frequency, 'o', markersize=2, label="TF Frequency")
# # scatter, = ax.loglog(mct_interp_temp, tf_amp, 'o', markersize=2, label="TF Response")
# scatter, = ax.loglog(mct_interp_temp, tf_width, 'o', markersize=2, label="TF Width")
# # scatter, = ax.loglog(mct_interp_temp, tf_frequency/tf_width, 'o', markersize=2, label="TF Q Factor")
# # scatter, = ax.loglog(mct_interp_temp, tf_phase, 'o', markersize=2, label="TF Phase")

# ax.set_xlabel("Temp, mK")
# ax.set_ylabel(scatter.get_label())
# ax.set_title(scatter.get_label()+" vs Temp (MCT)")
# ax.grid(True)

# %%

# fig, ax = plt.subplots(3,1)


# ax[0].loglog(mct_interp_temp, tf_a0_bgrd, 'o', markersize=2, label="constant bgrd")
# ax[1].loglog(mct_interp_temp, tf_a1_bgrd, 'o', markersize=2, label="linear bgrd")
# ax[2].loglog(mct_interp_temp, tf_a2_bgrd, 'o', markersize=2, label="quad bgrd")
# ax[-1].set_xlabel("Temp, mK")
# ax[0].set_ylabel("Constant, V")
# ax[1].set_ylabel("Linear, dV/df")
# ax[2].set_ylabel("Quadratic, d2V/d2f")
# ax[0].set_title("Background vs Temp (MCT)")
# for subplot in ax:
#     subplot.legend(loc=2)
#     subplot.grid(True)

# %%

if True:
    try:
        tf_data['Drive Voltage, V'] = tf_data['Drive Voltage, V'].combine_first(tf_data['Drive Votlage, V'])
        tf_data = tf_data.drop(columns=['Drive Votlage, V'])
    except:
        pass
    save_location = r"C:\Users\physics-svc-mkdata\Documents\Data\2022_TFTs\Cell TFT\{}_{}_CELL_TFT_FITS - Sorted.dat".format((cooldown_dates[time_period])[0], (cooldown_dates[time_period])[1])
    numpy_tf_data = tf_data.to_numpy()
    numpy_tf_data = numpy_tf_data[numpy_tf_data[:, 0].argsort(),:]
    np.savetxt(save_location, numpy_tf_data, delimiter="\t", header="Time, s	Temperature, K	Drive Votlage, V	x:Frequency, Hz	x:Amplitude, V	x:Width, Hz	x:Phase, Rad	x:Background intercept, V	x:Background slope, dV/df	x:Background quadratic, d2V/d2f	y:Frequency, Hz	y:Amplitude, V	y:Width, Hz	y:Phase, Rad	y:Background intercept, V	y:Background slope, dV/df	y:Background quadratic, d2V/d2f")
    
    save_location = r"C:\Users\physics-svc-mkdata\Documents\Data\2022_TFTs\Cell TFT\{}_{}_MCT - Sorted.dat".format((cooldown_dates[time_period])[0], (cooldown_dates[time_period])[1])
    numpy_mct_data = mct_data.to_numpy()
    numpy_mct_data = numpy_mct_data[numpy_mct_data[:, 0].argsort(),:]
    np.savetxt(save_location, numpy_mct_data, delimiter="\t", header = "Time, s	Ratio	Voltage, V	Temperature, K")
    
    # mct_data.sort_values("Time, s", ascending=True)
    # mct_data.to_csv(save_location, sep='\t', index=False)
    
    
    
    
