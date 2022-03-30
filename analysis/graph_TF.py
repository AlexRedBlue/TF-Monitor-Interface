# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:11:18 2022

@author: physics-svc-mkdata
"""

from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

quartz_dir = r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\archive-data\data\cooldown_1\TFT_data\Quartz_TFT\fits\*.dat"

file_list = glob(quartz_dir)

# %%

fig, ax = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()

graphs = [ax, ax2, ax3]

for name in file_list:
    data = pd.read_csv(name, sep='\t')
    ax.plot(data['Time, s'], data['Width, Hz'])
    ax2.plot(data['Time, s'], data['# Frequency, Hz'])
    ax3.plot(data['Time, s'], data['Amplitude, V'])
    
    
ax.set_xlabel("Time")
ax2.set_xlabel("Time")
ax3.set_xlabel("Time")

ax.set_ylabel("$\Delta f$")
ax2.set_ylabel("$f_0$")
ax3.set_ylabel("$I_0$")

# %%

for graph in graphs:
    ticks = graph.get_xticks()
    new_times = []
    new_ticks = []
    for idx, t in enumerate(ticks):
        dt = datetime.fromtimestamp(t)
        dt = datetime(year=int(dt.strftime("%Y")), month=int(dt.strftime("%m")), day=int(dt.strftime("%d")))
        new_ticks.append(dt.strftime("%m-%d"))
        new_times.append(dt.timestamp())
    graph.set_xticks(new_times)
    graph.set_xticklabels(new_ticks)
    
# %%

fig, ax = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()

for name in file_list:
    data = pd.read_csv(name, sep='\t')
    ax.plot(data['# Frequency, Hz'], data['Width, Hz'], ',')
    ax2.plot(data['# Frequency, Hz'], data['Amplitude, V'], ',')
    ax3.plot(data['Width, Hz'], data['Amplitude, V'], ',')
    

    
    