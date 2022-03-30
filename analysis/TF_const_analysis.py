# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 10:45:40 2022

@author: physics-svc-mkdata
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from tuning_fork import Lorentz_Fitting as LF

from glob import glob

# %% data directory

# set this path to "tf_const_measurements" folder
directory = r'C:\Users\alexd\Documents\GitHub\data-monitoring\archive-data\data\tf_const_measurements'

file_name_list = glob(directory+"\\*.dat")

# %% fitting

TF_width = []
TF_freq = []
TF_height = []
TF_drive = []

TF_width_old = []
TF_freq_old = []
TF_height_old = []

for name in file_name_list:
    sweep_data = np.loadtxt(name)
    guess = [32600, 1, 50, 0, 0 , 0, 0]
    TF_fit, flag = LF.Lorentz_Fit_X_quad(sweep_data[:,1], sweep_data[:,2], guess)
    guess = [32600, 1E-3, 50, 0, 0 , 0, 0]
    TF_fit_old, flag_old = LF.Lorentz_Fit_X_quad_old(sweep_data[:,1], sweep_data[:,2], guess)
    
    TF_width.append(np.abs(TF_fit[2]))
    TF_freq.append(np.abs(TF_fit[0]))
    TF_height.append(np.abs(TF_fit[1]))
    TF_drive.append(sweep_data[0, 4])
    
    TF_width_old.append(np.abs(TF_fit_old[2]))
    TF_freq_old.append(np.abs(TF_fit_old[0]))
    TF_height_old.append(np.abs(TF_fit_old[1]))
    
# %%

def bgrd_func(f, a0, a1, a2):
    return a0 + a1*f + a2*f**2


sweep_data = np.loadtxt(file_name_list[0])
guess = [32600, 1, 50, 0, 0 , 0, 0]
TF_fit, flag = LF.Lorentz_Fit_X_quad(sweep_data[:,1], sweep_data[:,2], guess)
TF_fit_y, flag = LF.Lorentz_Fit_Y_quad(sweep_data[:,1], sweep_data[:,3], guess)

guess = [32600, 1E-3, 50, 0, 0 , 0, 0]
TF_fit_old, flag_old = LF.Lorentz_Fit_X_quad_old(sweep_data[:,1], sweep_data[:,2], guess)

plt.figure()
plt.plot(sweep_data[:,1], sweep_data[:,2], 'o', markersize='4')
plt.plot(sweep_data[:,1], LF.Lorentz_x_quad(sweep_data[:,1], TF_fit))

plt.plot(sweep_data[:,1], LF.Lorentz_x_quad_old(sweep_data[:,1], TF_fit_old))

bgrd_X = bgrd_func(sweep_data[:,1], *TF_fit[4:7])
bgrd_Y = bgrd_func(sweep_data[:,1], *TF_fit_y[4:7])
phase = TF_fit[3]
# X = [(mX+bgrd)/sin - (mY+bgrd)/cos]/(cot+tan)
# Y = [(mX+bgrd)/cos + (mY+bgrd)/sin]/(tan+cot)
X = ((sweep_data[:,2]+bgrd_X)/np.sin(phase) - (sweep_data[:,3]+bgrd_Y)/np.cos(phase))/(1/np.tan(phase)+np.tan(phase))
Y = ((sweep_data[:,2]+bgrd_X)/np.cos(phase) + (sweep_data[:,3]+bgrd_Y)/np.sin(phase))/(1/np.tan(phase)+np.tan(phase))
plt.figure()
plt.plot(sweep_data[:,1], X)
plt.plot(sweep_data[:,1], Y)
plt.plot(sweep_data[:,1].mean(), TF_fit[1]/TF_fit[2], 'o')
# plt.plot(sweep_data[:,1].mean(), TF_fit_old[1], 'o')

# %% fit comparison

fig, ax = plt.subplots(3)
ax[0].plot(TF_width)
ax[0].plot(TF_width_old)
ax[1].plot(TF_freq)
ax[1].plot(TF_freq_old)
ax[2].plot(np.divide(TF_height, TF_width))
ax[2].plot(TF_height_old)

width_diff = 0
freq_diff = 0
amp_diff = 0
for idx, elem in enumerate(TF_width):
    width_diff += np.abs(TF_width[idx] - TF_width_old[idx])
    freq_diff += np.abs(TF_freq[idx] - TF_freq_old[idx])
    amp_diff += np.abs(TF_height[idx]/TF_width[idx] - TF_height_old[idx])
    
print(width_diff,freq_diff,amp_diff)

    
# %% sorting and converting to np arrays

x = np.divide(TF_drive, TF_width)
y = np.array(TF_height)/1E4

x_sort_ind = x.argsort()

x = x[x_sort_ind]
y = y[x_sort_ind]

# %% fitting to a linear function

def fit_func(x, a0, a1):
    return a0 + a1*x

line_fit, flags = optimize.curve_fit(fit_func, x, y)


# %% display

plt.figure()
plt.plot(x, y, 'o', markersize=2)
plt.plot(x, fit_func(x, *line_fit), c='coral')

# %% calculating the tuning fork constant from the slope

# slope is a**2 / (4*pi*m)
# m = 0.25*rhoq*L*W*T
# or
# m = 0.24267*rhoq*L*W*T

rhoq = 2659 # kg/m^3
L = 3E-3
W = 0.25E-3
T = 0.1E-3
meff = 0.25*rhoq*L*W*T
mvac = 0.24267*rhoq*L*W*T # after Blaauwgeers

a_0 = np.sqrt(4*np.pi*meff*line_fit[1]) # using 0.25    coef for mass
a_1 = np.sqrt(4*np.pi*mvac*line_fit[1]) # using 0.24267 coef for mass

print("Slope:   %f x 10^-6" % (line_fit[1]*1E6))
print("a(meff): %f x 10^-7" % (a_0*1E7))
print("a(mvac): %f x 10^-7" % (a_1*1E7))
