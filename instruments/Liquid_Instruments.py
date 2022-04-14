# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 15:59:47 2022

@author: alexd
"""

import numpy as np
from pymoku import Moku
from pymoku.instruments import LockInAmp
from pymoku.instruments import WaveformGenerator

class MokuLab(Moku):
    def __init__(self, connection_type="name", connection_key="Moku"):
        super().__init__()
        self.connect_Moku(connection_type, connection_key)
        self.channel_dict = {}
        self.instrument_dict = {}
        
    def connect_Moku(self, connection_type, connection_key):
        if connection_type == "serial":
            serial = connection_key
            self.get_by_serial(serial)
        elif connection_type == "IP":
            ip = connection_key
            self.get_by_ip(ip)
        elif connection_type == "name":
            Name = connection_key
            self.get_by_name(Name)
        
    def enable_lockin(self, channel, override=False):
        try:
            if channel not in self.channel_dict.keys():
                self.instrument_dict["Lock-in Amplifier"] = MokuLockinAmplifier(self.deploy_or_connect(LockInAmp), channel)
                self.channel_dict[channel] = "Lock-in Amplifier"
            elif override:
                self.instrument_dict["Lock-in Amplifier"] = MokuLockinAmplifier(self.deploy_or_connect(LockInAmp), channel)
                self.instrument_dict[self.channel_dict[channel]].detach_instrument()
                print(self.channel_dict[channel], "detached")
                del self.instrument_dict[self.channel_dict[channel]]
                self.channel_dict[channel] = "Lock-in Amplifier"
            else:
                print("Channel Occupied by", self.channel_dict[channel])
                self.instrument_dict[self.channel_dict[channel]].detach_instrument()
                del self.instrument_dict[self.channel_dict[channel]]
                
        except Exception as e:
            print("Moku Lock-in was unable to be connected:", e)
            
    def enable_signal_gen(self, channel, override=False):
        try:
            if channel not in self.channel_dict.keys():
                self.instrument_dict["Waveform Generator"] = MokuSignalGenerator(self.deploy_or_connect(WaveformGenerator), channel)
                self.channel_dict[channel] = "Waveform Generator"
            elif override:
                self.instrument_dict["Waveform Generator"] = MokuSignalGenerator(self.deploy_or_connect(WaveformGenerator), channel)
                self.instrument_dict[self.channel_dict[channel]].detach_instrument()
                print(self.channel_dict[channel], "detached")
                del self.instrument_dict[self.channel_dict[channel]]
                self.channel_dict[channel] = "Waveform Generator"
                
            else:
                print("Channel Occupied by", self.channel_dict[channel])
                self.instrument_dict[self.channel_dict[channel]].detach_instrument()
                del self.instrument_dict[self.channel_dict[channel]]
        except Exception as e:
            print("Moku Waveform Generator was unable to be connected:", e)
            
            

class MokuLockinAmplifier:
    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel
        self.instrument.enable_input(self.channel)
        self.instrument.set_frontend()
        
    def change_channel(self, new_channel):
        self.channel = new_channel
    
    def detach_instrument(self):
        self.instrument.detach_instrument()
    
    def Set_Phase(self, phase):
        self.instrument.set_demodulation(phase=phase)
        
    def Read_XY(self):
        data = self.instrument.get_data()
        return float(data.ch1), float(data.ch2)
    
    def set_frontend(self):
        self.instrument.set_frontend(self.channel, fiftyr=True, atten=False, ac=True)



class MokuSignalGenerator:
    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel
        self.voltage = 0
        self.frequency = 0
    
    def change_channel(self, new_channel):
        self.channel = new_channel
        
    def detach_instrument(self):
        self.instrument.detach_instrument()
        
    def Set_Voltage(self, V):
        self.voltage = V*np.sqrt(2)
    
    def Set_Frequency(self, f):
        self.frequency = f
        self.sin_wave()
    
    def sin_wave(self):
        self.instrument.gen_sinewave(self.channel, self.voltage, self.frequency)
        
if __name__ == "__main__":
    
    test_moku = MokuLab("IP", "192.168.1.1")
    print(test_moku.get_serial())
        
    
    
        
        
        