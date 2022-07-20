# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 13:49:03 2022

@author: physics-svc-mkdata
"""

import os
import numpy as np
import pandas as pd
from tuning_fork import Lorentz_Fitting as LF
from tuning_fork.TF_visc import Meas_Temp

from datetime import datetime
import time

class TFdata:
    def __init__(self, TF_name, save_folder):
        self.current_working_dir = os.getcwd()
        self.TF_name = TF_name
        self.save_folder = save_folder
        self.get_today()
        self.frequency_limit = 32600
        self.set_drive(1)
        self.set_current_amp(1)
        self.store_last_sweep([])
        x_header = "\tx:Frequency, Hz\tx:Amplitude, V\tx:Width, Hz\tx:Phase, Rad\tx:Background intercept, V\tx:Background slope, dV/df\tx:Background quadratic, d2V/d2f"
        y_header = "\ty:Frequency, Hz\ty:Amplitude, V\ty:Width, Hz\ty:Phase, Rad\ty:Background intercept, V\ty:Background slope, dV/df\ty:Background quadratic, d2V/d2f"
        self.header = "Time, s\tDrive, V\tCurrent Amp\tTemperature, K"+x_header+y_header
        
        self.Vx_names = ["x:Frequency, Hz", "x:Amplitude, V", "x:Width, Hz", "x:Phase, Rad", 
                    "x:Background intercept, V", "x:Background slope, dV/df", "x:Background quadratic, d2V/d2f"]
        self.Vy_names = ["y:Frequency, Hz", "y:Amplitude, V", "y:Width, Hz", "y:Phase, Rad", 
                    "y:Background intercept, V", "y:Background slope, dV/df", "y:Background quadratic, d2V/d2f"]
        
        self.sweep_header = "Time, s\tFrequency, hz\tVx, V\tVy, V\tDrive, V\tCurrent Amp"
        self.reset_sweep()
        self.reset_fits()
        self.reset_saved_fits()
        self.reset_fit_data()
        self.reset_saved_fit_data()
        self.reset_save_time()
        
        
    def reset_fit_data(self):
        self.fit_data = {"Time, s": [],
                         "Drive, V": [],
                         "Current Amp": [],
                         "Temperature, K": []
                         }
        for thing in self.Vx_names:
            self.fit_data[thing] = []
        for thing in self.Vy_names:
            self.fit_data[thing] = []
            
    def reset_saved_fit_data(self):
        self.saved_fit_data = {"Time, s": [],
                         "Drive, V": [],
                         "Current Amp": [],
                         "Temperature, K": []
                         }
        for thing in self.Vx_names:
            self.saved_fit_data[thing] = []
        for thing in self.Vy_names:
            self.saved_fit_data[thing] = []
    
    def append_fit_data(self, new_data):
        for i, key in enumerate(self.fit_data):
            self.fit_data[key].append(new_data[i])

        
    def get_today(self):
        now = datetime.now()
        self.today = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = time.mktime(self.today.timetuple())
        self.today = self.today.strftime("%Y-%m-%d")
        
    def store_last_sweep(self, sweep):
        self.last_sweep = np.array(sweep)
        
    def set_drive(self, value):
        self.drive = value
        
    def set_current_amp(self, value):
        self.current_amp=value
        
    def reset_save_time(self):
        self.last_save = time.time()
        
    def reset_fits(self):
        self.fits = []
    
    def reset_saved_fits(self):
        self.saved_fits = np.array([])
        
    def daily_save(self):
        # self.save_fits()
        self.save_fit_data()
        self.reset_save_time()
        # self.reset_fits()
        # self.reset_saved_fits()
        self.reset_fit_data()
        self.reset_saved_fit_data()
        self.get_today()
        
    def reset_sweep(self):
        self.sweep = []
        
    def append_sweep(self, new_values):
        if np.array(new_values).ndim == 1: 
            self.sweep.append(new_values)
            
    def append_fits(self, new_values):
        if np.array(new_values).ndim == 1: 
            self.fits.append(new_values)
            
    def fit_sweep(self):
        self.sweep = np.array(self.sweep)
        self.store_last_sweep(self.sweep)
        if self.sweep.ndim > 1:
            guess = [(self.sweep[-1, 1]+self.sweep[0, 1])/2, 0, (self.sweep[-1, 1]-self.sweep[0, 1])/8, 0, 0, 0, 0]
            self.xfit, xflag = LF.Lorentz_Fit_X_quad(self.sweep[:, 1], self.sweep[:, 2], guess)
            self.xfit[0], self.xfit[2] = np.abs(self.xfit[0]), np.abs(self.xfit[2])
            self.yfit, yflag = LF.Lorentz_Fit_Y_quad(self.sweep[:, 1], self.sweep[:, 3], guess)
            self.yfit[0], self.yfit[2] = np.abs(self.yfit[0]), np.abs(self.yfit[2])
            
            if xflag in [1,2,3,4]:
                self.T = Meas_Temp(width=self.xfit[2], frequency=self.xfit[0])
                # self.append_fits([self.sweep[:, 0].mean(), self.drive, self.current_amp, self.T, *self.xfit, *self.yfit])
                self.append_fit_data([self.sweep[:, 0].mean(), self.drive, self.current_amp, self.T, *self.xfit, *self.yfit])
                return xflag
            else:
                return 0
        else:
            return 0
        
    def getfilename(self, directory, file_tag, num=0):
        fname = self.current_working_dir+r"/data/{}/{}__{}.dat".format(directory, file_tag, num)
        if os.path.isdir(self.current_working_dir+"/data/"+directory) == False:
            os.makedirs(self.current_working_dir+"/data/"+directory)
        if os.path.isfile(fname):
            return self.getfilename(directory, file_tag, num+1)
        return fname
    
    def update_recent_temp_file(self):
        file_loc = r"C:\Users\physics-svc-mkdata\Documents\recent_temperature\TF_Temperature.dat"
        try:
            if self.fit_data["x:Frequency, Hz"][-1] > self.frequency_limit:
                np.savetxt(file_loc, np.array([self.fit_data["Time, s"][-1], self.fit_data["Temperature, K"][-1]]), delimiter='\t', header='Time, s\tTemperature, K')
        except:
            pass
        
    def save_fits(self):
        if np.asarray(self.fits).ndim > 1:
            fname = self.getfilename(self.save_folder+"/fits_{}".format(self.today), "{}_fits_{}".format(self.TF_name, self.today))
            if self.header is not None:
                np.savetxt(fname, np.asarray(self.fits), header=self.header, delimiter='\t')
            else:
                np.savetxt(fname, np.asarray(self.fits), delimiter='\t')
            if self.saved_fits.ndim == 2:
                self.saved_fits = np.concatenate((self.saved_fits, np.asarray(self.fits)), axis=0)
            elif self.saved_fits.ndim < 2:
                self.saved_fits = np.array(self.fits)
                
            self.reset_fits()
            self.reset_save_time()
    
    def save_fit_data(self):
        if len(self.fit_data["Time, s"]) > 0:
            fname = self.getfilename(self.save_folder+"/fits_{}".format(self.today), "{}_fits_{}".format(self.TF_name, self.today))
            pd.DataFrame(self.fit_data).to_csv(fname, sep='\t', index=False)
            for key in self.saved_fit_data:
                self.saved_fit_data[key] = self.saved_fit_data[key] + self.fit_data[key] 
            self.reset_fit_data()
        self.reset_save_time()
            
    def save_sweep(self):
        fname = self.getfilename(self.save_folder+"/sweeps_{}".format(self.today), "{}_{}".format(self.TF_name, self.today))
        if self.sweep_header is not None:
            np.savetxt(fname, np.array(self.sweep), header=self.sweep_header, delimiter='\t')
        else:
            np.savetxt(fname, np.array(self.sweep), delimiter='\t')

from tuning_fork.Amplitude_Tracking import temperature
            
class TF_Amp_Data:
    def __init__(self, TF_name, save_folder):
        self.current_working_dir = os.getcwd()
        self.TF_name = TF_name
        self.save_folder = save_folder
        self.get_today()
        self.last_sweep_time = time.time() - 60*60
        self.set_drive(1)
        self.set_current_amp(1)
        self.reset_data()
        self.reset_saved_data()
        self.reset_save_time()
        
    def reset_data(self):
        self.data = {
            "Time, s": [],
            "Frequency, hz": [],
            "Amplitude, nA": [],
            "Temperature, K": [],
            "Drive, V": [],
            "Current Amplifier": []
            }
        
    def reset_saved_data(self):
        self.saved_data = {
            "Time, s": [],
            "Frequency, hz": [],
            "Amplitude, nA": [],
            "Temperature, K": [],
            "Drive, V": [],
            "Current Amplifier": []
            }
        
    def reset_sweep_time(self):
        self.last_sweep_time = time.time()
        
    def reset_save_time(self):
        self.last_save = time.time()
    
    def get_today(self):
        now = datetime.now()
        self.today = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = time.mktime(self.today.timetuple())
        self.today = self.today.strftime("%Y-%m-%d")
        
    def getfilename(self, directory, file_tag, num=0):
        fname = self.current_working_dir+r"/data/{}/{}__{}.dat".format(directory, file_tag, num)
        if os.path.isdir(self.current_working_dir+"/data/"+directory) == False:
            os.makedirs(self.current_working_dir+"/data/"+directory)
        if os.path.isfile(fname):
            return self.getfilename(directory, file_tag, num+1)
        return fname
        
    def set_drive(self, value):
        self.drive = value
        
    def set_current_amp(self, value):
        self.current_amp = value
        
    def append_data(self, time, amplitude, frequency):
        self.data["Time, s"].append(time)
        self.data["Amplitude, nA"].append(amplitude*1E9/self.current_amp)
        self.data["Frequency, hz"].append(frequency)
        self.data["Temperature, K"].append(temperature(amplitude*1E9/self.current_amp, self.drive))
        self.data["Drive, V"].append(self.drive)
        self.data["Current Amplifier"].append(self.current_amp)
    
    def daily_save(self):
        self.save_data()
        self.reset_saved_data()
        self.reset_save_time()
        self.get_today()
        
    def save_data(self):
        if len(self.data["Time, s"]) > 0:
            fname = self.getfilename(self.save_folder+"/Amplitude_Tracking_{}".format(self.today), "{}_AT_{}".format(self.TF_name, self.today))
            pd.DataFrame(self.data).to_csv(fname, sep='\t', index=False)
            for key in self.saved_data:
                self.saved_data[key] = self.saved_data[key] + self.data[key] 
            self.reset_data()
        self.reset_save_time()
            