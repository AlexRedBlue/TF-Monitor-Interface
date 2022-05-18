# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 19:35:44 2022

@author: alexd

Tuning Fork Monitoring Application
"""


import tkinter as tk

from instruments import LOCKIN
from instruments import AGILENT_SIGNAL_GEN
from instruments import SignalGenerators
# from instruments.Liquid_Instruments import MokuLab

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import configparser
import os
import time

import traceback
import logging

import numpy as np
from tuning_fork import Lorentz_Fitting as LF

# TFdata Class
from handlers.tuning_fork import TFdata
# Useful Functions
from functions.info import close_win, ticks_to_hours, isStrInt, isStrFloat, phaseAdjust

class tkApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.state("zoomed")
        
        self.init_window_size()
        
        self.config = configparser.RawConfigParser()
        
        self.config_directory = "configs/"
        self.config_name = 'TFMI_Config.cfg'
        
        self.config_label = tk.Label(self, text=self.config_name)
        self.config_label.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(1*self.scaling_factor["y"]))
        
        if not os.path.exists(self.config_directory+self.config_name):
            self.initConfig()
            
        # Read configurations using section and key to get the value
        self.change_config(initial=True)
        self.config.read(self.config_directory+self.config_name)
        self.load_config(initial=True)
        
        self.init_logs()
        
        logging.info("Program Initialized")
        
        self.save_interval = 60 # in minutes
        
        # Interface frames
        self.wm_title("Freq Sweep Alpha")
        
        graph_size = 0.8
        # graph_ratio = 4.8/6.4
        graph_ratio = 1
        padding = (1-graph_size)/2*(self.win_zoom_inches["width"]/2)
        
        # Two Graphs
        self.graph_1 = tk.Frame(self)
        self.graph_1.place(x="{}i".format(padding),y="0i")
        self.graph_2 = tk.Frame(self)
        self.graph_2.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding),y="0i")
        
        self.fig = Figure(figsize=(graph_size*self.win_zoom_inches["width"]/2, graph_size*self.win_zoom_inches["width"]/2*graph_ratio), dpi=self.default_dpi)
        self.ax = self.fig.add_subplot(2,1,1)
        self.ay = self.fig.add_subplot(2,1,2, sharex=self.ax)
        
        self.fig2 = Figure(figsize=(graph_size*self.win_zoom_inches["width"]/2, graph_size*self.win_zoom_inches["width"]/2*graph_ratio), dpi=self.default_dpi)
        self.ax2 = self.fig2.add_subplot(2,1,1)
        self.ay2 = self.fig2.add_subplot(2,1,2, sharex=self.ax2)
        
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

        # Param Frames
        self.param_entry_frame = tk.Frame(self)
        self.param_entry_frame.place(x="{}i".format(1*self.scaling_factor["x"]), y="{}i".format(graph_size*self.win_zoom_inches["width"]/2*graph_ratio+0.75))
        self.param_label_frame = tk.Frame(self)
        self.param_label_frame.place(x="{}i".format(2*self.scaling_factor["x"]), y="{}i".format(graph_size*self.win_zoom_inches["width"]/2*graph_ratio+0.75))
        
        self.param_entry_frame_2 = tk.Frame(self)
        self.param_entry_frame_2.place(x="{}i".format(4*self.scaling_factor["x"]), y="{}i".format(graph_size*self.win_zoom_inches["width"]/2*graph_ratio+0.75))
        self.param_label_frame_2 = tk.Frame(self)
        self.param_label_frame_2.place(x="{}i".format(5*self.scaling_factor["x"]), y="{}i".format(graph_size*self.win_zoom_inches["width"]/2*graph_ratio+0.75))
        
        # Sensitivity Options
        self.sensitivity = tk.StringVar(self)
        self.sensitivity.set(self.current_sens) # default value
        self.sens_options = tk.OptionMenu(self, self.sensitivity, *self.sens_list, command=self.switchSens)
        self.sens_options.place(x="{}i".format(6.5*self.scaling_factor["x"]), y="{}i".format(graph_size*self.win_zoom_inches["width"]/2*graph_ratio+0.75))
        
        # Time Constant Options
        self.time_constant = tk.StringVar(self)
        self.time_constant.set(self.current_time_constant) # default value
        self.time_constant_options = tk.OptionMenu(self, self.time_constant, *self.time_constant_list, command=self.switchTC)
        self.time_constant_options.place(x="{}i".format(6.5*self.scaling_factor["x"]), y="{}i".format(graph_size*self.win_zoom_inches["width"]/2*graph_ratio+1.25))
        
        # Checkbox Frame
        self.checkbox_frame = tk.Frame(self)
        self.checkbox_frame.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding), y="{}i".format(0.5+graph_size*self.win_zoom_inches["width"]/2*graph_ratio))
        
        self.current_temp_label = tk.Label(master=self, text="Current Temp: ")
        self.current_temp_label.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding), y="{}i".format(1.5+graph_size*self.win_zoom_inches["width"]/2*graph_ratio))
        
        # Option Frame
        self.option_frame = tk.Frame(self)
        self.option_frame.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding), y="{}i".format(1.0+graph_size*self.win_zoom_inches["width"]/2*graph_ratio))
        
        # Tracking checkbox
        self.tracking_button = tk.Button(self.checkbox_frame, text="Update Tracking Range", padx=10, command=self.update_tracking_range)
        self.tracking_button.pack(in_=self.checkbox_frame, side=tk.RIGHT, padx=10)
        self.tracking_label = tk.Label(self.checkbox_frame, text="Tracking Range: {:.2f}".format(self.tracking_range))
        self.tracking_label.pack(in_=self.checkbox_frame, side=tk.RIGHT, padx=10)
        self.tracking_entry = tk.Entry(self.checkbox_frame, width=5)
        self.tracking_entry.pack(in_=self.checkbox_frame, side=tk.RIGHT, padx=10)
        
               
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
                if key == "Num Pts" or key == "Wait Time, ms":
                    self.label_list.append(tk.Label(self.param_label_frame_2, text = key+": {}".format(val)))
                else:
                    self.label_list.append(tk.Label(self.param_label_frame_2, text = key+": {:.3f}".format(val)))
                self.label_list[-1].pack(in_=self.param_label_frame_2, pady=5)
                
                self.entry_list.append(tk.Entry(self.param_entry_frame_2, width=8))
                self.entry_list[-1].pack(in_=self.param_entry_frame_2, pady=5)

        
        # Update Params Button
        self.update_button = tk.Button(master=self, text="Update Params", command=self.update_sweep_params)
        self.update_button.pack(in_=self.param_entry_frame, pady=5)
        
        # Checkbox bools
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
        
        # Graph options
        self.graph_option_list = ["Temperature", "Resonance", "Amplitude", "Width", "Phase", "Bgd_0", "Bgd_1", "Bgd_2"]
        self.graph_labels      = ["T, K", "$f_0$, hz", "I, nA", "$\\Delta f$, hz", "Phase", "Bgd_0", "Bgd_1", "Bgd_2"]
        
        self.whichGraph_1 = tk.StringVar(self)
        self.whichGraph_1.set(self.graph_option_list[3]) # default value
        self.whichGraph_1_Options = tk.OptionMenu(self, self.whichGraph_1, *self.graph_option_list, command=self.switchGraph)
        self.whichGraph_1_Options.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(2.5*self.scaling_factor["y"]))
        
        self.whichGraph_2 = tk.StringVar(self)
        self.whichGraph_2.set(self.graph_option_list[1]) # default value
        self.whichGraph_2_Options = tk.OptionMenu(self, self.whichGraph_2, *self.graph_option_list, command=self.switchGraph)
        self.whichGraph_2_Options.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(6*self.scaling_factor["y"]))
        
        # Settings Frame
        self.settings_frame = tk.Frame(self)
        self.settings_frame.place(x="{}i".format(self.win_zoom_inches["width"]-2.5),  y="{}i".format(self.win_zoom_inches["height"]-9/16))

        # Settings Menu Button
        self.settings_button = tk.Button(master=self, text="Settings", command=self.settingsWindow)
        self.settings_button.pack(in_=self.settings_frame, side=tk.RIGHT, padx=5, pady=5)
        
        # Clear Graphs Button
        self.clear_button = tk.Button(master=self, text="Save & Clear Graphs", command=self.clearData)
        self.clear_button.pack(in_=self.settings_frame, side=tk.LEFT, padx=5, pady=5)
        
        # Start Button
        self.start_button = tk.Button(master=self, text="Start", bg='green', fg='white', height=2, width=9, command=self.start)
        self.start_button.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(8.5*self.scaling_factor["y"]))
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # self.update_idletasks()
        # self.update()

    def on_closing(self):
        self.update_idletasks()
        self.update()
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.run = False
            self.TFdata.save_fits()
            logging.info("Program Terminated")
            self.quit()
            self.destroy()

    def initConfig(self):
        self.config.add_section('Frequency Sweep Settings')
        self.config.set('Frequency Sweep Settings', 'Start Frequency', '32700')
        self.config.set('Frequency Sweep Settings', 'End Frequency', '32900')
        self.config.set('Frequency Sweep Settings', 'Phase, deg', '0')
        self.config.set('Frequency Sweep Settings', 'Num Pts', '100')
        self.config.set('Frequency Sweep Settings', 'Wait Time, ms', '1000')
        self.config.set('Frequency Sweep Settings', 'Drive, V', '0.1')
        self.config.set('Frequency Sweep Settings', 'Current Amp', '10000')
        
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
        
        self.config.add_section("Logs Settings")
        self.config.set("Logs Settings", "Log File Name", "TFMI")
        
        with open(self.config_directory+self.current_config, 'w') as output:
            self.config.write(output)
    
    def load_config(self, initial=False):
        
        self.tracking_range = float(self.config["Tracking Settings"]["Range"])
        
        self.TFdata = TFdata(TF_name=self.config["Monitor Save Settings"]["Tuning Fork Name"], 
                             save_folder=self.config["Monitor Save Settings"]["Save Folder"])
        self.TFdata.set_drive(float(self.config["Frequency Sweep Settings"]["Drive, V"]))
        self.TFdata.set_current_amp(float(self.config["Frequency Sweep Settings"]["Current Amp"]))
        
        NewLockinSet = self.set_lockin(self.config["Instrument Settings"]["lock-in model"], self.config["Instrument Settings"]["lock-in gpib"])
        NewGenSet = self.set_signalgen(self.config["Instrument Settings"]["signal-gen model"], self.config["Instrument Settings"]["signal-gen gpib"])
            
        if NewLockinSet == False or NewGenSet == False:
            if not NewLockinSet:
                print("Something went wrong with Lock-in GPIB settings")
            if not NewGenSet:
                print("Something went wrong with Signal-Gen GPIB settings")
            self.settingsWindow()
        
        try:
            self.gen.Set_Voltage(float(self.config["Frequency Sweep Settings"]["Drive, V"]))
        except:
            print("Drive Not Set Properly")
        try:
            self.lockin.Set_Phase(float(self.config["Frequency Sweep Settings"]["Phase, deg"]))
        except:
            print("Phase Not Set Properly")
        
        self.params = { "Start Frequency": float(self.config["Frequency Sweep Settings"]["Start Frequency"]),
                        "End Frequency": float(self.config["Frequency Sweep Settings"]["End Frequency"]),
                        "Phase, deg": float(self.config["Frequency Sweep Settings"]["Phase, deg"]),
                        "Num Pts": int(self.config["Frequency Sweep Settings"]["Num Pts"]),
                        "Wait Time, ms": int(self.config["Frequency Sweep Settings"]["Wait Time, ms"]),
                        "Drive, V": float(self.config["Frequency Sweep Settings"]["Drive, V"])
                      }
        if not initial:
            self.update_sweep_params()
            self.fitBool.set(int(self.config["Monitor Checkbox Settings"]["Fitting"]))
            self.trackBool.set(int(self.config["Monitor Checkbox Settings"]["Tracking"]))
    
    
    def updateConfig(self, section, key, value):
    #Update config using section key and the value to change
    #call this when you want to update a value in configuation file
    # with some changes you can save many values in many sections
        self.config.set(section, key, value)
        with open(self.config_directory+self.config_name, 'w') as output:
            self.config.write(output)
            
            
    def update_checkbox_config(self):
        self.updateConfig("Monitor Checkbox Settings", "Fitting", self.fitBool.get())
        self.updateConfig("Monitor Checkbox Settings", "Tracking", self.trackBool.get())
        
    def init_logs(self):
        logging.basicConfig(filename='logs/'+self.config["Logs Settings"]["Log File Name"]+".log", 
                            format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        
        fileh = logging.FileHandler('logs/'+self.config["Logs Settings"]["Log File Name"]+".log", 'a')
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        fileh.setFormatter(formatter)
        
        log = logging.getLogger()  # root logger
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fileh) 
            
    def init_window_size(self):
        self.update_idletasks()
        self.default_dpi = 96 # 1080p monitors
        default_screen_size = {"width":20, "height":11.25}
        self.screen_ratio = {"width": 16, "height": 9}
        self.screen_size = {"x":self.winfo_screenwidth(), "y":self.winfo_screenheight()}
        self.screen_size_inches = {"width": self.winfo_screenwidth()/self.default_dpi, 
                                    "height": self.winfo_screenheight()/self.default_dpi}
        
        self.win_zoom_size = {"x":self.winfo_width(), "y":self.winfo_height()}
        
        self.win_zoom_inches = {"width": self.win_zoom_size["x"]/self.default_dpi, 
                                "height": self.win_zoom_size["y"]/self.default_dpi}
        self.scaling_factor = {"x": self.screen_size_inches["width"]/default_screen_size["width"],
                               "y": self.screen_size_inches["height"]/default_screen_size["height"]}
     
    def switchSens(self, event):
        try:
            # print(event)
            self.lockin.Set_Sensitivity(event)
            self.current_sens = event
        except:
            traceback.print_exc()
            self.sensitivity.set(self.current_sens)
        
    def switchTC(self, event):
        try:
            # print(event)
            self.lockin.Set_Time_Constant(event)
            self.current_time_constant = event
        except:
            traceback.print_exc()
            self.time_constant.set(self.current_time_constant)
    
    def settingsWindow(self):
        sWin = tk.Toplevel(self)
        
        try:
            self.start_button.config(text="Start Sweep", bg="green", fg="white", command=self.start)
        except:
            pass
        self.run = False
        
        sWin.geometry("540x360")
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
        self.L_Model_Options = tk.OptionMenu(sWin, self.Lockin_Model, "LI 5640", "SR 830", "Moku", "Testing")
        self.L_Model_Options.place(anchor="nw", x=160, y=28)
        
        self.SignalGen_Model = tk.StringVar(sWin)
        self.SignalGen_Model.set(self.config["Instrument Settings"]["Signal-Gen Model"]) # default value
        self.SG_Model_Options = tk.OptionMenu(sWin, self.SignalGen_Model, "Keysight", "Agilent", "Moku", "Testing")
        self.SG_Model_Options.place(anchor="nw", x=160, y=68)

        # Save Folder
        self.Save_Folder_entry = tk.Entry(sWin, width=20)
        self.Save_Folder_entry.insert(0, self.config["Monitor Save Settings"]["Save Folder"])
        self.Save_Folder_entry.place(anchor="nw", x=100, y=120)
        
        Folder_Label = tk.Label(sWin, text="Save Folder")
        Folder_Label.place(x=15, y=120)
        
        # TF Name
        self.TF_savename = tk.Entry(sWin, width=20)
        self.TF_savename.insert(0, self.config["Monitor Save Settings"]["Tuning Fork Name"])
        self.TF_savename.place(anchor="nw", x=100, y=150)
        
        Name_Label = tk.Label(sWin, text="TF Name")
        Name_Label.place(x=15, y=150)
        
        try:
            next_fit_name = self.TFdata.getfilename(self.TFdata.save_folder, "{}_fits_{}".format(self.TFdata.TF_name, self.TFdata.today)).replace(self.TFdata.current_working_dir,'')
            
            self.fit_Label = tk.Label(sWin, text="Next Fit File: \t\t"+next_fit_name)
            self.fit_Label.place(x=15, y=200)
            
            self.sweep_label = tk.Label(sWin, text="Current Sweep Folder: \t"+"/data/{}/sweeps_{}".format(self.config["Monitor Save Settings"]["Save Folder"], self.TFdata.today))
            self.sweep_label.place(x=15, y=230)
        except:
            pass
        
        self.config_name_label = tk.Label(sWin, text=self.config_name)
        self.config_name_label.place(x=300, y=35)
        
        Config_Button = tk.Button(sWin, text="Select Config", command=self.change_config)
        Config_Button.place(x=300, y=60)
        
        
        ###### TODO #######
        # TODO
        # More Settings
        
        # Save Folder
        self.current_amp_entry = tk.Entry(sWin, width=12)
        self.current_amp_entry.insert(0, float(self.config["Frequency Sweep Settings"]["Current Amp"]))
        self.current_amp_entry.place(anchor="nw", x=400, y=120)
        
        Current_Amp_Label = tk.Label(sWin, text="Current Amp")
        Current_Amp_Label.place(x=300, y=120)

        
        ###### END OF TODO ######

        save_button = tk.Button(sWin, text='Save', command=self.save_settings)
        save_button.place(anchor="sw", x=15, y=345)
        close_button = tk.Button(sWin, text='Exit', command=lambda:close_win(sWin))
        close_button.place(anchor="se", x=525, y=345)

        # self.wait_window(self)
    
    def load_settings_text(self):
        self.Lockin_GPIB.delete(0,'end')
        self.Lockin_GPIB.insert(0, self.config["Instrument Settings"]["Lock-in GPIB"])
        self.SignalGen_GPIB.delete(0,'end')
        self.SignalGen_GPIB.insert(0, self.config["Instrument Settings"]["Signal-Gen GPIB"])
        self.Lockin_Model.set(self.config["Instrument Settings"]["Lock-in Model"])
        self.SignalGen_Model.set(self.config["Instrument Settings"]["Signal-Gen Model"])
        self.Save_Folder_entry.delete(0,'end')
        self.Save_Folder_entry.insert(0, self.config["Monitor Save Settings"]["Save Folder"])
        self.TF_savename.delete(0,'end')
        self.TF_savename.insert(0, self.config["Monitor Save Settings"]["Tuning Fork Name"])
        self.config_name_label.config(text=self.config_name)
        self.current_amp_entry.delete(0,'end')
        self.current_amp_entry.insert(0, float(self.config["Frequency Sweep Settings"]["Current Amp"]))
        next_fit_name = self.TFdata.getfilename(self.TFdata.save_folder, "{}_fits_{}".format(self.TFdata.TF_name, self.TFdata.today)).replace(self.TFdata.current_working_dir,'')
        self.fit_Label.config(text="Next Fit File: \t\t"+next_fit_name)
        next_sweep_name = "/data/{}/sweeps_{}".format(self.TFdata.save_folder, self.TFdata.today)
        self.sweep_label.config(text="Current Sweep Folder: \t"+next_sweep_name)
        
        
    def save_settings(self):
        
        if isStrInt(self.Lockin_GPIB.get()):
            NewLockinSet = self.set_lockin(self.Lockin_Model.get(), self.Lockin_GPIB.get())
            if NewLockinSet:
                self.updateConfig("Instrument Settings", "Lock-in GPIB", self.Lockin_GPIB.get())
                self.updateConfig("Instrument Settings", "Lock-in Model", self.Lockin_Model.get())
            else:
                print("Invalid Lock-in Settings")
        if isStrInt(self.SignalGen_GPIB.get()):
            NewGenSet = self.set_signalgen(self.SignalGen_Model.get(), self.SignalGen_GPIB.get())
            if NewGenSet:
                self.updateConfig("Instrument Settings", "Signal-Gen GPIB", self.SignalGen_GPIB.get())
                self.updateConfig("Instrument Settings", "Signal-Gen Model", self.SignalGen_Model.get())
            else:
                print("Invalid Signal Gen Settings")
        
        if self.Save_Folder_entry.get() != self.config["Monitor Save Settings"]["Save Folder"]:
            self.updateConfig("Monitor Save Settings", "Save Folder", self.Save_Folder_entry.get())
            self.TFdata.save_folder = self.Save_Folder_entry.get()

        if self.TF_savename.get() != self.config["Monitor Save Settings"]["Tuning Fork Name"]:
            self.updateConfig("Monitor Save Settings", "Tuning Fork Name", self.TF_savename.get())
            self.TFdata.TF_name = self.TF_savename.get()

        next_fit_name = self.TFdata.getfilename(self.TFdata.save_folder, "{}_fits_{}".format(self.TFdata.TF_name, self.TFdata.today)).replace(self.TFdata.current_working_dir,'')
        self.fit_Label.config(text="Next Fit File: \t\t"+next_fit_name)
        next_sweep_name = "/data/{}/sweeps_{}".format(self.TFdata.save_folder, self.TFdata.today)
        self.sweep_label.config(text="Current Sweep Folder: \t"+next_sweep_name)

        if isStrFloat(self.current_amp_entry.get()):
            self.updateConfig("Frequency Sweep Settings", "Current Amp", self.current_amp_entry.get())
            self.TFdata.set_current_amp(float(self.current_amp_entry.get()))
            
                
    def change_config(self, initial=False):
        new_config_file = tk.filedialog.askopenfilename(initialdir=self.config_directory)
        # print(new_config_file, new_config_file.split('/')[-1])
        self.config_name = new_config_file.split('/')[-1]
        self.config.read(self.config_directory+self.config_name)
        self.init_logs()
        self.load_config(initial)
        self.config_label.config(text=self.config_name)
        if not initial:
            self.load_settings_text()
                
    def update_sweep_params(self):
        old_params = self.params
        for idx, (key, val) in enumerate(self.params.items()):
            try:
                if self.entry_list[idx].get() != '':
                    if key == "Num Pts" or key == "Wait Time, ms":
                        self.params[key] = int(self.entry_list[idx].get())
                    else:
                        self.params[key] = float(self.entry_list[idx].get())
                    if key == "Drive, V":
                        try:
                            self.gen.Set_Voltage(float(self.entry_list[idx].get()))
                        except:
                            self.params[key] = old_params[key]
                            print("Drive Not Set Properly")
                    if key == "Phase, deg":
                        try:
                            self.lockin.Set_Phase(float(self.entry_list[idx].get()))
                        except:
                            self.params[key] = old_params[key]
                            print("Phase Not Set Properly")
                    self.updateConfig('Frequency Sweep Settings', key, self.params[key])
                    self.entry_list[idx].delete(0, 'end')
                if key == "Num Pts" or key == "Wait Time, ms":
                    self.label_list[idx].config(text=key+": {:d}".format(int(self.params[key])))
                else:
                    self.label_list[idx].config(text=key+": {:.3f}".format(float(self.params[key])))
            except Exception as e:
                print(e)

    def set_lockin(self, model, GPIB):
        try:
            if model == "LI 5640":
                self.lockin = LOCKIN.LI5640("GPIB0::"+GPIB+"::INSTR")
            elif model == "SR 830":
                self.lockin = LOCKIN.SR830("GPIB0::"+GPIB+"::INSTR")
            # elif model == "Moku":
            #     try:
            #         self.gen = self.MokuLab.instrument_dict["Lock-in Amplifier"]
            #     except:
            #         self.lockin = MokuLab("IP", GPIB).enable_lockin(2)
            #         self.gen = self.MokuLab["Lock-in Amplifier"]
            elif model == "Testing":
                print("lock-in is in testing mode")
                self.lockin = LOCKIN.test_lockin("GPIB0::"+GPIB+"::INSTR")
            else:
                print("Invalid Lock-in Instrument Type: Reset Config File")
                return False
            self.sens_list = [j for (i, j) in self.lockin.sens_dict.items()]
            self.time_constant_list = [j for (i, j) in self.lockin.time_const_dict.items()]
            self.current_sens = self.lockin.Get_Sensitivity()
            self.current_time_constant = self.lockin.Get_Time_Constant()
            try:
                self.sensitivity.set(self.current_sens)
                self.sens_options["menu"].delete(0, "end")
                for sens in self.sens_list:
                    self.sens_options['menu'].add_command(label=sens, command=tk._setit(self.sensitivity, sens, self.switchSens))
                # self.sens_options.config(command=self.switchSens)
            except:
                pass
            try:
                self.time_constant.set(self.current_time_constant)
                self.time_constant_options["menu"].delete(0, "end")
                for tc in self.time_constant_list:
                    self.time_constant_options['menu'].add_command(label=tc, command=tk._setit(self.time_constant, tc, self.switchTC))
                # self.time_constant_options.config(command=self.switchTC)
            except:
                pass
            return True
        except:
            traceback.print_exc()
            self.sens_list = ["None"]
            self.time_constant_list = ["None"]
            self.current_sens = self.sens_list[0]
            self.current_time_constant = self.time_constant_list[0]
            try:
                self.sensitivity.set(self.current_sens)
            except:
                pass
            try:
                self.time_constant.set(self.current_time_constant)
            except:
                pass
            return False
    
    def set_signalgen(self, model, GPIB):
        try:
            if model == "Keysight" or model == "Agilent":
                self.gen = AGILENT_SIGNAL_GEN.AGILENT_SIGNAL_GEN("GPIB0::"+GPIB+"::INSTR")
            # elif model == "Moku":
            #     try:
            #         self.gen = self.MokuLab.instrument_dict["Waveform Generator"]
            #     except:
            #         self.MokuLab("IP", GPIB).enable_signal_gen(1)
            #         self.gen = self.MokuLab["Waveform Generator"]
            elif model == "Testing":
                print("signal-gen is in testing mode")
                self.gen = SignalGenerators.test_gen("GPIB0::"+GPIB+"::INSTR")
            else:
                print("Invalid Signal-Gen Instrument Type: Reset Config File")
            return True
        except:
            return False

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)
        
        
    def update_tracking_range(self):
        if self.tracking_entry.get() != '' and isStrFloat(self.tracking_entry.get()):
            self.tracking_range = float(self.tracking_entry.get())
            self.tracking_label.config(text="Tracking Range: {}".format(self.tracking_entry.get()))
            self.updateConfig("Tracking Settings", "Range", self.tracking_entry.get())
            self.tracking_range.delete(0, 'end')
    

    
    def tracking(self):
        resonance = self.TFdata.xfit[0]
        width = self.TFdata.xfit[2]
        if resonance > self.params["Start Frequency"] and resonance < self.params["End Frequency"]:
            new_start = resonance-self.tracking_range*width
            new_end = resonance+self.tracking_range*width
        else:
            current_range = self.params["End Frequency"] - self.params["Start Frequency"]
            new_start = self.params["Start Frequency"] - 0.5*current_range
            new_end = self.params["End Frequency"] + 0.5*current_range
        
        if new_end > 90E5:
                new_end = 90E5
        if new_start < 1:
                new_start = 1
        
        self.params["Start Frequency"] = new_start
        self.params["End Frequency"] = new_end
        
        self.updateConfig('Frequency Sweep Settings', "Start Frequency", new_start)
        self.updateConfig('Frequency Sweep Settings', "End Frequency", new_end)
        self.label_list[0].config(text = "Start Frequency: {:.3f}".format(new_start))
        self.label_list[1].config(text = "End Frequency: {:.3f}".format(new_end))
        
    def phaseCorrection(self):
        self.params['Phase, deg'] = phaseAdjust(self.params['Phase, deg']-(self.TFdata.xfit[3]*180/np.pi))
        self.lockin.Set_Phase(self.params['Phase, deg'])
        self.updateConfig('Frequency Sweep Settings', "Phase, deg", self.params['Phase, deg'])
        self.label_list[2].config(text = "Phase, deg: {:.2f}".format(self.params['Phase, deg']))
        
    
    def switchGraph(self, event):
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
            self.ax2.plot(self.TFdata.saved_fits[:, 0], self.TFdata.saved_fits[:, 3+self.graph_option_list.index(self.whichGraph_1.get())])
            self.ay2.plot(self.TFdata.saved_fits[:, 0], self.TFdata.saved_fits[:, 3+self.graph_option_list.index(self.whichGraph_2.get())])
            time0 = self.TFdata.saved_fits[0, 0]
            time1 = self.TFdata.saved_fits[-1,0]
        if np.asarray(self.TFdata.fits).ndim > 1:
            self.ax2.plot(np.asarray(self.TFdata.fits)[:, 0], np.asarray(self.TFdata.fits)[:, 3+self.graph_option_list.index(self.whichGraph_1.get())])
            self.ay2.plot(np.asarray(self.TFdata.fits)[:, 0], np.asarray(self.TFdata.fits)[:, 3+self.graph_option_list.index(self.whichGraph_2.get())])
            time1 = self.TFdata.fits[-1][0]
            if self.TFdata.saved_fits.ndim < 2:
                time0 = self.TFdata.fits[0][0]
        
        if self.TFdata.saved_fits.ndim > 1 or np.asarray(self.TFdata.fits).ndim > 1: 
            ticks_to_hours(self.ay2, time0, time1)
          
        self.ax2.set_title("Fit Values")
        self.ax2.set_ylabel(self.graph_labels[self.graph_option_list.index(self.whichGraph_1.get())])
        self.ay2.set_ylabel(self.graph_labels[self.graph_option_list.index(self.whichGraph_2.get())])
        self.ay2.set_xlabel("time")
        
        self.canvas2.draw()
        
    def update_temp_label(self):
        try:
            if self.TFdata.T > 100:
                self.current_temp_label.config(text="Current Temp: {:.1f} K".format(self.TFdata.T))
            elif self.TFdata.T > 10:
                self.current_temp_label.config(text="Current Temp: {:.2f} K".format(self.TFdata.T))
            elif self.TFdata.T > 1:
                self.current_temp_label.config(text="Current Temp: {:.3f} K".format(self.TFdata.T))
            elif self.TFdata.T > 0.1:
                self.current_temp_label.config(text="Current Temp: {:.1f} mK".format(1000*self.TFdata.T))
            elif self.TFdata.T > 0.01:
                self.current_temp_label.config(text="Current Temp: {:.2f} mK".format(1000*self.TFdata.T))
            elif self.TFdata.T > 0.001:
                self.current_temp_label.config(text="Current Temp: {:.3f} mK".format(1000*self.TFdata.T))
            else:
                self.current_temp_label.config(text="Current Temp: {:.1f} uK".format(1e6*self.TFdata.T))
        except:
            pass
        
    def clearData(self):
        self.run = False
        self.start_button.config(text="Start Sweep", bg="green", fg="white", command=self.start)
        if tk.messagebox.askokcancel("Clear Graphs", "Confirm"):
            self.TFdata.daily_save()
            self.TFdata.store_last_sweep([])
            self.graph_fits()
            self.graph_sweep()
                
    def sweep(self):
        self.TFdata.reset_sweep()
        frequencies = np.linspace(self.params["Start Frequency"], self.params["End Frequency"], self.params["Num Pts"])
        update_frequency = 100 # in ms
        update_time_left = 3*int(self.params["Wait Time, ms"])
        self.gen.Set_Frequency(self.params["Start Frequency"])
        while update_time_left > 0:
            if update_time_left > update_frequency:
                self.after(update_frequency, self.update())
            else:
                self.after(update_time_left, self.update())
            update_time_left -= update_frequency
        for idx, f in enumerate(frequencies):
            if self.run:
                self.gen.Set_Frequency(f)
                update_time_left = int(self.params["Wait Time, ms"])
                while update_time_left > 0:
                    if update_time_left > update_frequency:
                        self.after(update_frequency, self.update())
                    else:
                        self.after(update_time_left, self.update())
                    update_time_left -= update_frequency
                Vx, Vy = self.lockin.Read_XY()
                self.TFdata.append_sweep([time.time(), f, Vx, Vy, self.TFdata.drive, self.TFdata.current_amp])
                # if self.showGraph.get() == "Frequency Sweep":
                self.graph_sweep()
                self.update_idletasks()
                self.update()
            else:
                return False
        return True
    
    def savegraph(self, num=0):
        fname = "data/{}/figures/{}_{}__{}".format(self.config["Monitor Save Settings"]["Save Folder"], 
                                               self.config["Monitor Save Settings"]["Tuning Fork Name"], 
                                               self.TFdata.today, num)
        folders = fname.split("/")
        # print(fname, "file exists:", os.path.exists(fname))
        if not os.path.exists(fname):
            # print(folders[0]+'/'+folders[1]+'/'+folders[2], "directory exists:", os.path.exists(folders[0]+'/'+folders[1]+'/'+folders[2]))
            if os.path.exists(folders[0]+'/'+folders[1]+'/'+folders[2]):
                self.fig2.savefig(fname, dpi=300)
            elif os.path.exists(folders[0]+'/'+folders[1]):
                os.mkdir(folders[0]+'/'+folders[1]+'/'+folders[2])
                self.fig2.savefig(fname, dpi=300)
            else:
                print(folders[0]+'/'+folders[1], "save directory doesnt exist")
        else:
            self.savegraph(num=num+1)

    def start(self):
        self.start_button.config(text="Stop", bg="red", fg="white", command=self.stop)
        logging.info("Started Sweeping")
        # Main Loop
        self.run = True
        while self.run:
            try:
                sweep_finished = self.sweep()
                if sweep_finished:
                    self.TFdata.save_sweep()
                    if self.fitBool.get():
                        xflag = self.TFdata.fit_sweep()
                        if self.trackBool.get():
                                self.tracking()
                        if xflag in [1,2,3,4]:
                            self.update_temp_label()
                            self.TFdata.update_recent_temp_file()
                            if self.correctPhaseBool.get():
                                self.phaseCorrection()
                        # if self.showGraph.get() == "Fit Details":
                        self.graph_fits()
                        if (time.time()-self.TFdata.timestamp_today) > 24*60*60:
                            try:
                                self.savegraph()
                            except:
                                print("Unable to save figure")
                            self.TFdata.daily_save()
                            logging.info("Fit Data Saved")
                        elif (time.time()-self.TFdata.last_save)/60 > self.save_interval:
                            self.TFdata.save_fits()
                            self.TFdata.reset_save_time()
                            logging.info("Fit Data Saved")
                        
                
            except Exception as e1:
                logging.warning(e1)
                traceback.print_exc()
                if self.run:
                    self.TFdata.save_fits()
                    self.run = False
                    try:
                        self.start_button.config(text="Start Sweep", bg="green", fg="white", command=self.start)
                    except Exception as e2:
                        logging.warning(e2)
                        traceback.print_exc(file=open("logs/"+self.config["Logs Settings"]["Log File Name"]+'.txt', 'w'))
            
        
    def stop(self):
        self.start_button.config(text="Start Sweep", bg="green", fg="white", command=self.start)
        self.run = False
        logging.info("Paused Sweeping")
        
    
    def _quit(self):
        self.update_idletasks()
        self.update()
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.TFdata.save_fits()
        
if __name__ == "__main__":
    if os.getcwd().split("\\")[-1] == "TF-Monitor-Interface":
        App = tkApp()        
        App.mainloop()
    else:
        print("TFMI_App is in incorrect directory:", os.getcwd())
        print("TFMI_App is meant to run in TF-Monitor-Interface project")
    