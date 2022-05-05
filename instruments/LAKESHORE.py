# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 15:36:36 2021

@author: physics-svc-mkdata
"""

import pyvisa
import time
import matplotlib.pyplot as plt

# TODO
# ADD MORE QUERY METHODS
# ADD DICT
# ADD MULTI-CHANNEL READS

class LS370:
    
    ID = ''
    
    def __init__(self,GPIB_Addr):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(GPIB_Addr)
        # self.inst.read_termination ='\r\n'
        # self.inst.write_termination ='\r\n'
        self.ID = self.inst.query("*IDN?")
        # self.sens = self.sens_dict[int(self.inst.query("SENS?").rstrip())]
        
    def Read_R(self, channel=1):
        return float(self.inst.query("RDGR? "+str(channel)).rstrip())
        
    def Ask_Scan_Channel(self):
        return float(self.inst.query("SCAN?").rstrip())
        
    def Autoscan(self, channels=[1], wait_time=5):
        measurements = []
        for idx, channel in enumerate(channels):
            self.inst.write("SCAN {:d},0".format(channel))
            # plt.pause(wait_time)
            measurements.append([channel, self.Read_R(channel)])
        return measurements
        
    def Scan(self, channel=1):
        self.inst.write("SCAN "+str(channel))
        
    def Ask_Heater_Range(self, channel):
        return float(self.inst.query("HTRRNG?").rstrip())
    
    def Ask_Heater_Output(self, channel):
        return float(self.inst.query("HTR?").rstrip())
        
class LS336:
    
    ID = ''
    
    def __init__(self, GPIB_Addr):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(GPIB_Addr)
        # self.inst.read_termination ='\r\n'
        # self.inst.write_termination ='\r\n'
        self.ID = self.inst.query("*IDN?")
        # self.sens = self.sens_dict[int(self.inst.query("SENS?").rstrip())]
        
    def Read_R(self, channel=1):
        return float(self.inst.query("RDGR? "+str(channel)).rstrip())
        
    def Ask_Scan_Channel(self):
        return float(self.inst.query("SCAN?").rstrip())
        
    def Autoscan(self, channels=[1], wait_time=5):
        measurements = []
        for idx, channel in enumerate(channels):
            self.inst.write("SCAN {:d},0".format(channel))
            # plt.pause(wait_time)
            measurements.append([channel, self.Read_R(channel)])
        return measurements
        
    def Scan(self, channel=1):
        self.inst.write("SCAN "+str(channel))
        
    def Ask_Heater_Range(self, channel):
        return float(self.inst.query("HTRRNG?").rstrip())
    
    def Ask_Heater_Output(self, channel):
        return float(self.inst.query("HTR?").rstrip())
        
