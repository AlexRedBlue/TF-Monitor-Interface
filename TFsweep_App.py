# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:24:27 2022

@author: physics-svc-mkdata
"""

import tkinter as tk

from instruments import LOCKIN
from instruments import AGILENT_SIGNAL_GEN

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import configparser
import os

import time

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

class tkApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.config = configparser.RawConfigParser()
        
        if not os.path.exists('sweepConfig.cfg'):
            self.initConfig()
            
        # Read configurations using section and key to get the value
        self.config.read('sweepConfig.cfg')
        
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
        
        self.top = tk.Frame(self)
        self.bottom2 = tk.Frame(self)
        self.bottom1 = tk.Frame(self)
        self.top.pack(side=tk.TOP)
        self.bottom2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.bottom1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(2,1,1)
        self.ay = self.fig.add_subplot(2,1,2)
        
        
        self.data = []
        self.params = {
                        "Num Pts": int(self.config["Frequency Sweep Settings"]["Num Pts"]),
                        "End Frequency": float(self.config["Frequency Sweep Settings"]["End Frequency"]),
                        "Start Frequency": float(self.config["Frequency Sweep Settings"]["Start Frequency"])
                      }
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(in_=self.top, fill=tk.BOTH, expand=1)
        
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        
        # self.quit_button = tk.Button(master=self, text="Quit", command=self._quit)
        # self.quit_button.pack(in_=self.bottom2, side=tk.LEFT)
        
        self.start_button = tk.Button(master=self, text="Start", command=self.start_sweep)
        self.start_button.pack(in_=self.bottom2, side=tk.LEFT, padx=5, pady=5)
        
        self.save_button = tk.Button(master=self, text="Save Sweep", command=self.save_sweep)
        self.save_button.pack(in_=self.bottom2, side=tk.LEFT)
        self.save_label = tk.Label(text=self.config["Frequency Sweep Settings"]["Save Directory"])
        self.save_label.pack(in_=self.bottom2, side=tk.LEFT, padx=5)
        
        # labels & Text Boxes
        self.label_list = []
        self.entry_list = []
        for idx, (key, val) in enumerate(self.params.items()):
            
            self.label_list.append(tk.Label(self.top, text = key+" "+str(val)))
            self.label_list[-1].pack(in_=self.top,side=tk.RIGHT)
            
            self.entry_list.append(tk.Entry(self.top))
            self.entry_list[-1].pack(in_=self.top, side=tk.RIGHT)

        
        self.update_button = tk.Button(master=self, text="Update Params", command=self.update_sweep_params)
        self.update_button.pack(in_=self.bottom2, side=tk.RIGHT)
        
        self.fit_button = tk.Button(master=self, text="Fit", command=self.fitSweep)
        self.fit_label = tk.Label(master=self, text='')
        self.fit_label.pack(in_=self.bottom1, side=tk.LEFT, padx=5, pady=5)
        
        self.settings_button = tk.Button(master=self, text="Settings", command=self.settingsWindow)
        self.settings_button.pack(in_=self.bottom2, side=tk.RIGHT, padx=5, pady=5)

    def initConfig(self):
        self.config.add_section('Frequency Sweep Settings')
        self.config.set('Frequency Sweep Settings', 'Start Frequency', '32700')
        self.config.set('Frequency Sweep Settings', 'End Frequency', '32900')
        self.config.set('Frequency Sweep Settings', 'Num Pts', '100')
        self.config.set('Frequency Sweep Settings', 'Save Directory', r"C:\Users\physics-svc-mkdata\Documents\Data\TuningForkThermometer")
        
        self.config.add_section("Instrument Settings")
        self.config.set("Instrument Settings", "Lock-in Model", "LI 5640")
        self.config.set("Instrument Settings", "Lock-in GPIB", "25")
        self.config.set("Instrument Settings", "Signal-Gen Model", "Keysight")
        self.config.set("Instrument Settings", "Signal-Gen GPIB", "24")
        
        with open('sweepConfig.cfg', 'w') as output:
            self.config.write(output)
        

    
    def updateConfig(self, section, key, value):
    #Update config using section key and the value to change
    #call this when you want to update a value in configuation file
    # with some changes you can save many values in many sections
        self.config.set(section, key, value)
        with open('sweepConfig.cfg', 'w') as output:
            self.config.write(output)
            
    def settingsWindow(self):
        sWin = tk.Toplevel(self)
        sWin.geometry("480x360")
        sWin.title("Settings")
        
        GPIB_Label = tk.Label(sWin, text="GPIB")
        GPIB_Label.place(x=95, y=15)
        
        Lockin_Label = tk.Label(sWin, text="Lock In")
        Lockin_Label.place(x=15, y=35)
        
        self.SignalGen_Label = tk.Label(sWin, text="Signal Gen")
        self.SignalGen_Label.place(x=15, y=75)
        
        self.Lockin_GPIB = tk.Entry(sWin)
        self.Lockin_GPIB.insert(0, self.config["Instrument Settings"]["Lock-in GPIB"])
        self.Lockin_GPIB.place(anchor="nw", x=90, y=35)
        
        self.SignalGen_GPIB = tk.Entry(sWin)
        self.SignalGen_GPIB.insert(0, self.config["Instrument Settings"]["Signal-Gen GPIB"])
        self.SignalGen_GPIB.place(anchor="nw", x=90, y=75)
        
        self.Lockin_Model = tk.StringVar(sWin)
        self.Lockin_Model.set(self.config["Instrument Settings"]["Lock-in Model"]) # default value
        self.L_Model_Options = tk.OptionMenu(sWin, self.Lockin_Model, "LI 5640", "SR 830")
        self.L_Model_Options.place(anchor="nw", x=235, y=28)
        
        self.SignalGen_Model = tk.StringVar(sWin)
        self.SignalGen_Model.set(self.config["Instrument Settings"]["Signal-Gen Model"]) # default value
        self.SG_Model_Options = tk.OptionMenu(sWin, self.SignalGen_Model, "Keysight", "Agilent")
        self.SG_Model_Options.place(anchor="nw", x=235, y=68)

        save_button = tk.Button(sWin, text='Save', command=self.save_settings)
        save_button.place(anchor="sw", x=15, y=345)
        close_button = tk.Button(sWin, text='Quit', command=lambda:close_win(sWin))
        close_button.place(anchor="se", x=465, y=345)

        sWin.mainloop()
        
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
        if self.config["Instrument Settings"]["Signal-Gen Model"] == "Keysight":
            self.gen = AGILENT_SIGNAL_GEN.AGILENT_SIGNAL_GEN("GPIB0::"+self.config["Instrument Settings"]["Signal-Gen GPIB"]+"::INSTR")
        else:
            print("Invalid Signal-Gen Instrument Type: Reset Config File")
    

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)
        
    def update_sweep_params(self):
        for idx, (key, val) in enumerate(self.params.items()):
            try:
                if self.entry_list[idx].get() != '':
                    self.params[key] = int(self.entry_list[idx].get())
                    self.updateConfig('Frequency Sweep Settings', key, int(self.entry_list[idx].get()))
                    self.label_list[idx].config(text=key+": "+self.entry_list[idx].get())
                    self.entry_list[idx].delete(0, 'end')
            except Exception as e:
                print(e)
        self.mainloop()
    

    def _quit(self):
        self.update_idletasks()
        self.update()
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate    

    def start_sweep(self):
        self.start_button.config(text="Stop", command=self.stop)
        self.fit_label.forget()
        self.save_button.forget()
        self.save_label.forget()
        frequencies = np.linspace(self.params["Start Frequency"], self.params["End Frequency"], self.params["Num Pts"])
        self.gen.Set_Frequency(self.params["Start Frequency"])
        time.sleep(3)
        self.data = []
        x, y = [], []
        for idx, f in enumerate(frequencies):
            try:
                self.gen.Set_Frequency(f)
                time.sleep(1)
                Vx, Vy = self.lockin.Read_XY()
                x.append(Vx)
                y.append(Vy)
                self.data.append([time.time(), f, Vx, Vy])
                self.ax.clear()
                self.ay.clear()
                self.ax.plot(frequencies[:idx+1], x)
                self.ay.plot(frequencies[:idx+1], y)
                self.ax.set_title("Frequency Sweep")
                self.ax.set_ylabel("I")
                self.ay.set_ylabel("I")
                self.ay.set_xlabel("f, hz")
                self.canvas.draw()
                self.update_idletasks()
                self.update()
            except:
                pass
            
        self.save_button.pack(in_=self.bottom2, side=tk.LEFT)
        self.save_label.pack(in_=self.bottom2, side=tk.LEFT, padx=5)
        self.start_button.config(text="Start Sweep", command=self.start_sweep)
        self.fit_button.pack(in_=self.bottom1, side=tk.LEFT, padx=5, pady=5)
        self.fit_label.pack(in_=self.bottom1, side=tk.LEFT, padx=5, pady=5)
        self.mainloop()
        
    def stop(self):
        self.start_button.config(text="Start Sweep", command=self.start_sweep)
        self.mainloop()
        
    def fitSweep(self):
        guess = [(self.data[0][1] + self.data[-1][1])/2, 0, (-self.data[0][1] + self.data[-1][1])/5, 0, 0, 0, 0]
        fit_coeff, flags = LF.Lorentz_Fit_X_quad(np.asarray(self.data)[:,1],np.asarray(self.data)[:,2], guess)
        self.ax.plot(np.asarray(self.data)[:, 1], LF.Lorentz_x_quad(np.asarray(self.data)[:, 1], fit_coeff))
        # self.ay.plot(np.asarray(self.data)[:, 1], LF.Lorentz_y_quad(np.asarray(self.data)[:, 1], fit_coeff))
        self.canvas.draw()
        self.fit_label.config(text='f0: '+str(fit_coeff[0])+'   Width: '+str(fit_coeff[2]))
        self.fit_button.forget()
        self.mainloop()
        
    def save_sweep(self):
        file = tk.filedialog.asksaveasfile(initialdir=self.config["Frequency Sweep Settings"]["Save Directory"])
        if type(file) != None and self.data != []:
            np.savetxt(file.name, self.data, delimiter='\t', header='Time\tFreq\tX\tY')
            self.updateConfig("Frequency Sweep Settings", "Save Directory", file.name)
            self.save_label.config(text=file.name)
        file.close()
        self.mainloop()
        
        
        
if __name__ == "__main__":

    App = tkApp()        
    App.mainloop()
    
    