# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 15:00:31 2021

@author: physics-svc-mkdata
"""
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from instruments import diode_temp
from datetime import datetime
from calibration import mct
from scipy.stats import linregress

from tuning_fork import TF_visc

# from tuning_fork import TF_eqns as TF
# from tuning_fork import AW_uK_Analysis_Functions as AW
from tuning_fork import Lorentz_Fitting as LF

class ac_susceptometer_tracker:
    def __init__(self, lockin_1, lockin_2, lakeshore=None):
        self.data = []
        self.lockin_1 = lockin_1
        self.lockin_2 = lockin_2
        try:
            self.L1_Amp = lockin_1.Get_Osc_Amplitude()
            self.L2_Amp = lockin_2.Get_Osc_Amplitude()
            self.save_drive = True
        except:
            self.save_drive = False
        print(self.lockin_1.ID, " initialized.\n")
        print(self.lockin_2.ID, " initialized.\n")
        if lakeshore != None:
            self.lakeshore = lakeshore
            print(self.lakeshore.ID, " initialized.\n")
        else:
            self.lakeshore = None
        self.get_date()
        self.save_num = 0
        
    def get_date(self):
        now = datetime.now()
        self.date = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = time.mktime(self.date.timetuple())
    
    def take_data(self):
        Vx1, Vy1 = self.lockin_1.Read_XY()
        Vx2, Vy2 = self.lockin_2.Read_XY()
        if self.lakeshore == None:
            self.data.append([time.time(), Vx1, Vy1, Vx2, Vy2])
        else:
            T = self.lakeshore.Read_R(channel=8)
            self.data.append([time.time(), Vx1, Vy1, Vx2, Vy2, T])

    def take_T_data(self, channel=8):
        self.temp.append(self.lakeshore.Read_R(channel=channel))

    def getfilename(self, directory, file_tag):
        if os.path.isfile(directory+file_tag + '_{:s}_{:d}.dat'.format(self.date.strftime("%Y-%m-%d"), self.save_num)):
            self.save_num += 1
            return self.getfilename(directory, file_tag)
        return file_tag + '_{:s}_{:d}.dat'.format(self.date.strftime("%Y-%m-%d"), self.save_num)

    def save_data(self, directory=r'data\acs_data', file_tag=r'\acs', header="Time, s\tL1: Vx, V\tL1: Vy, V\tL2: Vx, V\tL2: Vy, V"):
        if not os.path.exists(directory):
            os.makedirs(directory)
        # file_name = filetag_YearMonthDay_#.dat
        file_name = self.getfilename(directory, file_tag)
        if self.lakeshore == None:
            if self.save_drive == True:
                np.savetxt(directory+file_name, np.concatenate((self.data, np.full((len(self.data),1), self.L1_Amp), np.full((len(self.data),1), self.L2_Amp)), axis=1), 
                           header=header + "\tL1 Drive, V\tL2 Drive, V",
                           delimiter="\t")
            else:
                np.savetxt(directory+file_name, self.data, header=header,
                       delimiter="\t")
        else:
            np.savetxt(directory+file_name, self.data, header=header+"\tT (K)",
                       delimiter="\t")

    def save_fig(self, directory=r'archive_data\data\figures', num=0):
        if not os.path.exists(directory):
            os.makedirs(directory)
        fname = directory + "\\{}_acs_{}.png".format(self.date.strftime("%Y-%m-%d"), num)
        if os.path.isfile(fname) == False:
            self.fig.savefig(fname)
        else:
            return self.save_fig(directory, num+1)

    def initialize_graphs(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(2, 2, sharex=True)
        self.fig.set_size_inches(8, 6)
        # self.fig.set_title("Lockin 1 & 2")
        
    def update_graphs(self):
        for row in self.ax:
            for sub_plot in row:
                sub_plot.clear()
        self.ax[0][0].set_title("Lockin Amp 1, GPIB 30")
        self.ax[0][1].set_title("L2, GPIB 2: " + self.date.strftime("%m-%d"))
        self.ax[0][0].set_ylabel("Vx, V")
        self.ax[1][0].set_ylabel("Vy, V")
        self.ax[1][0].set_xlabel("Time, hrs")
        self.ax[1][1].set_xlabel("Time, hrs")
        
        self.ax[0][0].plot(
            (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
            np.asarray(self.data)[:,1], color='cornflowerblue')
        self.ax[1][0].plot(
            (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
            np.asarray(self.data)[:,2], color='cornflowerblue')
        self.ax[0][1].plot(
            (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
            np.asarray(self.data)[:,3], color='coral')
        self.ax[1][1].plot(
            (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
            np.asarray(self.data)[:,4], color='coral')
        
######################################## LAKESHORE ########################################
from scipy import interpolate
class lakeshore_tracker:
    
    channel_dict= {
        "channel 1": "R8",
        "channel 2": "R7",
        "channel 3": "R2",
        "channel 4": "R3",
        "channel 5": "R5",
        "channel 6": "R6",
        "channel 7": "R11",
        "channel 8": "R12",
        "channel 9": "ROX"
        }
    
    def __init__(self, lakeshore, channel_list):
        self.lakeshore = lakeshore
        print(self.lakeshore.ID, " initialized.\n")
        self.channel_list = channel_list
        self.last_save = time.time()
        self.save_folder = "R8_2022"
        self.file_tag = "R8"
        self.load_calibration()
        self.saved_data = np.array([])
        self.data = []
        self.get_today()
        self.save_num = 0
        
    def load_calibration(self):
        calibration_directory = r"C:\Users\physics-svc-mkdata\Documents\GitHub\TF-Monitor-Interface\calibration"
        file_name = "\\08-20-08-26_rvt_calibration_main.dat"
        R8_file_name = "\\R8_RT_Curve.dat"
        calibration = np.loadtxt(calibration_directory+file_name, delimiter="\t", skiprows=1)
        R8_calibration = np.loadtxt(calibration_directory+R8_file_name, delimiter="\t", skiprows=1)
        R8_calibration = R8_calibration[R8_calibration[:,0].argsort(), :]
        self.R8_tck = interpolate.splrep(R8_calibration[:, 0], R8_calibration[:, 1])
        self.r_tck_list = []
        for i in range(calibration.shape[1]-2):
            argsort_R = calibration[:, i+2].argsort()
            self.r_tck_list.append(interpolate.splrep(calibration[argsort_R, i+2], calibration[argsort_R, 0]))
    
    def get_today(self):
        now = datetime.now()
        self.today = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = time.mktime(self.today.timetuple())
        self.today = self.today.strftime("%Y-%m-%d")       
    
    def update_temperature_file(self):
        current_temp, bound = self.get_current_temp(self.data[-1][1], 1)
        np.savetxt(r"C:\Users\physics-svc-mkdata\Documents\recent_temperature\R8_temp.dat", np.array([self.data[-1][0], current_temp]), header = "Time, s\tTemperature, K")
    
    # def get_current_temp(self, resistance, channel):
    #     if channel==1:
    #         temp = np.interp(resistance, (self.R8_calibration[:, 0])[self.R8_sorted], (self.R8_calibration[:, 1])[self.R8_sorted])
    #         if resistance < self.R8_calibration[0, 0]:
    #             boundary = 2
    #             temp = self.R8_calibration[0, 1]
    #         elif resistance > self.R8_calibration[-1, 0]:
    #             boundary = 1
    #             temp = self.R8_calibration[-1, 1]
    #         else:
    #             boundary = 0
    #         return temp,  boundary
    #     else:
    #         r_sorted = self.r_sorted_list[channel-1]
    #         temp = np.interp(resistance, (self.calibration[:, channel+1])[r_sorted], (self.calibration[:, 0])[r_sorted])
    #         if resistance < ((self.calibration[:, channel+1])[r_sorted])[0]:
    #             boundary = 2
    #             temp = ((self.calibration[:, 0])[r_sorted])[0]
    #         elif resistance > ((self.calibration[:, channel+1])[r_sorted])[-1]:
    #             boundary = 1
    #             temp = ((self.calibration[:, 0])[r_sorted])[-1]
    #         else:
    #             boundary = 0
    #         return temp, boundary
    
    def get_current_temp(self, resistance, channel):
        if channel==1:
            temp = interpolate.splev(-1*resistance,self.R8_tck)  
        else:
            temp = interpolate.splev(-1*resistance, self.r_tck_list[channel-1])
        boundary = 0   
        return temp, boundary
            
    def take_data(self, wait_time=5):
        R_values = [time.time()]
        reading = self.lakeshore.Autoscan(channels=self.channel_list, wait_time=wait_time)
        for idx, item in enumerate(reading):
            R_values.append(reading[idx][1])
        self.data.append(R_values)
        self.update_temperature_file()
        
    def getfilename(self, num=0):
        save_directory = "data/{}".format(self.save_folder)
        fname = "/{}_{}__{}.dat".format(self.file_tag, self.today, num)
        if not os.path.isdir(save_directory):
            os.makedirs(save_directory)
        if os.path.isfile(save_directory+fname):
            return self.getfilename(num+1)
        return save_directory+fname

    def save_data(self):
        if np.array(self.data).ndim > 1:
            header = "Time, s"
            for name in self.channel_list:
                header = header + "\tChannel {}: {}, Ohms".format(name, self.channel_dict['channel {}'.format(name)])
            # file_name = filetag_YearMonthDay_#.dat
            file_name = self.getfilename()
            np.savetxt(file_name, self.data, header=header,
                       delimiter="\t")
            try: 
                self.saved_data = np.concatenate((self.saved_data, self.data))
            except:
                self.saved_data = np.array(self.data)
            self.data = []
            self.last_save = time.time()
            

    # def save_fig(self, directory=r'archive_data\data\figures', num=0):
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)
    #     fname = directory + "\\{}_rt_{}.png".format(self.date.strftime("%Y-%m-%d"), num)
    #     if os.path.isfile(fname) == False:
    #         self.fig.savefig(fname)
    #     else:
    #         return self.save_fig(directory, num+1)

    def initialize_graphs(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(len(self.channel_list), 1, sharex=True)
        self.fig.set_size_inches(8, 6)
        
    color_list = []
    
    def update_graphs(self):
        if len(self.channel_list) == 1:
            self.ax.clear()
            self.ax.plot(
                (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
                np.asarray(self.data)[:,1],
                color='chocolate'
                )
            self.ax.set_ylabel("R, $\Omega$")
            self.ax.set_xlabel("time, hrs")
            self.ax.set_title("Resistive Thermometers: " + self.date.strftime("%m-%d"))
        else:
            for idx, subplot in enumerate(self.ax):
                subplot.clear()
                channel = self.channel_list[idx]
                current_temp, boundary = self.get_current_temp(np.asarray(self.data)[-1, idx+1], channel=channel)
                if boundary == 0:
                    label='{:.4f} K'.format(current_temp)
                elif boundary == 1:
                    label='< {:.4f} K'.format(current_temp)
                elif boundary == 2:
                    label='> {:.4f} K'.format(current_temp)

                subplot.plot(
                    (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
                    np.asarray(self.data)[:,idx+1],
                    color="lightseagreen",
                    label=label
                    )
                subplot.set_ylabel("R, $\Omega$")
                subplot.legend(loc=2)
                
            self.ax[-1].set_xlabel("time, hrs")
            self.ax[0].set_title("Resistive Thermometers: " + self.date.strftime("%m-%d"))
  

######################################## DIODE ########################################

class diode_tracker:
    def __init__(self, multimeter):
        # TODO
        # Set up all the initial variables, arrays, and objects
        self.multimeter = multimeter
        print(self.multimeter.ID, " initialized.\n")
        self.save_folder='diode_2022' 
        self.file_tag='diode'
        self.last_save = time.time()
        self.saved_data = np.array([])
        self.data = []
        self.get_today()
        self.Diode_Fit_Vec = np.vectorize(diode_temp.Diode_Fit)
        
    def get_today(self):
        now = datetime.now()
        self.today = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = time.mktime(self.today.timetuple())
        self.today = self.today.strftime("%Y-%m-%d")
    
    def update_temperature_file(self):
        T = self.data[-1][2]
        time = self.data[-1][0]
        np.savetxt(fname=r"C:\Users\physics-svc-mkdata\Documents\recent_temperature\diode_temp.dat", X=[time, T], delimiter='\t', header="Time, s\tTemperature, K")
    
    def take_data(self):
        # TODO
        # Read data from multimeter
        try:
            V = self.multimeter.Read_V()
            try:
                T = self.Diode_Fit_Vec(np.abs(V))
            except:
                T = np.nan
        except:
            V = np.nan
            T = np.nan
        self.data.append([time.time(), V, T])
        try:
            self.update_temperature_file()
        except:
            pass
        
    def getfilename(self, num=0):
        save_directory = "data/{}".format(self.save_folder)
        fname = "/{}_{}__{}.dat".format(self.file_tag, self.today, num)
        if not os.path.isdir(save_directory):
            os.makedirs(save_directory)
        if os.path.isfile(save_directory+fname):
            return self.getfilename(num+1)
        return save_directory+fname
    
    def save_data(self):
        if np.array(self.data).ndim > 1:
            file_name = self.getfilename()
            np.savetxt(file_name, self.data, delimiter="\t",
                       header="Time, s\tVoltage, V\t, Temperature, K")
            try: 
                self.saved_data = np.concatenate((self.saved_data, self.data))
            except:
                self.saved_data = np.array(self.data)
            self.data = []
            self.last_save = time.time()

    def save_fig(self, directory='data/diode/figures', num=0):
        if not os.path.exists(directory):
            os.makedirs(directory)
        fname = directory + "/diode_{}__{}.png".format(self.date.strftime("%Y-%m-%d"), num)
        if os.path.isfile(fname):
            return self.save_fig(directory, num+1)
        else:
            self.fig.savefig(fname)

    def initialize_graphs(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(1, 1)
        self.fig.set_size_inches(8, 6)
        
    def update_graphs(self):
        # TODO
        # Change this to display T vs time
        self.ax.clear()
        self.ax.plot(
            (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
            np.asarray(self.data)[:,2],
            color='orchid',
            label='Current Temp: {:.2f} K'.format(np.asarray(self.data)[-1,2])
            #label='Current Temp'.format(np.asarray(self.data)[-1,2])
            )
        self.ax.set_ylabel("T, K")
        self.ax.set_xlabel("time, hrs")
        self.ax.set_title("Diode Thermometer: " + self.date.strftime("%m-%d"))
        self.ax.legend(loc=2)
        
        
######################################## MCT ########################################      
        
class mct_tracker:
    def __init__(self, DVM, Bridge, track_ratio, P, I, D):
        print(DVM.ID, " Initialized")
        print(Bridge.ID, " Initialized")
        self.DVM = DVM
        self.Bridge = Bridge
        self.track_ratio = track_ratio
        self.last_save = time.time()
        self.save_folder = "MCT_2022"
        self.file_tag = "MCT"
        self.data = []
        self.saved_data = np.array([])
        self.get_today()
        self.P = P
        self.I = I
        self.D = D
        
    def get_today(self):
        now = datetime.now()
        self.today = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = time.mktime(self.today.timetuple())
        self.today = self.today.strftime("%Y-%m-%d")
        
    def getfilename(self, num=0):
        save_directory = "data/{}".format(self.save_folder)
        fname = "/{}_{}__{}.dat".format(self.file_tag, self.today, num)
        if not os.path.isdir(save_directory):
            os.makedirs(save_directory)
        if os.path.isfile(save_directory+fname):
            return self.getfilename(num+1)
        return save_directory+fname

    def save_data(self):
        if np.array(self.data).ndim > 1:
            file_name = self.getfilename()
            np.savetxt(file_name, self.data, delimiter="\t",
                       header="Time, s\tRatio\tVoltage, V\t, Temperature, K")
            try: 
                self.saved_data = np.concatenate((self.saved_data, self.data))
            except:
                self.saved_data = np.array(self.data)
            self.data = []
            self.last_save = time.time()

    def update_temperature_file(self):
        np.savetxt(fname=r"C:\Users\physics-svc-mkdata\Documents\recent_temperature\mct_temp.dat", X=np.array(self.data[-1]), delimiter='\t', header="Time, s\tTemperature, K")
    
    def take_data(self):
        V = self.DVM.Read_V()
        Ratio = self.Bridge.Read_Ratio()
        T, p = mct.MCT_V2T(V, Ratio)
        self.data.append([time.time(), Ratio, V, T])
        if np.abs(V) > 0.005 and np.asarray(self.data).shape[0]>2 and self.track_ratio == True:
            # COMMENT OUT THE NEXT LINE IF PID CONTROL DOES NOT WORK
            # OR SET track_ratio = False in mct_monitor_app
          self.PID_bridge_balance(V, Ratio) #commented out by Lucia 09/28/2021. PID control did work, but I wanted a smoother curve.
        try:
            self.update_temperature_file()
        except:
            pass
        
    def PID_bridge_balance(self, V, Ratio):
        dt = (self.data[-1][0] - self.data[-2][0])
        
        points = int(self.I/dt)
        if np.asarray(self.data).shape[0] > points:
            integral = np.sum(np.asarray(self.data)[-points:, 2]) * dt
            derivative = linregress(np.asarray(self.data)[-points:, 0], np.asarray(self.data)[-points:, 2])[0]
        else:
            integral = np.sum(np.asarray(self.data)[:, 2]) * dt
            derivative = linregress(np.asarray(self.data)[:, 0], np.asarray(self.data)[:, 2])[0]
        
        new_ratio = Ratio - self.P * (V + (integral/self.I) + (self.D * derivative))
        self.Bridge.Set_Ratio(new_ratio)
        
    def initialize_graphs(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(3, 1, sharex=True)
        self.fig.set_size_inches(8, 6)
        plt.tight_layout()
        
    def update_graphs(self):
        # TODO
        # Change this to display T vs time
        colors = ['cornflowerblue', 'coral', 'firebrick']
        for idx, subplot in enumerate(self.ax):
            subplot.clear()
            subplot.plot(
                (np.asarray(self.data)[:,0] - self.timestamp_today)/3600, 
                 np.asarray(self.data)[:,idx+1],
                 color=colors[idx],
                 label='{:.5f}'.format(np.asarray(self.data)[-1,idx+1])
                 )
            subplot.set_ylabel(self.record_names[idx])
                
        self.ax[-1].set_xlabel("time, hrs")
        self.ax[0].set_title("MCT: " + self.date.strftime("%m-%d"))
        
        for subplot in self.ax:
            subplot.legend(loc=2)
        
        
        
        