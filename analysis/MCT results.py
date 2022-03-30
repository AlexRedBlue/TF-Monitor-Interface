# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 11:55:08 2022

@author: alexd
"""

import numpy as np
import pandas as pd
import glob
import os

from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 288

from calibration.mct import MCT_V2Tv

# %%

def import_MCT_data_from_directory(directory=r'C:\Users\alexd\Documents\GitHub\data-monitoring\archive-data\data\cooldown_4\MCT_data',
                                         verbose=False):
    # key = lambda x: x.split('.')[0]
    data_name = 'MCT'
    file_list = sorted(glob.glob(directory+r'\mct_*.dat'), key=os.path.getmtime)
    data_list = []
    unique_indexes = []
    
    for file in file_list:
        data_list.append(pd.read_csv(file, sep="\t", index_col=None, names=["Time", "Ratio", "Voltage", "Temperature"], skiprows=2))
    if verbose == True:
        print(file_list[-1][len(directory):], ' Accepted')
    unique_indexes.append(-1)
    for i in range(len(data_list)-2, -1, -1):
        if data_list[i].to_numpy()[-1,0] not in data_list[i+1].to_numpy()[:,0]:
            if verbose == True:
                print(file_list[i][len(directory):], ' Accepted')
            unique_indexes.append(i)
        else:
            if verbose == True:
                print(file_list[i][len(directory):], ' Not accepted')
            pass
    mct_data = pd.concat([data_list[x] for x in unique_indexes])
    
    return mct_data

# %%

mct_data = import_MCT_data_from_directory()

temperature, pressure = MCT_V2Tv(mct_data["Voltage"], mct_data["Ratio"])

graphing_idxs = np.logical_and(temperature>-0.75, temperature<0.75)

voltage_idxs = np.logical_and(mct_data["Voltage"]<0.01, mct_data["Voltage"]>-0.01)

# %%


x=np.linspace(.0009,.750, 1000)

an3 = -1.3855442E-12
an2 = 4.557026E-9
an1 = -6.4430869E-6
a0 = 3.4467434E0
a1 = -4.416438E0
a2 = 1.5427437E1
a3 = -3.5789853E1
a4 = 7.1499125E1
a5 = -1.0414379E2
a6 = 1.0518538E2
a7 = -6.9443767E1
a8 = 2.6833087E1
a9 = -4.5875709E0

y=(((an3*x**-3) + (an2*x**-2) + (an1*x**-1) + (a0*x**0) + (a1*x**1) + (a2*x**2) + (a3*x**3) + (a4*x**4) + (a5*x**5) + (a6*x**6) + (a7*x**7) + (a8*x**8) + (a9*x**9)))



# %% Pressure vs Temp

plt.figure() 
plt.scatter(temperature[graphing_idxs], pressure[graphing_idxs])
plt.plot(x, y, c='red', alpha = 0.9)
plt.xlabel("T, K")
plt.ylabel("P, MPa")
plt.title("MCT Curve")

# %% Temp

plt.figure()
plt.scatter(mct_data["Time"][graphing_idxs], temperature[graphing_idxs])
plt.xlabel("time, s")
plt.ylabel("T, K")
plt.title("MCT Temp")

# %% Pressure

plt.figure()
plt.scatter(mct_data["Time"][graphing_idxs], pressure[graphing_idxs])
plt.xlabel("time, s")
plt.ylabel("Pressure, MPa")
plt.title("MCT Pressure")

# %% Ratio

plt.figure()
plt.scatter(mct_data["Time"][graphing_idxs], mct_data["Ratio"][graphing_idxs])
plt.xlabel("time, s")
plt.ylabel("Ratio")
plt.title("MCT Ratio")
