# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 19:35:44 2022

@author: alexd

Tuning Fork Monitoring Application
"""


import tkinter as tk

from instruments import LOCKIN
from instruments import AGILENT_SIGNAL_GEN

# from instruments import TEST_LOCKIN
# from instruments import TEST_SIGNAL_GEN

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import configparser
import os

import time
from datetime import datetime
from datetime import timedelta

import numpy as np
from tuning_fork import Lorentz_Fitting as LF

def ticks_to_hours(graph, time_start, time_end):
    new_ticks = []
    xlabels = []
    time_start, time_end = time_start/3600, time_end/3600
    # time if time length of data is < 30 minutes, use 7 HH:MM:SS; otherwise 9 HH:MM
    if (time_end - time_start)*60 < 30:
        ticks = np.linspace(time_start, time_end, 7)
        for idx, val in enumerate(ticks):
            dt = str(timedelta(seconds=int(val*3600)))
            if dt not in xlabels:
                xlabels.append(dt)
                new_ticks.append(val*3600)
    else:
        ticks = np.linspace(time_start, time_end, 9)
        for idx, val in enumerate(ticks):
            dt = str(timedelta(seconds=int(val*3600))).split(":")
            try:
                time = float(dt[0]) + float(dt[1])/60
            except:
                time = val
            dt = dt[0]+":"+dt[1]
            if dt not in xlabels:
                xlabels.append(dt)
                new_ticks.append(time*3600)

    graph.set_xticks(new_ticks)
    graph.set_xticklabels(xlabels)

def close_win(top):
        top.destroy()
        
def isStrInt(text):
    try:
        int(text)
        return True
    except:
        return False
    
def isStrFloat(text):
    try:
        float(text)
        return True
    except:
        return False
    
class TFdata:
    def __init__(self, TF_name, save_directory):
        self.current_working_dir = os.getcwd()
        self.TF_name = TF_name
        self.save_directory = save_directory
        self.get_today()
        self.set_drive(1)
        self.set_current_amp(1)
        self.store_last_sweep([])
        x_header = "\tx:Frequency, Hz\tx:Amplitude, V\tx:Width, Hz\tx:Phase, Rad\tx:Background intercept, V\tx:Background slope, dV/df\tx:Background quadratic, d2V/d2f"
        y_header = "\ty:Frequency, Hz\ty:Amplitude, V\ty:Width, Hz\ty:Phase, Rad\ty:Background intercept, V\ty:Background slope, dV/df\ty:Background quadratic, d2V/d2f"
        self.header = "Time, s\tDrive, V\tCurrent Amp"+x_header+y_header
        self.sweep_header = "Time, s\tFrequency, hz\tVx, V\tVy, V\tDrive, V\tCurrent Amp"
        self.reset_sweep()
        self.reset_fits()
        self.reset_saved_fits()
        self.reset_save_time()

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
        if self.saved_fits.ndim > 1:
            self.saved_fits = np.concatenate((self.saved_fits, np.array(self.fits)))
        else:
            self.saved_fits = np.array(self.fits)
        self.reset_fits()
        
    def reset_fits(self):
        self.fits = []
    
    def reset_saved_fits(self):
        self.saved_fits = np.array([])
        
    def daily_save(self):
        self.save_fits()
        self.reset_save_time()
        self.reset_fits()
        self.reset_saved_fits()
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
            self.append_fits([self.sweep[:, 0].mean(), self.drive, self.current_amp, *self.xfit, *self.yfit])
        return xflag
        
        
    def getfilename(self, directory, file_tag, num=0):
        fname = self.current_working_dir+r"/data/{}/{}__{}.dat".format(directory, file_tag, num)
        if os.path.isdir(self.current_working_dir+"/data/"+directory) == False:
            os.makedirs(self.current_working_dir+"/data/"+directory)
        if os.path.isfile(fname):
            return self.getfilename(directory, file_tag, num+1)
        return fname
        
    def save_fits(self):
        if np.array(self.fits).ndim > 1:
            fname = self.getfilename(self.save_directory+"/fits_{}".format(self.today), "{}_fits_{}".format(self.TF_name, self.today))
            if self.header is not None:
                np.savetxt(fname, np.array(self.fits), header=self.header, delimiter='\t')
            else:
                np.savetxt(fname, np.array(self.fits), delimiter='\t')
            
    def save_sweep(self):
        fname = self.getfilename(self.save_directory+"/sweeps_{}".format(self.today), "{}_{}".format(self.TF_name, self.today))
        if self.sweep_header is not None:
            np.savetxt(fname, np.array(self.sweep), header=self.sweep_header, delimiter='\t')
        else:
            np.savetxt(fname, np.array(self.sweep), delimiter='\t')
            

class tkApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.state("zoomed")
        
        self.init_window_size()
        
        self.config = configparser.RawConfigParser()
        
        if not os.path.exists('TFMI_Config.cfg'):
            self.initConfig()
            
        # Read configurations using section and key to get the value
        self.config.read('TFMI_Config.cfg')
        
        self.save_interval = 60 # in minutes
        self.tracking_range = float(self.config["Tracking Settings"]["Range"])
        
        if self.config["Instrument Settings"]["Lock-in Model"] == "LI 5640":
            self.lockin = LOCKIN.LI5640("GPIB0::"+self.config["Instrument Settings"]["Lock-in GPIB"]+"::INSTR")
        elif self.config["Instrument Settings"]["Lock-in Model"] == "SR 830":
            self.lockin = LOCKIN.SR830("GPIB0::"+self.config["Instrument Settings"]["Lock-in GPIB"]+"::INSTR")
        else:
            print("Invalid Lock-in Instrument Type: Reset Config File")
        if self.config["Instrument Settings"]["Signal-Gen Model"] == "Agilent":
            self.gen = AGILENT_SIGNAL_GEN.AGILENT_SIGNAL_GEN("GPIB0::"+self.config["Instrument Settings"]["Signal-Gen GPIB"]+"::INSTR")
        elif self.config["Instrument Settings"]["Signal-Gen Model"] == "Keysight":
            self.gen = AGILENT_SIGNAL_GEN.AGILENT_SIGNAL_GEN("GPIB0::"+self.config["Instrument Settings"]["Signal-Gen GPIB"]+"::INSTR")
        else:
            print("Invalid Signal-Gen Instrument Type: Reset Config File")
        
        self.TFdata = TFdata(TF_name=self.config["Monitor Save Settings"]["Tuning Fork Name"], 
                             save_directory=self.config["Monitor Save Settings"]["Save Folder"])
        self.TFdata.set_drive(float(self.config["Frequency Sweep Settings"]["Drive"]))
        try:
            self.gen.Set_Voltage(float(self.config["Frequency Sweep Settings"]["Drive"]))
        except:
            print("Drive Not Set Properly")
            
        try:
            self.lockin.Set_Phase(float(self.config["Frequency Sweep Settings"]["Phase, deg"]))
        except:
            print("Phase Not Set Properly")
            
            
        self.TFdata.set_current_amp(float(self.config["Frequency Sweep Settings"]["Current Amp"]))
        
        self.params = { "Start Frequency": float(self.config["Frequency Sweep Settings"]["Start Frequency"]),
                        "End Frequency": float(self.config["Frequency Sweep Settings"]["End Frequency"]),
                        "Phase, deg": float(self.config["Frequency Sweep Settings"]["Phase, deg"]),
                        "Num Pts": int(self.config["Frequency Sweep Settings"]["Num Pts"]),
                        "Wait Time, ms": int(float(self.config["Frequency Sweep Settings"]["Wait Time, ms"])),
                        "Drive, V": float(self.config["Frequency Sweep Settings"]["Drive"])
                      }
        
        # Interface frames
        self.wm_title("Freq Sweep Alpha")
        
        graph_size = 0.8
        padding = (1-graph_size)/2*(self.win_zoom_inches["width"]/2)
        
        self.graph_1 = tk.Frame(self)
        self.graph_1.place(x="{}i".format(padding),y="0i")
        self.graph_2 = tk.Frame(self)
        self.graph_2.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding),y="0i")
        
        self.fig = Figure(figsize=(graph_size*self.win_zoom_inches["width"]/2, self.win_zoom_inches["width"]/2*4.8/6.4), dpi=96)
        self.ax = self.fig.add_subplot(2,1,1)
        self.ay = self.fig.add_subplot(2,1,2)
        
        self.fig2 = Figure(figsize=(graph_size*self.win_zoom_inches["width"]/2, self.win_zoom_inches["width"]/2*4.8/6.4), dpi=96)
        self.ax2 = self.fig2.add_subplot(2,1,1)
        self.ay2 = self.fig2.add_subplot(2,1,2)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(in_=self.graph_1)

        self.toolbar1 = NavigationToolbar2Tk(self.canvas, self.graph_1)
        self.toolbar1.update()
        self.canvas.get_tk_widget().pack(in_=self.graph_1)
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)  # A tk.DrawingArea.
        self.canvas2.get_tk_widget().pack(in_=self.graph_2)
        
        self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.graph_2)
        self.toolbar2.update()
        self.canvas2.get_tk_widget().pack(in_=self.graph_2)
        self.canvas2.mpl_connect("key_press_event", self.on_key_press)

        
        self.param_entry_frame = tk.Frame(self)
        self.param_entry_frame.place(x="1i", y="8.25i")
        self.param_label_frame = tk.Frame(self)
        self.param_label_frame.place(x="2i", y="8.25i")
        
        self.param_entry_frame_2 = tk.Frame(self)
        self.param_entry_frame_2.place(x="4i", y="8.25i")
        self.param_label_frame_2 = tk.Frame(self)
        self.param_label_frame_2.place(x="5i", y="8.25i")
        
        self.checkbox_frame = tk.Frame(self)
        self.checkbox_frame.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding), y="{}i".format(0.5+self.win_zoom_inches["width"]/2*4.8/6.4))
        
        self.option_frame = tk.Frame(self)
        self.option_frame.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding), y="{}i".format(1.0+self.win_zoom_inches["width"]/2*4.8/6.4))
        
        self.tracking_button = tk.Button(self.checkbox_frame, text="Update Tracking Range", padx=10, command=self.update_tracking_range)
        self.tracking_button.pack(in_=self.checkbox_frame, side=tk.RIGHT, padx=10)
        self.tracking_label = tk.Label(self.checkbox_frame, text="Tracking Range: {:.2f}".format(self.tracking_range))
        self.tracking_label.pack(in_=self.checkbox_frame, side=tk.RIGHT, padx=10)
        self.tracking_entry = tk.Entry(self.checkbox_frame, width=5)
        self.tracking_entry.pack(in_=self.checkbox_frame, side=tk.RIGHT, padx=10)
        
        self.settings_frame = tk.Frame(self)
        self.settings_frame.place(x="{}i".format(self.win_zoom_inches["width"]-1),  y="{}i".format(self.win_zoom_inches["height"]-9/16))
        
        # labels & Text Boxes
        self.label_list = []
        self.entry_list = []
        for idx, (key, val) in enumerate(self.params.items()):
            if idx<3:
                self.label_list.append(tk.Label(self.param_label_frame, text = key+": {:.3f}".format(val)))
                self.label_list[-1].pack(in_=self.param_label_frame, pady=5)
                
                self.entry_list.append(tk.Entry(self.param_entry_frame, width=8))
                self.entry_list[-1].pack(in_=self.param_entry_frame, pady=5)
            else:
                self.label_list.append(tk.Label(self.param_label_frame_2, text = key+": {:.3f}".format(val)))
                self.label_list[-1].pack(in_=self.param_label_frame_2, pady=5)
                
                self.entry_list.append(tk.Entry(self.param_entry_frame_2, width=8))
                self.entry_list[-1].pack(in_=self.param_entry_frame_2, pady=5)

        
        self.update_button = tk.Button(master=self, text="Update Params", command=self.update_sweep_params)
        self.update_button.pack(in_=self.param_entry_frame, pady=5)
        
        self.fitBool = tk.IntVar()
        self.fitBool.set(int(self.config["Monitor Checkbox Settings"]["Fitting"]))
        self.fit_check = tk.Checkbutton(master=self, text="Fit", variable=self.fitBool, onvalue=1, offvalue=0, command=self.update_checkbox_config)
        self.fit_check.pack(in_=self.checkbox_frame, side=tk.LEFT, padx=5, pady=5)
        
        self.correctPhaseBool = tk.IntVar()
        self.correctPhaseBool.set(0)
        self.correctPhase_check = tk.Checkbutton(master=self, text="Correct Phase", variable=self.correctPhaseBool, onvalue=1, offvalue=0)
        self.correctPhase_check.pack(in_=self.checkbox_frame, side=tk.LEFT, padx=5, pady=5)
        
        self.trackBool = tk.IntVar()
        self.trackBool.set(int(self.config["Monitor Checkbox Settings"]["Tracking"]))
        self.track_check = tk.Checkbutton(master=self, text="Track", variable=self.trackBool, onvalue=1, offvalue=0, command=self.update_checkbox_config)
        self.track_check.pack(in_=self.checkbox_frame, side=tk.LEFT, padx=5, pady=5)
        
        self.showGraph = tk.StringVar(self)
        self.showGraph.set("Frequency Sweep") # default value
        self.showGraph_Options = tk.OptionMenu(self, self.showGraph, "Frequency Sweep", "Fit Details", command=self.switchGraph)
        self.showGraph_Options.pack(in_=self.option_frame)
        
        self.settings_button = tk.Button(master=self, text="Settings", command=self.settingsWindow)
        self.settings_button.pack(in_=self.settings_frame, side=tk.RIGHT, padx=5, pady=5)
        
        self.start_button = tk.Button(master=self, text="Start", bg='green', fg='white', height=2, width=9, command=self.start)
        self.start_button.place(x="{}i".format(10-0.4), y="8.5i")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.update_idletasks()
        self.update()
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.run = False
            self.TFdata.save_fits()
            self.quit()
            self.destroy()

    def initConfig(self):
        self.config.add_section('Frequency Sweep Settings')
        self.config.set('Frequency Sweep Settings', 'Start Frequency', '32700')
        self.config.set('Frequency Sweep Settings', 'End Frequency', '32900')
        self.config.set('Frequency Sweep Settings', 'Phase, deg', '0')
        self.config.set('Frequency Sweep Settings', 'Num Pts', '100')
        self.config.set('Frequency Sweep Settings', 'Wait Time, ms', '1')
        self.config.set('Frequency Sweep Settings', 'Drive', '1')
        self.config.set('Frequency Sweep Settings', 'Current Amp', '10000')
        self.config.set('Frequency Sweep Settings', 'Save Directory', r"C:\Users\physics-svc-mkdata\Documents\Data\TuningForkThermometer")
        
        self.config.add_section("Instrument Settings")
        self.config.set("Instrument Settings", "Lock-in Model", "LI 5640")
        # self.config.set("Instrument Settings", "Lock-in Model", "Test")
        self.config.set("Instrument Settings", "Lock-in GPIB", "25")
        self.config.set("Instrument Settings", "Signal-Gen Model", "Keysight")
        # self.config.set("Instrument Settings", "Signal-Gen Model", "Test")
        self.config.set("Instrument Settings", "Signal-Gen GPIB", "24")
        
        self.config.add_section("Monitor Save Settings")
        self.config.set("Monitor Save Settings", "Save Folder", "Testing")
        self.config.set("Monitor Save Settings", "Tuning Fork Name", "TestTF")
        
        self.config.add_section("Monitor Checkbox Settings")
        self.config.set("Monitor Checkbox Settings", "Fitting", "1")
        self.config.set("Monitor Checkbox Settings", "Tracking", "0")
        
        self.config.add_section("Tracking Settings")
        self.config.set("Tracking Settings", "Range", "6")
        
        with open('TFMI_Config.cfg', 'w') as output:
            self.config.write(output)
    
    def updateConfig(self, section, key, value):
    #Update config using section key and the value to change
    #call this when you want to update a value in configuation file
    # with some changes you can save many values in many sections
        self.config.set(section, key, value)
        with open('TFMI_Config.cfg', 'w') as output:
            self.config.write(output)
            
    def update_checkbox_config(self):
        self.updateConfig("Monitor Checkbox Settings", "Fitting", self.fitBool.get())
        self.updateConfig("Monitor Checkbox Settings", "Tracking", self.trackBool.get())
            
    def init_window_size(self):
        self.update_idletasks()
        self.screen_ratio = {"width": 16, "height": 9}
        self.screen_size = {"x":self.winfo_screenwidth(), "y":self.winfo_screenheight()}
        self.screen_size_inches = {"width": 20, "height": 11.25}
        
        self.monitor_dpi = self.screen_size["x"]/self.screen_size_inches["width"]
        self.win_zoom_size = {"x":self.winfo_width(), "y":self.winfo_height()}
        self.win_zoom_inches = {"width": self.win_zoom_size["x"]/self.monitor_dpi, 
                                "height": self.win_zoom_size["y"]/self.monitor_dpi}
    
    def settingsWindow(self):
        sWin = tk.Toplevel(self)
        
        sWin.geometry("480x360")
        sWin.title("Settings")
        
        # GPIB Settings
        GPIB_Label = tk.Label(sWin, text="GPIB")
        GPIB_Label.place(x=100, y=15)
        
        Lockin_Label = tk.Label(sWin, text="Lock In")
        Lockin_Label.place(x=15, y=35)
        
        SignalGen_Label = tk.Label(sWin, text="Signal Gen")
        SignalGen_Label.place(x=15, y=75)
        
        self.Lockin_GPIB = tk.Entry(sWin, width=5)
        self.Lockin_GPIB.insert(0, self.config["Instrument Settings"]["Lock-in GPIB"])
        self.Lockin_GPIB.place(anchor="nw", x=100, y=35)
        
        self.SignalGen_GPIB = tk.Entry(sWin, width=5)
        self.SignalGen_GPIB.insert(0, self.config["Instrument Settings"]["Signal-Gen GPIB"])
        self.SignalGen_GPIB.place(anchor="nw", x=100, y=75)
        
        self.Lockin_Model = tk.StringVar(sWin)
        self.Lockin_Model.set(self.config["Instrument Settings"]["Lock-in Model"]) # default value
        self.L_Model_Options = tk.OptionMenu(sWin, self.Lockin_Model, "LI 5640", "SR 830")
        self.L_Model_Options.place(anchor="nw", x=160, y=28)
        
        self.SignalGen_Model = tk.StringVar(sWin)
        self.SignalGen_Model.set(self.config["Instrument Settings"]["Signal-Gen Model"]) # default value
        self.SG_Model_Options = tk.OptionMenu(sWin, self.SignalGen_Model, "Keysight", "Agilent")
        self.SG_Model_Options.place(anchor="nw", x=160, y=68)

        # Save Folder
        self.Save_Folder = tk.Entry(sWin, width=12)
        self.Save_Folder.insert(0, self.config["Monitor Save Settings"]["Save Folder"])
        self.Save_Folder.place(anchor="nw", x=100, y=120)
        
        Folder_Label = tk.Label(sWin, text="Save Folder")
        Folder_Label.place(x=15, y=120)
        
        # TF Name
        self.TF_savename = tk.Entry(sWin, width=12)
        self.TF_savename.insert(0, self.config["Monitor Save Settings"]["Tuning Fork Name"])
        self.TF_savename.place(anchor="nw", x=100, y=150)
        
        Name_Label = tk.Label(sWin, text="TF Name")
        Name_Label.place(x=15, y=150)
        
        next_fit_name = self.TFdata.getfilename(self.TFdata.save_directory, "{}_fits_{}".format(self.TFdata.TF_name, self.TFdata.today)).replace(self.TFdata.current_working_dir,'')
        
        self.fit_Label = tk.Label(sWin, text="Next Fit File:        "+next_fit_name)
        self.fit_Label.place(x=15, y=200)
        
        self.sweep_label = tk.Label(sWin, text="Current Sweep Folder: "+"\data\{}\sweeps_{}".format(self.config["Monitor Save Settings"]["Save Folder"], self.TFdata.today))
        self.sweep_label.place(x=15, y=230)
        
        ###### TODO #######
        # TODO
        # More Settings
        
        # Save Folder
        self.current_amp_entry = tk.Entry(sWin, width=12)
        self.current_amp_entry.insert(0, float(self.config["Frequency Sweep Settings"]["Current Amp"]))
        self.current_amp_entry.place(anchor="nw", x=370, y=120)
        
        Current_Amp_Label = tk.Label(sWin, text="Current Amp")
        Current_Amp_Label.place(x=250, y=120)
        
        # TF Name
        self.drive_entry = tk.Entry(sWin, width=12)
        self.drive_entry.insert(0, float(self.config["Frequency Sweep Settings"]["Drive"]))
        self.drive_entry.place(anchor="nw", x=370, y=150)
        
        Drive_Label = tk.Label(sWin, text="Drive, V")
        Drive_Label.place(x=250, y=150)
        
        next_fit_name = self.TFdata.getfilename(self.TFdata.save_directory, "{}_fits_{}".format(self.TFdata.TF_name, self.TFdata.today)).replace(self.TFdata.current_working_dir,'')
        
        ###### END OF TODO ######

        save_button = tk.Button(sWin, text='Save', command=self.save_settings)
        save_button.place(anchor="sw", x=15, y=345)
        close_button = tk.Button(sWin, text='Quit', command=lambda:close_win(sWin))
        close_button.place(anchor="se", x=465, y=345)

        self.wait_window(self)
        
    def save_settings(self):
        
        if isStrInt(self.Lockin_GPIB.get()):
            self.updateConfig("Instrument Settings", "Lock-in GPIB", self.Lockin_GPIB.get())
        if isStrInt(self.SignalGen_GPIB.get()):
            self.updateConfig("Instrument Settings", "Signal-Gen GPIB", self.SignalGen_GPIB.get())
        
        self.updateConfig("Instrument Settings", "Lock-in Model", self.Lockin_Model.get())
        self.updateConfig("Instrument Settings", "Signal-Gen Model", self.SignalGen_Model.get())
        
        if self.config["Instrument Settings"]["Lock-in Model"] == "LI 5640":
            self.lockin = LOCKIN.LI5640("GPIB0::"+self.config["Instrument Settings"]["Lock-in GPIB"]+"::INSTR")
        elif self.config["Instrument Settings"]["Lock-in Model"] == "SR 830":
            self.lockin = LOCKIN.SR830("GPIB0::"+self.config["Instrument Settings"]["Lock-in GPIB"]+"::INSTR")
        else:
            print("Invalid Lock-in Instrument Type: Reset Config File")
        if self.config["Instrument Settings"]["Signal-Gen Model"] == "Keysight" or self.config["Instrument Settings"]["Signal-Gen Model"] == "Agilent":
            self.gen = AGILENT_SIGNAL_GEN.AGILENT_SIGNAL_GEN("GPIB0::"+self.config["Instrument Settings"]["Signal-Gen GPIB"]+"::INSTR")
        else:
            print("Invalid Signal-Gen Instrument Type: Reset Config File")
        
        if self.Save_Folder != self.config["Monitor Save Settings"]["Save Folder"]:
            self.updateConfig("Monitor Save Settings", "Save Folder", self.Save_Folder.get())
            self.TFdata.save_directory = self.Save_Folder.get()
            next_fit_name = self.TFdata.getfilename(self.TFdata.save_directory, "{}_fits_{}".format(self.TFdata.TF_name, self.TFdata.today)).replace(self.TFdata.current_working_dir,'')
            self.fit_Label.config(text="Next Fit File:        "+next_fit_name)
        
        if self.TF_savename != self.config["Monitor Save Settings"]["Tuning Fork Name"]:
            self.updateConfig("Monitor Save Settings", "Tuning Fork Name", self.TF_savename.get())
            self.TFdata.TF_name = self.TF_savename.get()
            self.sweep_label.config(text="Current Sweep Folder: "+"\data\{}\sweeps_{}".format(self.TFdata.save_directory, self.TFdata.today))
            
        if isStrFloat(self.current_amp_entry.get()):
            self.updateConfig("Frequency Sweep Settings", "Current Amp", self.current_amp_entry.get())
            self.TFdata.set_current_amp(float(self.current_amp_entry.get())) 
        if isStrFloat(self.drive_entry.get()):
            self.updateConfig("Frequency Sweep Settings", "Drive", self.drive_entry.get())
            self.TFdata.set_drive(float(self.drive_entry.get()))
            try:
                self.gen.Set_Voltage(float(self.config["Frequency Sweep Settings"]["Drive"]))
            except:
                print("Drive Not Set")


    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)
        
    def update_sweep_params(self):
        for idx, (key, val) in enumerate(self.params.items()):
            try:
                if self.entry_list[idx].get() != '':
                    self.params[key] = int(self.entry_list[idx].get())
                    self.updateConfig('Frequency Sweep Settings', key, self.entry_list[idx].get())
                    self.label_list[idx].config(text=key+": {}".format(float(self.entry_list[idx].get())))
                    self.entry_list[idx].delete(0, 'end')
                    if key == "Drive, V":
                        self.gen.Set_Voltage(float(self.entry_list[idx].get()))
                    if key == "Phase, deg":
                        self.lockin.Set_Phase(val)
                    
            except Exception as e:
                print(e)
        
    def update_tracking_range(self):
        if self.tracking_entry.get() != '' and isStrFloat(self.tracking_entry.get()):
            self.tracking_range = float(self.tracking_entry.get())
            self.tracking_label.config(text="Tracking Range: {}".format(self.tracking_entry.get()))
            self.updateConfig("Tracking Settings", "Range", self.tracking_entry.get())
            self.tracking_range.delete(0, 'end')
    

    def _quit(self):
        self.update_idletasks()
        self.update()
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.TFdata.save_fits()
    
    def tracking(self):
        resonance = self.TFdata.fits[-1][3]
        width = self.TFdata.fits[-1][5]
        new_start = resonance-self.tracking_range*width
        if new_start < 1:
            new_start = 1
        new_end = resonance+self.tracking_range*width
        if new_end > 90E5:
            new_end = 90E5
        
        self.params["Start Frequency"] = new_start
        self.params["End Frequency"] = new_end
        
        self.updateConfig('Frequency Sweep Settings', "Start Frequency", new_start)
        self.updateConfig('Frequency Sweep Settings', "End Frequency", new_end)
        self.label_list[0].config(text = "Start Frequency: {:.3f}".format(new_start))
        self.label_list[1].config(text = "End Frequency: {:.3f}".format(new_end))
        
    def phaseCorrection(self):
        self.params['Phase, deg'] = self.params['Phase, deg']-self.TFdata.xfit[3]*180/np.pi
        # print(self.params['Phase, deg'])
        self.lockin.Set_Phase(self.params['Phase, deg'])
        self.updateConfig('Frequency Sweep Settings', "Phase, deg", self.params['Phase, deg'])
        self.label_list[2].config(text = "Phase, deg: {:.2f}".format(self.params['Phase, deg']))
        
    
    def switchGraph(self, event):
        if event == "Frequency Sweep":
            self.graph_sweep()
        if event == "Fit Details":
            self.graph_fits() 
        self.update_idletasks()
        self.update()

    def graph_sweep(self):
        self.ax.clear()
        self.ay.clear()
        if self.TFdata.last_sweep.ndim > 1:
            self.ax.plot(self.TFdata.last_sweep[:, 1], LF.Lorentz_x_quad(self.TFdata.last_sweep[:, 1], self.TFdata.xfit)*1E9/self.TFdata.current_amp, color='black')
            self.ay.plot(self.TFdata.last_sweep[:, 1], LF.Lorentz_y_quad(self.TFdata.last_sweep[:, 1], self.TFdata.yfit)*1E9/self.TFdata.current_amp, color='black')
        if np.asarray(self.TFdata.sweep).ndim > 1:
            self.ax.plot(np.asarray(self.TFdata.sweep)[:, 1], np.asarray(self.TFdata.sweep)[:, 2]*1E9/self.TFdata.current_amp, 'o')
            self.ay.plot(np.asarray(self.TFdata.sweep)[:, 1], np.asarray(self.TFdata.sweep)[:, 3]*1E9/self.TFdata.current_amp, 'o')
        if self.TFdata.last_sweep.ndim > 1:
            self.ax.plot(self.TFdata.last_sweep[:, 1], self.TFdata.last_sweep[:, 2]*1E9/self.TFdata.current_amp, 'o', fillstyle='none')
            self.ay.plot(self.TFdata.last_sweep[:, 1], self.TFdata.last_sweep[:, 3]*1E9/self.TFdata.current_amp, 'o', fillstyle='none')
        self.ax.set_title("Frequency Sweep")
        self.ax.set_ylabel("I, nA")
        self.ay.set_ylabel("I, nA")
        self.ay.set_xlabel("f, hz")
        self.canvas.draw()
        
        
    def graph_fits(self):
        
        self.ax2.clear()
        self.ay2.clear()
        if self.TFdata.saved_fits.ndim > 1:
            self.ax2.plot(self.TFdata.saved_fits[:, 0]-self.TFdata.timestamp_today, self.TFdata.saved_fits[:, 5])
            self.ay2.plot(self.TFdata.saved_fits[:, 0]-self.TFdata.timestamp_today, self.TFdata.saved_fits[:, 3])
            time0 = self.TFdata.saved_fits[0, 0]
            time1 = self.TFdata.saved_fits[-1,0]
        if np.asarray(self.TFdata.fits).ndim > 1:
            self.ax2.plot(np.asarray(self.TFdata.fits)[:, 0]-self.TFdata.timestamp_today, np.asarray(self.TFdata.fits)[:, 5])
            self.ay2.plot(np.asarray(self.TFdata.fits)[:, 0]-self.TFdata.timestamp_today, np.asarray(self.TFdata.fits)[:, 3])
            time1 = self.TFdata.fits[-1][0]
            if self.TFdata.saved_fits.ndim < 2:
                time0 = self.TFdata.fits[0][0]

        if self.TFdata.saved_fits.ndim > 1 or np.asarray(self.TFdata.fits).ndim > 1: 
            ticks_to_hours(self.ay2, (time0-self.TFdata.timestamp_today), (time1-self.TFdata.timestamp_today))
          
        self.ax2.set_title("Fit Values")
        self.ax2.set_ylabel("Width, hz")
        self.ay2.set_ylabel("$f_0$, hz")
        self.ay2.set_xlabel("time")
        
        self.canvas2.draw()
        
        
    def sweep(self):
        self.TFdata.reset_sweep()
        frequencies = np.linspace(self.params["Start Frequency"], self.params["End Frequency"], self.params["Num Pts"])
        self.gen.Set_Frequency(self.params["Start Frequency"])
        self.after(3*self.params["Wait Time, ms"])
        for idx, f in enumerate(frequencies):
            if self.run:
                self.gen.Set_Frequency(f)
                self.after(self.params["Wait Time, ms"])
                Vx, Vy = self.lockin.Read_XY()
                self.TFdata.append_sweep([time.time(), f, Vx, Vy, self.TFdata.drive, self.TFdata.current_amp])
                # if self.showGraph.get() == "Frequency Sweep":
                self.graph_sweep()
                self.update_idletasks()
                self.update()
            else:
                return False
        return True

    def start(self):
        self.start_button.config(text="Stop", bg="red", fg="white", command=self.stop)
        # Main Loop
        self.run = True
        while self.run:
            try:
                sweep_finished = self.sweep()
                self.TFdata.save_sweep()
                if self.fitBool.get() and sweep_finished:
                    xflag = self.TFdata.fit_sweep()
                    if xflag in [1,2,3,4]:
                        if self.trackBool:
                            self.tracking()
                        if self.correctPhaseBool:
                            self.phaseCorrection()
                    # if self.showGraph.get() == "Fit Details":
                    self.graph_fits()
                    if (time.time()-self.TFdata.last_save)/60 > self.save_interval:
                        self.TFdata.save_fits()
                        self.TFdata.reset_save_time()
                    if (time.time()-self.TFdata.timestamp_today) > 24*60*60:
                        self.TFdata.daily_save()
                
            except Exception as e:
                print(e)
                if self.run:
                    self.TFdata.save_fits()
                    self.run = False
                    try:
                        self.quit()
                        self.destroy()
                    except Exception as e:
                        print(e)
                    
        
    def stop(self):
        self.start_button.config(text="Start Sweep", bg="green", fg="white", command=self.start)
        self.run = False

        
if __name__ == "__main__":

    App = tkApp()        
    App.mainloop()
    