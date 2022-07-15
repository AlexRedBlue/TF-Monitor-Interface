# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 16:06:46 2021

@author: physics-svc-mkdata
"""

import pyvisa
import numpy as np

class AGILENT_MULTIMETER:
    def __init__(self, GPIB_ADDR):
        rm = pyvisa.ResourceManager()
        self.instr = rm.open_resource(GPIB_ADDR)
        self.ID = self.instr.query("*IDN?")
        
    def Print_ID(self):
        self.ID = self.instr.query("*IDN?")
        print(self.ID)
        return self.ID
    
    def Read_V(self):
        try:
            return float(self.instr.query("READ?"))
        except:
            return np.nan