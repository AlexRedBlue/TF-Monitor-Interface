# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 00:52:00 2022

@author: alexd
"""

import pyvisa

class AGILENT_SIGNAL_GEN():
    def __init__(self, GPIB_ADDR):
        rm = pyvisa.ResourceManager()
        self.instr = rm.open_resource(GPIB_ADDR)
        self.ID = self.instr.query("*IDN?")
    
    def Print_ID(self):
        self.ID = self.instr.query("*IDN?")
        print(self.ID)
        return self.ID
    
    def Get_Waveform(self):
        return self.instr.query("SOUR1:APPL?")
    
    def Set_Waveform(self,freq,amplitude,function="SIN",DCOffset="0"):
        command_str = "SOUR1:APPL:{} {:.4f},{:.3f},{:.2f}".format(function,freq,amplitude,DCOffset)
        self.instr.write(command_str)
        
    def Get_Voltage(self):
        return float(self.instr.query("SOUR1:VOLT?"))
    
    def Set_Voltage(self,voltage):
        # Vrms used is 1/2 the peak to peak, so we divide by 2
        command_str = "SOUR1:VOLT {:.4f} VRMS".format(voltage/2)
        self.instr.write(command_str)
        
    def Get_Frequency(self):
        return float(self.instr.query("SOUR1:FREQ?"))
    
    def Set_Frequency(self,freq):
        command_str = "SOUR1:FREQ {:.4f} HZ".format(freq)
        self.instr.write(command_str)

class test_gen:
    def __init__(self, GPIB):
        self.ID = "Tester Signal Gen"
        self.Voltage = 1
        self.frequency = 1
        
    def Set_Voltage(self,voltage):
        self.Voltage = voltage
        
    def Set_Frequency(self,freq):
        self.frequency = freq