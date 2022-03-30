# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 11:51:12 2021

@author: physics-svc-mkdata
"""

import pyvisa

class PRT_73:
    def __init__(self, GPIB_ADDR):
        rm = pyvisa.ResourceManager()
        self.instr = rm.open_resource(GPIB_ADDR)
        self.ID = self.instr.query("ID")
        
    def Read_Ratio(self):
        return float(self.instr.query("Ratio")[7:])
    
    def Set_Ratio(self, ratio):
        if ratio >=0 and ratio <= 1:
            self.instr.query("Ratio {:f}".format(ratio))
        else:
            raise(ValueError("Ratio out of bounds"))
        
            
        