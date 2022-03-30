# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 19:44:31 2021

@author: alexd
"""

import numpy as np
import matplotlib.pyplot as plt

import time
import sys

from tuning_fork.Lorentz_Fitting import Lorentz_Fit_X as LFx

temperature_loc = r'D:\Maglab\data-monitoring-backup\data-monitoring\archive-data\data\cooldown_4\TFT_data\Cell_TFT\fits'

temp_file ='\Cell_TFT_2021-10-05_73.dat'

temp_cal = np.loadtxt(temperature_loc+temp_file)

# %%

temperatures = temp_cal[:,1]
frequencies = temp_cal[:,3]
widths = temp_cal[:,5]

sorted_idx = np.argsort(temperatures)

temperatures = temperatures[sorted_idx]
frequencies = frequencies[sorted_idx]
widths = widths[sorted_idx]

# %%





def temp_to_resonance(temp, temperatures=temperatures, frequencies=frequencies, widths=widths):
    width = np.interp(temp, temperatures, widths)
    freq = np.interp(temp, temperatures, frequencies)
    return width, freq

def lorentzian(x, G, naught=32700, eta=0):
    G = G/2
    if eta > 0:
        return (1 + np.random.uniform(-eta, eta)) * np.divide(G, np.power(x-naught, 2) + G**2)
    else:
        return np.divide(G, np.power(x-naught, 2) + G**2)


def sim_scan(start, stop, points, step_time):
    
    T_1 = 10E-3
    T_2 = 10.01E-3
    TF_1 = []
    TF_2 = []
    
    G_1, res_1 = temp_to_resonance(T_1)
    G_2, res_2 = temp_to_resonance(T_2)
    
    freq_list = np.linspace(start, stop, points)
    
    fig, ax = plt.subplots(3,1)
    
    for i, f in enumerate(freq_list):
        
        sys.stdout.write("\rnum: %i/%i" % (i+1, points))
        sys.stdout.flush()
        
        TF_1.append(lorentzian(f, G_1, res_1))
        TF_2.append(lorentzian(f, G_2, res_2))
        
        for subplot in ax:
            subplot.clear()
        
        ax[0].plot(freq_list[0:i+1], np.asarray(TF_1), color='red')
        ax[1].plot(freq_list[0:i+1], np.asarray(TF_2), color='blue')
        ax[2].plot(freq_list[0:i+1], np.asarray(TF_2)-np.asarray(TF_1), c='green')
        
        plt.pause(step_time)
    
    fit_coef, fit_flags = LFx(freq_list, np.asarray(TF_2)-np.asarray(TF_1), guess=[32000, 0, 500, 0,0,0])
    
    return fit_coef
        
# %%
        
if __name__ == "__main__":
    fit_coef = sim_scan(31500, 33500, 60, 0.05)
    print("\nFreq: %f\nPhase: %f\nWidth: %f" % (fit_coef[0], fit_coef[1]*180/np.pi, fit_coef[1]))
    
        
        
        