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

import numpy as np
from tuning_fork import Lorentz_Fitting as LF

def close_win(top):
        top.destroy()
        
def isStrInt(text):
    try:
        int(text)
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
        self.header = None
        self.sweep_header = None
        self.reset_sweep()
        self.reset_fits()
        self.reset_saved_fits()
        self.reset_save_time()

    def get_today(self):
        now = datetime.now()
        self.today = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = time.mktime(self.today.timetuple())
        self.today = self.today.strftime("%Y-%m-%d")
        
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
        if self.sweep.ndim > 1:
            guess = [(self.sweep[-1, 1]+self.sweep[0, 1])/2, 0, (self.sweep[-1, 1]-self.sweep[0, 1])/8, 0, 0, 0, 0]
            xfit, xflag = LF.Lorentz_Fit_X_quad(self.sweep[:, 1], self.sweep[:, 2], guess)
            xfit = np.abs(xfit)
            # print(xfit)
            yfit, yflag = LF.Lorentz_Fit_X_quad(self.sweep[:, 1], self.sweep[:, 3], guess)
            yfit = np.abs(yfit)
        self.append_fits([self.sweep[:, 0].mean(), self.drive, *xfit, *yfit])
        
        
    def getfilename(self, directory, file_tag, num=0):
        fname = self.current_working_dir+r"\data\{}\{}__{}.dat".format(directory, file_tag, num)
        if os.path.isdir(self.current_working_dir+"\\data\\"+directory) == False:
            os.makedirs(self.current_working_dir+"\\data\\"+directory)
        if os.path.isfile(fname):
            return self.getfilename(directory, file_tag, num+1)
        return fname
        
    def save_fits(self):
        if np.array(self.fits).ndim > 1:
            fname = self.getfilename(self.save_directory, "{}_fits_{}".format(self.TF_name, self.today))
            if self.header is not None:
                np.savetxt(fname, np.array(self.fits), header=self.header, delimiter='\t')
            else:
                np.savetxt(fname, np.array(self.fits), delimiter='\t')
            
    def save_sweep(self):
        fname = self.getfilename(self.save_directory+"\sweeps_{}".format(self.today), "{}_{}".format(self.TF_name, self.today))
        if self.sweep_header is not None:
            np.savetxt(fname, np.array(self.sweep), header=self.sweep_header, delimiter='\t')
        else:
            np.savetxt(fname, np.array(self.sweep), delimiter='\t')
            

class tkApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.config = configparser.RawConfigParser()
        
        if not os.path.exists('TFMI_Config.cfg'):
            self.initConfig()
            
        # Read configurations using section and key to get the value
        self.config.read('TFMI_Config.cfg')
        
        self.save_interval = 60 # in minutes
        
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
        
        
        self.wm_title("Freq Sweep Alpha")
        
        self.row1 = tk.Frame(self)
        self.row1.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.row2 = tk.Frame(self)
        self.row2.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.row3 = tk.Frame(self)
        self.row3.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # self.bottom1 = tk.Frame(self)
        # self.bottom2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # self.bottom1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(2,1,1)
        self.ay = self.fig.add_subplot(2,1,2)

        
        self.TFdata = TFdata(TF_name=self.config["Monitor Save Settings"]["Tuning Fork Name"], 
                             save_directory=self.config["Monitor Save Settings"]["Save Folder"])
        self.TFdata.set_drive(float(self.config["Frequency Sweep Settings"]["Drive"]))
        self.TFdata.set_current_amp(float(self.config["Frequency Sweep Settings"]["Current Amp"]))
        
        self.params = {
                        "Num Pts": int(self.config["Frequency Sweep Settings"]["Num Pts"]),
                        "End Frequency": float(self.config["Frequency Sweep Settings"]["End Frequency"]),
                        "Start Frequency": float(self.config["Frequency Sweep Settings"]["Start Frequency"])
                      }
        
        self.wait_time = int(float(self.config["Frequency Sweep Settings"]["Wait Time"])*1000) # wait time in ms
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(in_=self.row1, side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(in_=self.row1, side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        
        
        
        
        self.start_button = tk.Button(master=self, text="Start", command=self.start)
        self.start_button.pack(in_=self.row3, side=tk.LEFT, padx=5, pady=5)
        
        
        # labels & Text Boxes
        self.label_list = []
        self.entry_list = []
        for idx, (key, val) in enumerate(self.params.items()):
            
            self.label_list.append(tk.Label(self.row2, text = key+" "+str(val)))
            self.label_list[-1].pack(in_=self.row2,side=tk.RIGHT)
            
            self.entry_list.append(tk.Entry(self.row2, width=10))
            self.entry_list[-1].pack(in_=self.row2, side=tk.RIGHT)

        
        self.update_button = tk.Button(master=self, text="Update Params", command=self.update_sweep_params)
        self.update_button.pack(in_=self.row3, side=tk.RIGHT)
        
        self.fitBool = tk.IntVar()
        self.fitBool.set(int(self.config["Monitor Checkbox Settings"]["Fitting"]))
        self.fit_check = tk.Checkbutton(master=self, text="Fit", variable=self.fitBool, onvalue=1, offvalue=0, command=self.update_checkbox_config)
        self.fit_check.pack(in_=self.row3, side=tk.LEFT, padx=5, pady=5)
        
        self.trackBool = tk.IntVar()
        self.trackBool.set(int(self.config["Monitor Checkbox Settings"]["Tracking"]))
        self.track_check = tk.Checkbutton(master=self, text="Track", variable=self.trackBool, onvalue=1, offvalue=0, command=self.update_checkbox_config)
        self.track_check.pack(in_=self.row3, side=tk.LEFT, padx=5, pady=5)
        
        self.showGraph = tk.StringVar(self)
        self.showGraph.set("Frequency Sweep") # default value
        self.showGraph_Options = tk.OptionMenu(self, self.showGraph, "Frequency Sweep", "Fit Details", command=self.switchGraph)
        self.showGraph_Options.pack(in_=self.row3, side=tk.LEFT, padx=5, pady=5)
        
        self.settings_button = tk.Button(master=self, text="Settings", command=self.settingsWindow)
        self.settings_button.pack(in_=self.row3, side=tk.RIGHT, padx=5, pady=5)
        
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
        self.config.set('Frequency Sweep Settings', 'Num Pts', '100')
        self.config.set('Frequency Sweep Settings', 'Wait Time', '1')
        self.config.set('Frequency Sweep Settings', 'Drive', '1')
        self.config.set('Frequency Sweep Settings', 'Current Amp', '10000')
        self.config.set('Frequency Sweep Settings', 'Save Directory', r"C:\Users\physics-svc-mkdata\Documents\Data\TuningForkThermometer")
        
        self.config.add_section("Instrument Settings")
        self.config.set("Instrument Settings", "Lock-in Model", "LI 5640")
        self.config.set("Instrument Settings", "Lock-in GPIB", "25")
        self.config.set("Instrument Settings", "Signal-Gen Model", "Keysight")
        self.config.set("Instrument Settings", "Signal-Gen GPIB", "24")
        
        self.config.add_section("Monitor Save Settings")
        self.config.set("Monitor Save Settings", "Save Folder", "Testing")
        self.config.set("Monitor Save Settings", "Tuning Fork Name", "TestTF")
        
        self.config.add_section("Monitor Checkbox Settings")
        self.config.set("Monitor Checkbox Settings", "Fitting", "1")
        self.config.set("Monitor Checkbox Settings", "Tracking", "0")
        
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
            
    def settingsWindow(self):
        sWin = tk.Toplevel(self)
        
        sWin.geometry("480x360")
        sWin.title("Settings")
        
        # GPIB Settings
        GPIB_Label = tk.Label(sWin, text="GPIB")
        GPIB_Label.place(x=90, y=15)
        
        Lockin_Label = tk.Label(sWin, text="Lock In")
        Lockin_Label.place(x=15, y=35)
        
        SignalGen_Label = tk.Label(sWin, text="Signal Gen")
        SignalGen_Label.place(x=15, y=75)
        
        self.Lockin_GPIB = tk.Entry(sWin, width=5)
        self.Lockin_GPIB.insert(0, self.config["Instrument Settings"]["Lock-in GPIB"])
        self.Lockin_GPIB.place(anchor="nw", x=90, y=35)
        
        self.SignalGen_GPIB = tk.Entry(sWin, width=5)
        self.SignalGen_GPIB.insert(0, self.config["Instrument Settings"]["Signal-Gen GPIB"])
        self.SignalGen_GPIB.place(anchor="nw", x=90, y=75)
        
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
        self.Save_Folder.place(anchor="nw", x=90, y=120)
        
        Lockin_Label = tk.Label(sWin, text="Save Folder")
        Lockin_Label.place(x=15, y=120)
        
        # TF Name
        self.TF_savename = tk.Entry(sWin, width=12)
        self.TF_savename.insert(0, self.config["Monitor Save Settings"]["Tuning Fork Name"])
        self.TF_savename.place(anchor="nw", x=90, y=150)
        
        Lockin_Label = tk.Label(sWin, text="TF Name")
        Lockin_Label.place(x=15, y=150)
        
        next_fit_name = self.TFdata.getfilename(self.TFdata.save_directory, "{}_fits_{}".format(self.TFdata.TF_name, self.TFdata.today)).replace(self.TFdata.current_working_dir,'')
        
        self.fit_Label = tk.Label(sWin, text="Next Fit File:        "+next_fit_name)
        self.fit_Label.place(x=15, y=180)
        
        self.sweep_label = tk.Label(sWin, text="Current Sweep Folder: "+"\data\{}\sweeps_{}".format(self.config["Monitor Save Settings"]["Save Folder"], self.TFdata.today))
        self.sweep_label.place(x=15, y=210)

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
            
    

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)
        
    def update_sweep_params(self):
        for idx, (key, val) in enumerate(self.params.items()):
            try:
                if self.entry_list[idx].get() != '':
                    self.params[key] = int(self.entry_list[idx].get())
                    self.updateConfig('Frequency Sweep Settings', key, self.entry_list[idx].get())
                    self.label_list[idx].config(text=key+": "+self.entry_list[idx].get())
                    self.entry_list[idx].delete(0, 'end')
            except Exception as e:
                print(e)
    

    def _quit(self):
        self.update_idletasks()
        self.update()
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.TFdata.save_fits()
    
    def tracking(self):
        # TODO
        # Everything
        pass
    
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
        if np.asarray(self.TFdata.sweep).ndim > 1:
            self.ax.plot(np.asarray(self.TFdata.sweep)[:, 1], np.asarray(self.TFdata.sweep)[:, 2])
            self.ay.plot(np.asarray(self.TFdata.sweep)[:, 1], np.asarray(self.TFdata.sweep)[:, 3])
        self.ax.set_title("Frequency Sweep")
        self.ax.set_ylabel("I")
        self.ay.set_ylabel("I")
        self.ay.set_xlabel("f, hz")
        self.canvas.draw()
        
        
    def graph_fits(self):
        
        self.ax.clear()
        self.ay.clear()
        if self.TFdata.saved_fits.ndim > 1:
            self.ax.plot(self.TFdata.saved_fits[:, 0]-self.TFdata.timestamp_today, self.TFdata.saved_fits[:, 4])
            self.ay.plot(self.TFdata.saved_fits[:, 0]-self.TFdata.timestamp_today, self.TFdata.saved_fits[:, 2])
        if np.asarray(self.TFdata.fits).ndim > 1:
            self.ax.plot(np.asarray(self.TFdata.fits)[:, 0]-self.TFdata.timestamp_today, np.asarray(self.TFdata.fits)[:, 4])
            self.ay.plot(np.asarray(self.TFdata.fits)[:, 0]-self.TFdata.timestamp_today, np.asarray(self.TFdata.fits)[:, 2])
        self.ax.set_title("Fit Values")
        self.ax.set_ylabel("Width, hz")
        self.ay.set_ylabel("$f_0$, hz")
        self.ay.set_xlabel("time")
        self.canvas.draw()
        
        
    def sweep(self):
        self.TFdata.reset_sweep()
        frequencies = np.linspace(self.params["Start Frequency"], self.params["End Frequency"], self.params["Num Pts"])
        self.gen.Set_Frequency(self.params["Start Frequency"])
        self.after(3*self.wait_time)
        for idx, f in enumerate(frequencies):
            if self.run:
                self.gen.Set_Frequency(f)
                self.after( self.wait_time)
                Vx, Vy = self.lockin.Read_XY()
                self.TFdata.append_sweep([time.time(), f, Vx, Vy])
                if self.showGraph.get() == "Frequency Sweep":
                    self.graph_sweep()
                self.update_idletasks()
                self.update()

    def start(self):
        self.start_button.config(text="Stop", command=self.stop)
        # Main Loop
        self.run = True
        while self.run:
            try:
                self.sweep()
                self.TFdata.save_sweep()
                if self.fitBool.get():
                    self.TFdata.fit_sweep()
                    if self.showGraph.get() == "Fit Details":
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
        self.start_button.config(text="Start Sweep", command=self.start)
        self.run = False

        
if __name__ == "__main__":

    App = tkApp()        
    App.mainloop()
    