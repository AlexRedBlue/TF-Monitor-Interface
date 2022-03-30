# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 14:08:57 2021

@author: physics-svc-mkdata
"""

# TODO
# Create a program that graphs saved data

import numpy as np
import pandas as pd
import glob
import os

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.colors import Normalize
from matplotlib.widgets import Button

import time
from datetime import datetime

from scipy.optimize import curve_fit
# from scipy.optimize import polyfit

        
def find_limits(array, ratio=2):
    return [array.mean()-ratio*array.std(), array.mean()+ratio*array.std()]

def poly(x, a, b, c, d, e, f, g,):
    return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5

# def rgb(mag, cmin, cmax):
#     """ Return a tuple of integers, as used in AWT/Java plots. """
#     red, green, blue = floatRgb(mag, cmin, cmax)
#     return int(red*255), int(green*255), int(blue*255)

# %%
        
class data_explorer:
    def __init__(self):
        self.diode_data_empty = True
        self.acs_data_empty = True
        self.tf_data_empty = True
        self.rt_data_empty = True
        
    def get_start_date(self, timestamp):
        start = datetime.fromtimestamp(timestamp)
        day_0 = datetime(year=start.year, month=start.month, day=start.day)
        time_0 = time.mktime(day_0.timetuple())
        return day_0, time_0
    
    def get_timestamp_from_day(self, month_day_year, end_of_day=0):
        month, day, year = month_day_year.split("-")
        month, day, year = int(month), int(day), int(year)
        if end_of_day == 1:
            dt = datetime(year=year, month=month, day=day, hour=23, minute=59)
        elif end_of_day == 0:
            dt = datetime(year=year, month=month, day=day) 
        return time.mktime(dt.timetuple())

# %%
        
    def import_diode_data_from_directory(self, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\diode_data',
                                         verbose=False):
        # key = lambda x: x.split('.')[0]
        data_name = 'diode'
        file_list = sorted(glob.glob(directory+r'\diode_*.dat'), key=os.path.getmtime)
        data_list = []
        unique_indexes = []
        
        for file in file_list:
            data_list.append(pd.read_csv(file, sep="\t", index_col=None, header=0))
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
        self.diode_data = pd.concat([data_list[x] for x in unique_indexes])
        
    def import_MCT_data_from_directory(self, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\MCT_data',
                                         verbose=False):
        # key = lambda x: x.split('.')[0]
        data_name = 'MCT'
        file_list = sorted(glob.glob(directory+r'\mct_*.dat'), key=os.path.getmtime)
        data_list = []
        unique_indexes = []
        
        for file in file_list:
            data_list.append(pd.read_csv(file, sep="\t", index_col=None, names=["1", "2", "3", "4"], skiprows=2))
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
        self.mct_data = pd.concat([data_list[x] for x in unique_indexes])
         
    def import_acs_data_from_directory(self, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\acs_data',
                                       verbose=False):
        
        data_name = 'acs'
        file_list = sorted(glob.glob(directory+r'\acs_*.dat'), key=os.path.getmtime)
        data_list = []
        unique_indexes = []
        
        for file in file_list:
            data_list.append(pd.read_csv(file, sep="\t", index_col=None, header=0))
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
        self.acs_data = pd.concat([data_list[x] for x in unique_indexes])
        
    def import_tf_data_from_directory(self, data_name = 'MC_TFT', directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\TFT_data\NS_TFT\fits',
                                      verbose=False):
        
        data_name = 'MC_TFT'
        file_list = sorted(glob.glob(directory+'\\*.dat'), key=os.path.getmtime)
        # print(file_list)
        data_list = []
        unique_indexes = []
        
        for file in file_list:
            data_list.append(pd.read_csv(file, sep="\t", index_col=None, header=0))
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
        self.tf_data = pd.concat([data_list[x] for x in unique_indexes])
        
    def import_rt_data_from_directory(self, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\cooldown2\rt_data',
                                      verbose=False):
        
        data_name = 'rt'
        file_list = sorted(glob.glob(directory+r'\rt_*.dat'), key=os.path.getmtime)
        data_list = []
        unique_indexes = []
        
        for file in file_list:
            data_list.append(pd.read_csv(file, sep="\t", index_col=None, header=0))
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
        self.rt_data = pd.concat([data_list[x] for x in unique_indexes])
        
# %%
        
    def import_diode_data(self, file_name, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\diode_data'):
        file_path = directory + file_name
        if self.diode_data_empty == True:
            self.diode_data = pd.read_csv(file_path, sep="\t")
            self.diode_data_empty = False
        else:
            new_data = pd.read_csv(file_path, sep="\t", index_col=None, header=0)
            # print(new_data.to_numpy()[0,:])
            if new_data.to_numpy()[-1,:] not in self.diode_data.to_numpy():
                # print(file_name, ' Accepted')
                self.diode_data = pd.concat([self.diode_data, new_data])
            else:
                # print(file_name, ' Not accepted')
                pass
        
    def import_acs_data(self, file_name, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\acs_data'):
        file_path = directory + file_name
        if self.acs_data_empty == True:
            self.acs_data = pd.read_csv(file_path, sep="\t")
            self.acs_data_empty = False
        else:
            new_data = pd.read_csv(file_path, sep="\t", index_col=None, header=0)
            if new_data.to_numpy()[-1,:] not in self.acs_data.to_numpy()[:,:]:
                self.acs_data = pd.concat([self.acs_data, new_data])

    def import_tf_data(self, file_name, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\TFT_data\NS_TFT\fits'):
        file_path = directory + file_name
        if self.tf_data_empty == True:
            self.tf_data = pd.read_csv(file_path, sep="\t")
            self.tf_data_empty = False
        else:
            new_data = pd.read_csv(file_path, sep="\t", index_col=None, header=0)
            if new_data.to_numpy()[-1,:] not in self.tf_data.to_numpy()[:,:]:
                self.tf_data = pd.concat([self.tf_data, new_data])

            
    def import_rt_data(self, file_name, directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\rt_data'):
        file_path = directory + file_name
        if self.rt_data_empty == True:
            self.rt_data = pd.read_csv(file_path, sep="\t")
            self.rt_data_empty = False
        else:
            new_data = pd.read_csv(file_path, sep="\t", index_col=None, header=0)
            if new_data.to_numpy()[-1,:] not in self.rt_data.to_numpy()[:,:]:
                self.rt_data = pd.concat([self.rt_data, new_data])

        
    def print_diode_data(self):
        print((self.diode_data['# Time, s'].values[-1]-self.diode_data['# Time, s'].values[0])/3600)
        
    def print_acs_data(self):
        print(find_limits(self.acs_data['Vy (V).1'].values))
        
    def print_tf_data(self):
        print(self.tf_data.columns)
        
# %%
        
    def display_acs_data(self, diode=True, scale=24*3600, time_period=["08-21", "08-27"], T_min=2, T_max=270.0, plot_V_time=True, plot_VT=True, save_select_data=[False, 'cooldown_1'], std_multiplier=4):
        
        if diode == False and plot_VT == True:
            print("Warning: set diode to true to plot temperature.")
        
        time_0 = self.get_timestamp_from_day(time_period[0])
        time_1 = self.get_timestamp_from_day(time_period[1], end_of_day=1)
        acs_time_name = self.acs_data.columns[0]
        
        acs_time = self.acs_data[acs_time_name].to_numpy()
        acs_index_list = [idx for idx, val in enumerate(acs_time) if (val > time_0 and val < time_1)]
        acs_time = acs_time[acs_index_list] - time_0
        
        
        if diode == True:
            diode_time_name = self.diode_data.columns[0]
            diode_time = self.diode_data[diode_time_name].to_numpy()
            diode_index_list = [idx for idx, val in enumerate(diode_time) if (val > time_0 and val < time_1)]
            diode_time = diode_time - time_0
            
            diode_ind = diode_time[diode_index_list].argsort()
            acs_temperature = np.interp(acs_time, (diode_time[diode_index_list])[diode_ind], (self.diode_data[', Temperature, K'].to_numpy()[diode_index_list])[diode_ind])
            acs_temperature = np.nan_to_num(acs_temperature, nan=0.0)
        
            T_indicies = [idx for idx, val in enumerate(acs_temperature) if (val > T_min and val < T_max)]
        # print(self.acs_data.columns)        

        # Main Plots
        
        if diode == True and plot_V_time == True:
            fig, ax = plt.subplots(2,2, figsize=(18, 9))
            name_idx = 0
            for row_idx, row in enumerate(ax):
                for col_idx, subplot in enumerate(row):
                    name_idx += 1
                    col_name = self.acs_data.columns[name_idx]
                    s_plot = ax[row_idx][col_idx].scatter(
                        acs_time[T_indicies]/scale,
                        (self.acs_data[col_name].to_numpy()[acs_index_list])[T_indicies],
                        c=acs_temperature[T_indicies],
                        cmap="inferno",
                        marker='.',
                        label=col_name
                        )
                    plt.colorbar(s_plot, ax=ax[row_idx][col_idx])
        elif diode == False and plot_V_time == True:
            fig, ax = plt.subplots(2,2, figsize=(18, 9))
            name_idx = 0
            for row_idx, row in enumerate(ax):
                for col_idx, subplot in enumerate(row):
                    name_idx += 1
                    col_name = self.acs_data.columns[name_idx]
                    if row_idx == 0:
                        lockin_color = 'cornflowerblue'
                    else:
                        lockin_color = 'coral'
                    ax[row_idx][col_idx].scatter(
                        acs_time/scale,
                        (self.acs_data[col_name].to_numpy()[acs_index_list]),
                        color=lockin_color,
                        s=2,
                        label=col_name
                        )
        if plot_V_time == True:
            ax[0][0].set_ylabel('V')
            ax[1][0].set_ylabel('V')
            ax[1][0].set_xlabel('Time, Days')
            ax[1][1].set_xlabel('Time, Days')
            ax[0][0].set_title("Start time: {}".format(time_period[0]))
            
            for row in ax:
                for subplot in row:
                    subplot.legend(loc=2)
            
            fig.subplots_adjust(wspace=0.3, hspace=0.3)
                
        # Temperature Plots

        if diode == True and plot_VT == True:
            fig, ax = plt.subplots(2,2, figsize=(18, 9))
            
            theta = 0 * (np.pi/180)
            
            # L1x_V_min, L1x_V_max = -0.00019, -0.00015
            # L1y_V_min, L1y_V_max = -2E-5, 2E-5
            # L2x_V_min, L2x_V_max = 0.0075, 0.0077
            # L2y_V_min, L2y_V_max = -24E-5, -18E-5
            
            # selected_data_range = np.logical_and()
            
            limit_list = list()
            rotation_list = list()
            
            name_idx = 0
            for row_idx, row in enumerate(ax):
                for col_idx, subplot in enumerate(row):
                    name_idx += 1
                    col_name = self.acs_data.columns[name_idx]
                    
                    if row_idx == 0 and col_idx == 0:
                        x_name = self.acs_data.columns[name_idx]
                        y_name = self.acs_data.columns[name_idx + 1]
                        # print("plot {}: x-{}, y-{}".format(name_idx, x_name, y_name))
                        rotation = ((self.acs_data[x_name].to_numpy()[acs_index_list])[T_indicies]*np.cos(theta)-
                                    ((self.acs_data[y_name].to_numpy()[acs_index_list])[T_indicies])*np.sin(theta))
                        # V_min, V_max = -0.00019, -0.00015
                    elif row_idx == 0 and col_idx == 1:
                        x_name = self.acs_data.columns[name_idx - 1]
                        y_name = self.acs_data.columns[name_idx]
                        # print("plot {}: x-{}, y-{}".format(name_idx, x_name, y_name))
                        rotation = (((self.acs_data[x_name].to_numpy()[acs_index_list])[T_indicies])*np.sin(theta) +
                                    (self.acs_data[y_name].to_numpy()[acs_index_list])[T_indicies]*np.cos(theta))
                        # V_min, V_max = -2E-5, 2E-5
                    elif row_idx == 1 and col_idx == 0:
                        x_name = self.acs_data.columns[name_idx]
                        y_name = self.acs_data.columns[name_idx + 1]
                        # print("plot {}: x-{}, y-{}".format(name_idx, x_name, y_name))
                        rotation = ((self.acs_data[x_name].to_numpy()[acs_index_list])[T_indicies]*np.cos(theta) -
                                    (self.acs_data[y_name].to_numpy()[acs_index_list])[T_indicies]*np.sin(theta))
                        # V_min, V_max = 0.0075, 0.0077
                    elif row_idx == 1 and col_idx == 1:
                        x_name = self.acs_data.columns[name_idx - 1]
                        y_name = self.acs_data.columns[name_idx]
                        # print("plot {}: x-{}, y-{}".format(name_idx, x_name, y_name))
                        rotation = ((self.acs_data[x_name].to_numpy()[acs_index_list])[T_indicies]*np.sin(theta) +
                                    (self.acs_data[y_name].to_numpy()[acs_index_list])[T_indicies]*np.cos(theta))
                        # V_min, V_max = -24E-5, -18E-5
                        
                    # std_multiplier = 2.5 defined as input to function
                    V_min, V_max = (rotation.mean() - std_multiplier*rotation.std()), (rotation.mean() + std_multiplier*rotation.std())
                    # print(rotation.mean(), rotation.std(), V_min, V_max)
                    limit_list.append([V_min, V_max])
                    
                    rotation_list.append(rotation)
               
            select_data_points = np.logical_and(rotation>V_min, rotation<V_max)
            
            for idx, val in enumerate(limit_list):
                select_data_points = np.logical_and(select_data_points, (np.logical_and(rotation_list[idx]>val[0], rotation_list[idx]<val[1])))

            name_idx = 0
            for row_idx, row in enumerate(ax):
                for col_idx, subplot in enumerate(row):
                    col_name = self.acs_data.columns[name_idx]
                    if row_idx == 0:
                        lockin_color = 'cornflowerblue'
                    else:
                        lockin_color = 'coral'
                    s_plot = subplot.scatter(
                        (acs_temperature[T_indicies])[select_data_points],
                        (rotation_list[name_idx])[select_data_points],
                        # self.acs_data[col_name].to_numpy()[acs_index_list])[T_indicies]
                        marker='.',
                        color=lockin_color,
                        label=col_name
                        )
                    name_idx += 1

        
            ax[0][0].set_ylabel('V')
            ax[1][0].set_ylabel('V')
            ax[1][0].set_xlabel('Temperature, K')
            ax[1][1].set_xlabel('Temperature, K')
            ax[0][0].set_title("Start time: {}".format(time_period[0]))
            
            for row in ax:
                for subplot in row:
                    subplot.legend(loc=2)
                    
            fig.subplots_adjust(wspace=0.3, hspace=0.3)
            
            save_data = np.concatenate((np.c_[(acs_time[T_indicies])[select_data_points]+time_0], 
                                        np.c_[(acs_temperature[T_indicies])[select_data_points]], 
                                        np.c_[(rotation_list[0])[select_data_points]],
                                        np.c_[(rotation_list[1])[select_data_points]],
                                        np.c_[(rotation_list[2])[select_data_points]],
                                        np.c_[(rotation_list[3])[select_data_points]]), 
                                       axis=1)
            
            print(save_data.shape)
            
            header = "time, s\ttemperature, K\tL1: Vx, V\tL1: Vy, V\tL2: Vx, V\tL2: Vy, V"
            
            
            if save_select_data[0]==True:
                np.savetxt(r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\archive-data\data\select_data\select_{}_acs.dat".format(save_select_data[1]), save_data, delimiter='\t', header=header)
   
# %%                

    def display_tf_data(self, temperature=0, scale=24*3600, time_period=["08-21", "08-21"], T_min=4, T_max=300):
        
        time_0 = self.get_timestamp_from_day(time_period[0])
        time_1 = self.get_timestamp_from_day(time_period[1], end_of_day=1)
        
        # tf_width = self.tf_data['x:Width, Hz'].to_numpy()
        # tf_frequency = self.tf_data['x:Frequency, Hz'].to_numpy()
        
        tf_width = self.tf_data['x:Width, Hz'].to_numpy()
        tf_frequency = self.tf_data['x:Frequency, Hz'].to_numpy()
        
        
        tf_time = self.tf_data['# Time, s'].to_numpy()
        tf_index_list = [idx for idx, val in enumerate(tf_time) if (val > time_0 and val < time_1)]
        tf_time = tf_time - time_0
        
        sort_time_idx = tf_time.argsort()
        tf_time=tf_time[sort_time_idx]
        tf_width=tf_width[sort_time_idx]
        tf_frequency=tf_frequency[sort_time_idx]
        
        tf_time_ind = np.logical_and(tf_time>0, tf_time<time_1-time_0)
        tf_time=tf_time[tf_time_ind]
        tf_width=tf_width[tf_time_ind]
        tf_frequency=tf_frequency[tf_time_ind]
        
        mct_temp_name = self.mct_data.columns[3]
        mct_time_name = self.mct_data.columns[0]
        
        mct_volt_name = self.mct_data.columns[2]
        mct_ratio_name = self.mct_data.columns[1]
        
        # mct_temp = (self.mct_data[mct_temp_name])[1:].to_numpy(dtype=float)
        mct_time = (self.mct_data[mct_time_name])[1:].to_numpy(dtype=float)
        
        mct_volt = (self.mct_data[mct_volt_name])[1:].to_numpy(dtype=float)
        mct_ratio = (self.mct_data[mct_ratio_name])[1:].to_numpy(dtype=float)
        
        from tuning_fork.mct import MCT_V2Tv
        mct_temp = MCT_V2Tv(Vin=mct_volt, ratio=mct_ratio)[0]
        
        mct_time_index = np.logical_and(mct_time>time_0, mct_time<time_1)
        
        mct_time = mct_time[mct_time_index] - time_0
        mct_temp = mct_temp[mct_time_index]
        
        if temperature == -1:
            
            from tuning_fork import TF_visc
            # TF_visc.foVac_commFork = 32776.8 # Cell
            TF_visc.foVac_commFork = 32852.0 # Silver
            meff_factor = 0.875
            mvac = 0.24267*TF_visc.rhoq*TF_visc.L*TF_visc.W*TF_visc.T
            TF_visc.mvac = mvac * meff_factor
            
            tf_temp = TF_visc.Meas_Temp(tf_width, tf_frequency)       
            fig, ax = plt.subplots(1,1)
            ax.plot(tf_time/3600/24, tf_temp*1E3, label="TF_Temp")
            ax.plot(mct_time/3600/24, mct_temp*1E3, label="MCT_Temp")
            ax.set_ylabel("Temp, mK")
            ax.set_xlabel("Time, days")
            ax.set_title(str(meff_factor)+ " TF Mass" )
            ax.legend()
        
            
            
        elif temperature == 0:
            width_idx = np.logical_and(tf_width<20, tf_width>0)
            freq_idx = np.logical_and(tf_frequency<32900, tf_frequency>32500)
            
            fig, ax = plt.subplots(2,1, sharex=True)
            
            ax[0].plot(tf_time[width_idx]/3600/24, tf_width[width_idx])
            ax[1].plot(tf_time[freq_idx]/3600/24, tf_frequency[freq_idx]/1000)
            ax[0].set_title("Silver NS TFT: %s @ RT" % (time_period[0]))
            ax[0].set_ylabel("Width, hz")
            ax[1].set_ylabel("frequency, khz")
            ax[1].set_xlabel("time, days")
            ax[0].grid()
            ax[1].grid()
            
            print("Average Vacuum Width: %.6f hz" % (tf_width[width_idx].mean()))
            print("Average Vacuum Freq:  %.1f hz" % (tf_frequency[freq_idx].mean()))
            print("Num Points: %d" % (len(tf_frequency[freq_idx])))
            
        elif temperature == 1:
            diode_time = self.diode_data['# Time, s'].to_numpy()
            diode_index_list = [idx for idx, val in enumerate(diode_time) if (val > time_0 and val < time_1)]
            diode_time = diode_time - time_0
        
        
            arr1inds = diode_time[diode_index_list].argsort()
            tf_temperature = np.interp(tf_time[tf_index_list], (diode_time[diode_index_list])[arr1inds], (self.diode_data[', Temperature, K'].to_numpy()[diode_index_list])[arr1inds])
            tf_temperature = np.nan_to_num(tf_temperature, nan=0.0)
            
            T_indicies = [idx for idx, val in enumerate(tf_temperature) if (val > T_min and val < T_max)]
        
            fig, ax = plt.subplots(3,1, figsize=(8, 4))
            # Plot 1
            ax_00 = ax[0].scatter(
                (tf_time[tf_index_list])[T_indicies]/scale, 
                (abs(self.tf_data['x:Width, Hz'].to_numpy())[tf_index_list])[T_indicies],
                c=tf_temperature[T_indicies],
                cmap="inferno",
                s=4,
                label='tf width vs time',
                )
            ax[0].set_xlabel('Time, Days')
            plt.colorbar(ax_00, ax=ax[0], label='T, K')
            
            # Plot 2
            ax_01 = ax[1].scatter(
                tf_temperature[T_indicies], 
                (abs(self.tf_data['x:Width, Hz'].to_numpy())[tf_index_list])[T_indicies],
                s=4,
                label='tf width vs Temperature',
                color='coral'
                )
            ax[1].set_xlabel('Temperature, K')
            
            # Plot 3
            ax_02 = ax[2].scatter(
                (tf_time[tf_index_list])[T_indicies]/scale, 
                tf_temperature[T_indicies],
                s=4,
                label='tf T vs time',
                color='cornflowerblue'
                )
            ax[2].set_xlabel('Time, Days')
        
            ax[0].set_title("Start time: {}".format(datetime.fromtimestamp(time_0)))
            
            for subplot in ax:
                subplot.legend(loc=2)
            
            fig.subplots_adjust(wspace=0.3, hspace=0.3)
        
        elif temperature == 2:
            from tuning_fork import TF_visc
            
            tf_viscosity = TF_visc.Meas_Viscosity(width=tf_width, frequency=tf_frequency)
            tf_temp = self.tf_data['Temperature, K'].to_numpy()

            fig, ax = plt.subplots(3,1, figsize=(8, 4))
            # Plot 1
            ax_00 = ax[0].scatter(
                (tf_time[tf_index_list])/scale, 
                (abs(self.tf_data['Width, Hz'].to_numpy())[tf_index_list]),
                s=6,
                color='firebrick',
                label='tf width vs time',
                )
            # ax[0].set_xlabel('Time, Days')
            
            # Plot 2
            ax_01 = ax[1].scatter(
                (tf_time[tf_index_list])/scale, 
                (abs(self.tf_data['# Frequency, Hz'].to_numpy())[tf_index_list]),
                s=6,
                label='tf resonance vs time',
                color='coral'
                )
            
            ax[1].set_xlabel('Time, Days')
        
            ax_02 = ax[2].scatter(
                tf_temp[tf_index_list], 
                tf_viscosity[tf_index_list]*1E6,
                s=6,
                color='lightgreen',
                label='tf viscosity vs temperature'
                )
            ax[0].set_title("Start time: {}".format(datetime.fromtimestamp(time_0)))
            
            ax[2].set_xlabel('Temperature, K')
            
            ax[2].set_ylabel("Viscosity, $\mu$Pa s")
            
            for subplot in ax:
                subplot.legend(loc=2)
            
            fig.subplots_adjust(wspace=0.3, hspace=0.3)
            
        elif temperature == 3:
            from tuning_fork import TF_visc
            
            # R8 Thermometer
            r8_time = self.rt_data["# Time, s"].to_numpy()
            r8_index_list = np.logical_and(r8_time>time_0, r8_time<time_1)
            
            channels = self.rt_data.columns[2:]

            rt_resistances = (self.rt_data.to_numpy()[r8_index_list, 2:])
                
            r8_resistance = self.rt_data["Channel 1: R8, Ohms"].to_numpy()
            
            r8_time = r8_time[r8_index_list] - time_0
            r8_resistance = r8_resistance[r8_index_list]
            
            R8_calibration=r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration\R8_RT_Curve.dat"
            r8_cal = pd.read_csv(R8_calibration, sep="\t")

            r8_sorted_idx = r8_cal["# R, Ohms"].to_numpy().argsort()
            r8_temp = np.interp(r8_resistance, r8_cal["# R, Ohms"].to_numpy()[r8_sorted_idx], r8_cal["T, K"].to_numpy()[r8_sorted_idx])
            
            r8_temp_index_list = np.logical_and(r8_temp<T_max, r8_temp>T_min)
            
            r8_time = r8_time[r8_temp_index_list]
            r8_temp = r8_temp[r8_temp_index_list]
            
            rt_resistances = rt_resistances[r8_temp_index_list][:]
            
            # mct thermometer
            mct_temp_name = self.mct_data.columns[3]
            mct_time_name = self.mct_data.columns[0]
            
            mct_volt_name = self.mct_data.columns[2]
            mct_ratio_name = self.mct_data.columns[1]
            
            # mct_temp = (self.mct_data[mct_temp_name])[1:].to_numpy(dtype=float)
            mct_time = (self.mct_data[mct_time_name])[1:].to_numpy(dtype=float)
            
            mct_volt = (self.mct_data[mct_volt_name])[1:].to_numpy(dtype=float)
            mct_ratio = (self.mct_data[mct_ratio_name])[1:].to_numpy(dtype=float)
            
            from tuning_fork.mct import MCT_V2Tv
            mct_temp = MCT_V2Tv(Vin=mct_volt, ratio=mct_ratio)[0]
            
            mct_time_index = np.logical_and(mct_time>time_0, mct_time<time_1)
            
            mct_time = mct_time[mct_time_index] - time_0
            mct_temp = mct_temp[mct_time_index]
            
            # mct_time_sort = np.argsort(mct_time)
            
            # mct_time = mct_time[mct_time_sort]
            # mct_temp = mct_temp[mct_time_sort]
            
            mct_temp_idx = np.logical_and(mct_temp<T_max, mct_temp>T_min)
            
            mct_time = mct_time[mct_temp_idx] 
            mct_temp = mct_temp[mct_temp_idx]
            
            # TF thermometer

            # tf_viscosity = TF_visc.Meas_Viscosity(width=tf_width[tf_index_list], frequency=tf_frequency[tf_index_list])
            # tf_viscosity = (tf_viscosity[tf_index_list])[temp_idx]
            
            # tf_temp = self.tf_data['Temperature, K'].to_numpy()
            # tf_temp = np.interp(tf_time, mct_time, mct_temp)
            
            tf_temp = TF_visc.Meas_Temp(width=np.abs((tf_width)[tf_index_list]), frequency=(tf_frequency)[tf_index_list])
            
            temp_idx = np.logical_and(tf_temp<T_max, tf_temp>T_min)
            
            tf_temp = (tf_temp)[temp_idx]
            tf_time = (tf_time[tf_index_list])[temp_idx]
            
            fig, ax = plt.subplots(1,1, figsize=(8, 4))
            
            ax.scatter(
                tf_time/scale, 
                tf_temp,
                # np.abs(((tf_width[not_nan])[tf_index_list])[temp_idx]),
                # ((tf_frequency[not_nan])[tf_index_list])[temp_idx],
                s=12,
                # label='tf width vs temperature'
                # label='tf frequency vs temperature'
                # label='tf Viscosity vs temperature'
                label='tf temperature vs time'
                )
            
            ax.scatter(
                mct_time/scale, 
                mct_temp,
                # np.abs(((tf_width[not_nan])[tf_index_list])[temp_idx]),
                # ((tf_frequency[not_nan])[tf_index_list])[temp_idx],
                s=8,
                # label='tf width vs temperature'
                # label='tf frequency vs temperature'
                label='mct Temperature vs Time'
                )
            
            ax.scatter(
                r8_time/scale, 
                r8_temp,
                # np.abs(((tf_width[not_nan])[tf_index_list])[temp_idx]),
                # ((tf_frequency[not_nan])[tf_index_list])[temp_idx],
                s=4,
                # label='tf width vs temperature'
                # label='tf frequency vs temperature'
                label='R8 Temperature vs Time'
                )
            
            ax2 = ax.twinx()
            
            ax2.scatter(
                r8_time/scale, 
                rt_resistances[:, 0],
                s=4,
                color='tab:red',
                label='{}'.format(channels[0])
                )
            ax2.set_ylabel("$\Omega$")
            
            ax.set_title("Start time: {}".format(datetime.fromtimestamp(time_0)))
            
            # ax.set_xlabel('Temperature, K')
            ax.set_xlabel('Time, days')
            
            # ax.set_ylabel("Width, Hz")
            # ax.set_ylabel("Frequency, Hz")
            # ax.set_ylabel("Viscosity, $\mu$Pa s")
            ax.set_ylabel('Temperature, K')
            
            ax.legend(loc=2)
            
            fig.subplots_adjust(wspace=0.3, hspace=0.3)
            
            class Index:
                
                ind=0
                    
                def next(self, event):
                    if self.ind<len(channels)-1:
                        self.ind+=1
                    else:
                        self.ind=0
                    self.plot()
                    
                def prev(self, event):
                    if self.ind>0:
                        self.ind-=1
                    else:
                        self.ind=len(channels)-1
                    self.plot()
                 
                def plot(self):
                    ax2.clear()
                    ax2.scatter(
                            r8_time/scale, 
                            rt_resistances[:, self.ind],
                            s=4,
                            color='tab:red',
                            label='{}'.format(channels[self.ind])
                            )
                    ax2.set_ylabel("$\Omega$")
            callback = Index()
            # [x, y, w, h]
            axprev = plt.axes([0.86, 0.90, 0.1, 0.075])
            axnext = plt.axes([0.75, 0.90, 0.1, 0.075])
            bnext = Button(axprev, 'Next')
            bnext.on_clicked(callback.next)
            bprev = Button(axnext, 'Previous')
            bprev.on_clicked(callback.prev)

            axnext._button = bnext
            axprev._button = bprev

                    
            
            # tf_time = (((tf_time[not_nan])[tf_index_list])[temp_idx])[sorted_idx] + time_0
            
            # save_loc = r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\archive-data\data\select_data"
            # file_name = "\\9-14_9-29_multi-temperature_data.dat"
            
            # tf_save_indexes = np.logical_and(~np.isnan(tf_time), ~np.isnan(tf_temp))
            # tf_time = tf_time[tf_save_indexes]
            # tf_temp = tf_temp[tf_save_indexes]
            
            # mct_save_indexes = np.logical_and(~np.isnan(mct_time), ~np.isnan(mct_temp))
            # mct_time = mct_time[mct_save_indexes]
            # mct_temp = mct_temp[mct_save_indexes]
            
            # r8_save_indexes = np.logical_and(~np.isnan(r8_time), ~np.isnan(r8_temp))
            # r8_time = r8_time[r8_save_indexes]
            # r8_temp = r8_temp[r8_save_indexes]
            
            # plt.close(fig)
            # X = np.asarray([tf_time+time_0, tf_temp, mct_time+time_0, mct_temp, r8_time+time_0, r8_temp])
            # max_length = 0
            # for column in range(len(X)):
            #     if len(X[column])>max_length:
            #         max_length = len(X[column])
                
            # saving_array = np.empty((max_length,len(X),))
            # saving_array[:] = np.nan
            # for column in range(len(X)):
            #     saving_array[:len(X[column]), column] = X[column]
            
            # np.savetxt(
            # fname=save_loc+file_name, 
            # X=saving_array, 
            # header="Cell TF Time, s\tTF Temperature, K\tMCT Time, s\tMCT Temperature, K\tR8 Time, s\tR8 Temperature, K", 
            # delimiter='\t'
            # )
            
            
            
        
# %%
        
    def display_diode_data(self, scale=24*3600, time_period=["08-21", "08-21"]):
        time_0 = self.get_timestamp_from_day(time_period[0])
        time_1 = self.get_timestamp_from_day(time_period[1], end_of_day=1)
        
        diode_time = np.asarray(self.diode_data['# Time, s'].values) - time_0
        
        fig, ax = plt.subplots(1,1, figsize=(8, 4))
        # Plot 1
        ax_00 = ax.scatter(
            diode_time/scale,
            np.asarray(self.diode_data[', Temperature, K'].values),
            s=4,
            label='diode'
            )
        
        ax.set_title("Start time: {}".format(time_period[0]))
        ax.set_xlabel('Time, Days')
        
        ax.legend(loc=2)
        
        fig.subplots_adjust(wspace=0.3, hspace=0.3)
        
        
# %%
    
    def display_rt_data(self, mode=1, show_R8=True, R8_calibration=r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration\R8_RT_Curve.dat", 
                        scale=24*3600, time_period=["07-01", "07-14"], T_min=4, T_max=270):
            time_0 = self.get_timestamp_from_day(time_period[0])
            time_1 = self.get_timestamp_from_day(time_period[1], end_of_day=1)
        
            rt_time = self.rt_data['# Time, s'].to_numpy()
            rt_index_list = [idx for idx, val in enumerate(rt_time) if (val > time_0 and val < time_1)]
            rt_time = rt_time[rt_index_list] - time_0
            
            r8_cal = pd.read_csv(R8_calibration, sep="\t")
            # for col in r8_cal.columns:
            #     print(col)
            #     print(r8_cal[col].to_numpy())
            
            if show_R8 == True:
                y_name = self.rt_data.columns[1]
                r8_sorted_idx = r8_cal["# R, Ohms"].to_numpy().argsort()
                r8_temp = np.interp((self.rt_data[y_name].to_numpy())[rt_index_list], r8_cal["# R, Ohms"].to_numpy()[r8_sorted_idx], r8_cal["T, K"].to_numpy()[r8_sorted_idx])
                
                plt.figure()
                plt.scatter(rt_time/scale,
                            r8_temp*1000,
                            s=2
                            )
                plt.ylabel('T, mK')
                plt.xlabel('Time, days')
                plt.title('R8: ' + time_period[0])
                
            
            if mode == 1:
                diode_time = self.diode_data['# Time, s'].to_numpy()
                diode_index_list = [idx for idx, val in enumerate(diode_time) if (val > time_0 and val < time_1)]
                diode_ind = diode_time[diode_index_list].argsort()
            
                rt_temperature = np.interp(rt_time, (diode_time[diode_index_list])[diode_ind] - time_0, (np.asarray(self.diode_data[', Temperature, K'].to_numpy()[diode_index_list])[diode_ind]))
                rt_temperature = np.nan_to_num(rt_temperature, nan=0.0)
                
                temperature_points = np.logical_and(rt_temperature>T_min, rt_temperature<T_max)
            
                fig, ax = plt.subplots(2, 1)

                # Plot 1
                ax_00 = ax[0].scatter(
                    rt_time[temperature_points]/scale, 
                    (self.rt_data[y_name].to_numpy()[rt_index_list])[temperature_points],
                    marker='.',
                    c=rt_temperature[temperature_points],
                    cmap="inferno",
                    label=y_name
                    )
                plt.colorbar(ax_00, ax=ax[0], label='T, K')
                
                ax[0].set_title("Start time: {}".format(datetime.fromtimestamp(time_0)))
                ax[0].set_xlabel('Time, Days')
                ax[0].set_ylabel('Resistance, $\Omega$')
                
                # Plot 2
                ax_10 = ax[1].scatter(rt_temperature[temperature_points], 
                              (self.rt_data[y_name].to_numpy()[rt_index_list])[temperature_points], 
                              marker='.',
                              label = 'R vs T'
                              )
                ax[1].set_xlabel('Temperature, K')
                ax[1].set_ylabel('Resistance, $\Omega$')
                
                fig.subplots_adjust(wspace=0.3, hspace=0.3)
                
                for subplot in ax:
                    subplot.legend(loc=2)
                    
            elif mode == 2:
                fig, ax = plt.subplots(9, 1, sharex=True)
                for i in range(9):
                    y_name = self.rt_data.columns[i+1]
                    ax[i].scatter(
                        rt_time/scale,
                        (self.rt_data[y_name].to_numpy())[rt_index_list],
                        s=2,
                        label=y_name
                        )
                    ax[i].set_ylabel('R, $\Omega$')
                
                ax[0].set_title('R Thermometers: ' + time_period[0])
                ax[8].set_xlabel('Time, Hrs')
                for subplot in ax:
                    subplot.legend(loc=2)
                # fig.subplots_adjust(wspace=0.5, hspace=0.5)
                
                    
                
            ############################

            class Index:
                def __init__(self, data):
                    self.ind = 1
                    self.fitted = False
                    self.rt_data = data
            
                def next(self, event):
                    if self.ind < len(self.rt_data.columns)-1:
                        self.ind += 1
                        channel = self.rt_data.columns[self.ind]
                        ydata = (self.rt_data[channel].to_numpy()[rt_index_list])[temperature_points]
                        
                        ax_00.set_offsets(np.transpose([rt_time[temperature_points]/scale, ydata]))
                        # ax_00.set_offsets(np.concatenate((np.c_[rt_time[temperature_points]/scale], np.c_[ydata]), axis=1))
                        ax_00.set_label(channel)
                        
                        ax_10.set_offsets(np.transpose([rt_temperature[temperature_points], ydata]))
                        ax_10.set_label(channel)
                        
                        for subplot in ax:
                            subplot.set_ylim(ydata.min(), ydata.max())
                            subplot.legend(loc=2)
    
                        plt.draw()
                    else:
                        pass
            
                def prev(self, event):
                    if self.ind > 1:
                        self.ind -= 1
                        channel = self.rt_data.columns[self.ind]
                        ydata = (self.rt_data[channel].to_numpy()[rt_index_list])[temperature_points]
    
                        ax_00.set_offsets(np.transpose([rt_time[temperature_points]/scale, ydata]))
                        # ax_00.set_offsets(np.concatenate((np.c_[rt_time[temperature_points]/scale], np.c_[ydata]), axis=1))
                        ax_00.set_label(channel)
                        
                        ax_10.set_offsets(np.transpose([rt_temperature[temperature_points], ydata]))
                        ax_10.set_label(channel)
    
                        for subplot in ax:
                            subplot.set_ylim(ydata.min(), ydata.max())
                            subplot.legend(loc=2)
                        plt.draw()
                    else:
                        pass
                
                def fit(self, event):
                    ax[1].clear()
                    channel = self.rt_data.columns[self.ind]
                    ydata = (self.rt_data[channel].to_numpy()[rt_index_list])[temperature_points]
                    
                    x = rt_temperature[temperature_points]
                    x_order = x.argsort()
                    ax_10 = ax[1].scatter(x[x_order], 
                              ydata[x_order], 
                              marker='.',
                              label = 'R vs T'
                              )
                    if self.fitted == False:
                        popt, pcov = curve_fit(poly, x[x_order], ydata[x_order])
                        self.fit_line = ax[1].plot(x[x_order], poly(x[x_order], *popt), label='fit', color='orange')
                        self.fitted = True
                    else:
                        self.fitted = False
                    
                    ax[1].set_xlabel('Temperature, K')
                    ax[1].set_ylabel('Resistance, $\Omega$')
                    ax[1].legend(loc=2)
                    plt.draw()
                    
                    

            if diode == True:     
                callback = Index(self.rt_data)
                # [x, y, w, h]
                axprev = plt.axes([0.86, 0.90, 0.1, 0.075])
                axnext = plt.axes([0.75, 0.90, 0.1, 0.075])
                axfit = plt.axes([0.05, 0.90, 0.1, 0.075])
                bnext = Button(axprev, 'Next')
                bnext.on_clicked(callback.next)
                bprev = Button(axnext, 'Previous')
                bprev.on_clicked(callback.prev)
                bfit = Button(axfit, 'Fit')
                bfit.on_clicked(callback.fit)
                
                axnext._button = bnext
                axprev._button = bprev
                axfit._button = bfit
            
            #############################
            
# %%

    def calibrate_rt_to_diode(self, file_name, mode=1, verbose=1, 
                        scale=24*3600, time_period=["07-01", "07-14"], T_min=5, T_max=100, density = 200):
        
        time_0 = self.get_timestamp_from_day(time_period[0])
        time_1 = self.get_timestamp_from_day(time_period[1], end_of_day=1)
            
        rt_time = self.rt_data['# Time, s'].to_numpy()
        rt_time_idx = np.logical_and(rt_time<time_1, rt_time>time_0)
        rt_time = rt_time[rt_time_idx] - time_0
        
        rt_resistances = self.rt_data.to_numpy()[:, 1:]
        rt_resistances = rt_resistances[rt_time_idx][:]
        
        # print(np.shape(rt_resistances))
        
        f_dir= r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration\{}-{}_".format(*time_period)
        # 
        if mode == 0:
            poly_num = 8
            X = np.transpose([np.arange(0, poly_num + 1)])
            header = "poly-order"
            # print(X)
            
            for idx, rt_name in enumerate(self.rt_data.columns):
                if idx == 0:
                    pass
                else:
                    ordered_ind = rt_resistances[idx].argsort()
    
                    z = np.polyfit(diode_temp[ordered_ind], rt_resistances[ordered_ind], poly_num)
                    # print(z)
                    
                    header = header + "\t" + rt_name
                    
                    X = np.concatenate((X, np.transpose([z])), axis=1)
                    
            
    
            f_dir= r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration\{}-{}_".format(*time_period)
            fname = f_dir + "fitted_" + file_name
            
            np.savetxt(fname, X , header=header, delimiter='\t')
        
        elif mode == 1:
            from tuning_fork import TF_visc
            
            names = self.rt_data.columns
            
            """ for Diode """
            diode_time = self.diode_data['# Time, s'].to_numpy()
            
            diode_time_idx = np.logical_and(diode_time>time_0, diode_time<time_1)
            
            diode_time = diode_time[diode_time_idx] - time_0
            
            diode_temp = self.diode_data[', Temperature, K'].to_numpy()[diode_time_idx]
            
            diode_time_sort = diode_time.argsort()
            
            temperature = np.interp(rt_time, diode_time[diode_time_sort], diode_temp[diode_time_sort])
            
            temperature_idx = np.logical_and(temperature>T_min, temperature<T_max)
            
            temperature = temperature[temperature_idx]
            
            rt_resistances = rt_resistances[temperature_idx][:]
        
            
            """ End Diode """
           
            """ for TF """
            
            # tf_time = self.tf_data['Time, s'].to_numpy()
            # tf_time_idx = np.logical_and(tf_time>time_0, tf_time<time_1)
            # tf_time = tf_time - time_0
            
            # tf_width = self.tf_data['Width, Hz'].to_numpy()
            # tf_frequency = self.tf_data['# Frequency, Hz'].to_numpy()
            
            # tf_time = tf_time[tf_time_idx]
            # tf_width = tf_width[tf_time_idx]
            # tf_frequency = tf_frequency[tf_time_idx]
            
            # temperature = TF_visc.Meas_Temp(width=tf_width, frequency=tf_frequency)
            
            # temperature = np.interp(rt_time[::-1], tf_time[::-1], temperature)[::-1]
            
            # temperature_idx = np.logical_and(temperature>T_min, temperature<T_max)
            
            # rt_time = rt_time[temperature_idx]
            # rt_resistances = rt_resistances[temperature_idx][:]
            # temperature = temperature[temperature_idx]

            """ End TF """
            
            sort_temp_indexs = temperature.argsort()
            
            density_length = int(len(temperature)/density)
            
            T = []
            for i in range(density):
                if density_length*(i+1) >= len(temperature)-1:
                    value = np.mean((temperature[sort_temp_indexs])[density_length*i:])
                else:
                    value = np.mean((temperature[sort_temp_indexs])[density_length*i:density_length*(i+1)])
                T.append(value)
            data = np.c_[T]
            header = 'Temperature, K'
            for idx, name in enumerate(names[1:]):
                R = []
                for i in range(density):
                    if density_length*(i+1) >= len(temperature)-1:
                        value = np.mean((rt_resistances[sort_temp_indexs, idx])[density_length*i:])
                    else:
                        value = np.mean((rt_resistances[sort_temp_indexs, idx])[density_length*i:density_length*(i+1)])
                    # if points.size == 0:
                    #     if np.size(R) == 0:
                    #         print("No resistance in temperature range: {}-{}".format((T_min+T_range*i), (T_min+T_range*(i+1))))
                    #         raise ValueError
                        # else:
                        #     value = R[-1]
                    R.append(value)
                data = np.concatenate((data, np.c_[R]), axis=1)
                header = header + '\t' + name
            
            if verbose == 1:
                plot_num = len(names)-1
                fig, ax = plt.subplots(plot_num, 1)
                additional_points = [495, 496, 7374, 7460, 2867, 1526, 1.74E6, 1.68E6, 1486]
                
                for idx, subplot in enumerate(ax):
                    subplot.scatter(temperature, rt_resistances[:, idx])
                    subplot.scatter(data[:,0], data[:, 1+idx], s=8, color='coral')
                    subplot.scatter(4.3, additional_points[idx], color='green')
                    subplot.set_ylabel("$\Omega$")
                    
                ax[-1].set_xlabel("Temperature, K")
                
            fname = f_dir + file_name
            np.savetxt(fname, data, header=header, delimiter='\t')
                
        
        
        
            
# %%

    def calibrated_rt_curve(self, diode=True, calibration=r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration\temp-vs-resistance_rt-diode_calibration_07-01_07-14.dat", 
                        scale=24*3600, time_period=["07-01", "07-14"], T_min=1, T_max=100):
        
        time_0 = self.get_timestamp_from_day(time_period[0])
        time_1 = self.get_timestamp_from_day(time_period[1], end_of_day=1)
    
        rt_time = np.asarray(self.rt_data['# Time, s'].to_numpy())
        rt_index_list = [idx for idx, val in enumerate(rt_time) if (val > time_0 and val < time_1)]
        rt_time = rt_time[rt_index_list] - time_0
        
        poly_cal = pd.read_csv(calibration, sep="\t")
        # print(poly_cal)
        # for col in r8_cal.columns:
        #     print(col)
        #     print(r8_cal[col].to_numpy())
        
        
        channel = self.rt_data.columns[5]
        
        fig, ax = plt.subplots(2, 1)
        
        calibrated_T = np.polyval(poly_cal[channel].to_numpy(), (self.rt_data[channel].to_numpy())[rt_index_list])

        ax[0].scatter(rt_time/scale,
                    calibrated_T,
                    s=2
                    )
        ax[0].set_ylabel('T, mK')
        ax[0].set_xlabel('Time, Hrs')
        
        
        ax[1].scatter((self.rt_data[channel].to_numpy())[rt_index_list],
                    calibrated_T,
                    s=2
                    )
        ax[1].set_ylabel('T, mK')
        ax[1].set_xlabel('R, ohms')
        
        ax[0].set_title(channel + ' ' + time_period[0])
        
            
        
            

# %%


def get_files(directory, data_name):
    file_list = glob.glob(directory+'*.dat')
    df_files = pd.DataFrame(columns=['date', 'num'])
    
    for file in file_list:
        name, date, num = file[len(directory):-4].split('_')
        df_files = df_files.append({'date' : date, 'num' : int(num)}, ignore_index=True)
    file_dates = df_files['date'].unique()
    file_nums = df_files.groupby(['date']).max().to_numpy()[:,0]
    
    file_list = []
    for idx, value in enumerate(file_dates):
        file_list.append(directory+'{}_{}_{}.dat'.format(data_name, file_dates[idx],file_nums[idx]))
    return file_list
    
def get_directory(data_type, time_period, archive=True):
    if archive == True:
        return r'C:\Users\alexd\Documents\GitHub\data-monitoring\archive-data\data\{}\{}'.format(time_period, data_type)
    else:
        return r'C:\Users\alexd\Documents\GitHub\data-monitoring\data\{}\{}'.format(time_period, data_type)

cooldown_dates = {
        "cooldown_1": ["06-29", "07-14"],
        "cooldown_2": ["07-29", "08-17"],
        "cooldown_3": ["08-20", "08-26"],
        # "cooldown_4": ["08-25", "12-31"]
        # "cooldown_4": ["09-14", "09-29"]
        "cooldown_4": ["08-25", "08-31"],
        "cooldown_5": ["01-14-2022", "01-14-2022"]
        }

def show_diode_data(time_period="cooldown_2", verbose_import=False):
    
    explorer = data_explorer()
    
    diode_directory = get_directory('diode_data', time_period)
    
    explorer.import_diode_data_from_directory(directory=diode_directory, verbose=verbose_import)
    
    explorer.display_diode_data(time_period=cooldown_dates[time_period])

def show_acs_data(archive=True, time_period="cooldown_1", T_min=2, T_max=300.0, diode=True, plot_VT=True, plot_V_time=True, verbose_import=False, save_select_data=[False], std_multiplier=4):
    explorer = data_explorer()

    diode_directory = get_directory('diode_data', time_period)
    acs_directory = get_directory('acs_data', time_period)

    explorer.import_diode_data_from_directory(directory=diode_directory, verbose=verbose_import)
    explorer.import_acs_data_from_directory(directory=acs_directory, verbose=verbose_import)
    
    explorer.display_acs_data(diode=diode, time_period=cooldown_dates[time_period], T_min=T_min, T_max=T_max, plot_VT=plot_VT, plot_V_time=plot_V_time, save_select_data=[save_select_data, time_period], std_multiplier=4)
    
def show_tf_data(temperature, time_period, T_min, T_max): 
    
    # explorer = data_explorer()   
    
    # directory=r'C:\Users\alexd\Documents\GitHub\data-monitoring\archive-data\data\diode_data'
    
    # tf_directory = get_directory('TFT_data\\{}_TFT\\fits'.format(thermometer), time_period)
    # diode_directory = get_directory('diode_data', time_period)
    # mct_directory = get_directory('MCT_data', time_period)
    # rt_directory = get_directory('rt_data', time_period)
    
    # print(tf_directory)
    
    # explorer.import_tf_data_from_directory(directory=tf_directory, verbose=verbose_import)
    
    # if temperature == 1:
    #     explorer.import_diode_data_from_directory(directory=diode_directory, verbose=verbose_import)
    # elif temperature == 2:
    #     pass
    # elif temperature == 3:
    #     explorer.import_MCT_data_from_directory(directory=mct_directory)
    #     explorer.import_rt_data_from_directory(directory=rt_directory, verbose=verbose_import)

    explorer.display_tf_data(temperature=temperature, time_period=cooldown_dates[time_period], T_min=T_min, T_max=T_max)
    
def show_rt_data(file_name, time_period, display_mode=1, calibrate_mode=1, T_min=10, T_max=270, density = 200, verbose_import=False):
    
    
    
    rt_directory = get_directory('rt_data', time_period)
    diode_directory = get_directory('diode_data', time_period)
    tf_directory = get_directory('TFT_data\\{}_TFT\\fits'.format("CELL"), time_period)
    
    explorer.import_tf_data_from_directory(directory=tf_directory, verbose=verbose_import)
    explorer.import_rt_data_from_directory(directory=rt_directory, verbose=verbose_import)
    explorer.import_diode_data_from_directory(directory=diode_directory, verbose=verbose_import)
    
    if display_mode==1:
        explorer.display_rt_data(mode=calibrate_mode, time_period=cooldown_dates[time_period], T_min=T_min, T_max=T_max)
    elif display_mode == 2:
        explorer.calibrated_rt_curve(time_period=cooldown_dates[time_period], T_min=T_min, T_max=T_max)
    elif display_mode == 3:
        explorer.calibrate_rt_to_diode(file_name=file_name,
                                       mode=calibrate_mode,
                                       time_period=cooldown_dates[time_period], 
                                       T_min=T_min, T_max=T_max, 
                                       density=density)
        


    
    
# %%           
if __name__ == "__main__":
    import matplotlib as mpl
    mpl.rcParams['figure.dpi'] = 300 
    # show_diode_data(time_period='cooldown_4')
    
    # show_acs_data(diode=False, plot_V_time=True, time_period='cooldown_4', 
    #               T_min=3, T_max=50, verbose_import=False, save_select_data=False, std_multiplier=2.5)
    
    time_period='cooldown_5'
    thermometer = "silver-NS"
    # thermometer = "Cell"
    verbose_import=False
    
    # %%
    explorer = data_explorer()
    
    tf_directory = get_directory('TFT_data\\{}_TFT\\fits'.format(thermometer), time_period)
    explorer.import_tf_data_from_directory(directory=tf_directory, verbose=verbose_import)
    mct_directory = get_directory('MCT_data', time_period)
    explorer.import_MCT_data_from_directory(directory=mct_directory)
    # explorer.import_rt_data_from_directory(directory=rt_directory, verbose=verbose_import)
    # explorer.import_diode_data_from_directory(directory=diode_directory, verbose=verbose_import)
    
    # %%
    show_tf_data(temperature = -1, time_period=time_period, T_min=0.001, T_max=0.200, )
    
    # show_rt_data(
    #               file_name="rvt_calibration_03.dat", time_period='cooldown_4', 
    #               display_mode=3, calibrate_mode=1, 
    #               T_min=4, T_max=77, 
    #               density=10
    #               )
    
    # test_get_file_data(directory=r'C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\data\diode_data')
    
    
    
    

