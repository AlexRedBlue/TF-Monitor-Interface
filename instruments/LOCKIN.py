# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 15:54:07 2021

@author: physics-svc-mkdata
"""
import pyvisa
import time
import numpy as np

def invert_dict(dict_in):
    return {v:k for k,v in dict_in.items()}

class SR830:
    
    ID = ''
    ref_dict = {0:"External",1:"Internal"}
    trigger_dict = {0:"Sine",1:"TTL Rising Edge",2:"TTL Falling Edge"}
    input_dict = {0:"A",1:"A-B",2:"I (1 MOhm)",3:"I (100 MOhm)"}
    ground_dict = {0:"Float",1:"Ground"}
    coupling_dict = {0:"AC",1:"DC"}
    notch_dict = {0:"None",1:"Line",2:"2xLine",3:"Both"}
    sens_dict = {0:"2 nV",1:"5 nV",2:"10 nV",3:"20 nV",4:"50 nV",5:"100 nV",
                 6:"200 nV",7:"500 nV",8:"1 uV",9:"2 uV",10:"5 uV",11:"10 uV",
                 12:"20 uV",13:"50 uV",14:"100 uV",15:"200 uV",16:"500 uV",
                 17:"1 mV",18:"2 mV",19:"5 mV",20:"10 mV",21:"20 mV",22:"50 mV",
                 23:"100 mV",24:"200 mV",25:"500 mV",26:"1 V"}
    sens_dict_inv = {v: k for k, v in sens_dict.items()}
    current_sens_dict = {1:"5 fA",2:"10 fA",3:"20 fA",4:"50 fA",5:"100 fA",
                        6:"200 fA",7:"500 fA",8:"1 pA",9:"2 pA",10:"5 pA",
                        11:"10 pA",12:"20 pA",13:"50 pA",14:"100 pA",15:"200 pA",
                        16:"500 pA",17:"1 nA",18:"2 nA",19:"5 nA",20:"10 nA",
                        21:"20 nA",22:"50 nA",23:"100 nA",24:"200 nA",25:"500 nA",
                        26:"1 uA"}
    current_sens_dict_inv = invert_dict(current_sens_dict)
    time_const_dict = {0:"10 us",1:"30 us",2:"100 us",3:"300 us",4:"1 ms",5:"3 ms",
                       6:"10 ms",7:"30 ms",8:"100 ms",9:"300 ms",10:"1 s",11:"3 s",
                       12:"10 s",13:"30 s",14:"100 s",15:"300 s",16:"1 ks",17:"3 ks",
                       18:"10 ks",19:"30 ks"}
    time_const_dict_inv = {v: k for k, v in time_const_dict.items()}
    reserve_dict = {0:"High Reserve",1:"Normal",2:"Low Noise"}
    filter_slope_dict = {0:"6dB/oct",1:"12dB/oct",2:"18dB/oct",3:"24dB/oct"}
    
    
    def __init__(self, GPIB_Addr):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(GPIB_Addr)
        # self.inst.read_termination ='\n'
        # self.inst.write_termination ='\n'
        # self.ID = self.inst.query("*IDN?")
        # self.sens = self.Get_Sensitivity()
        self.Reset_Buffer()
        
    def Read_XYRT(self):
        return [float(s) for s in self.inst.query('SNAP? 1,2,3,4').split(",")]
    
    def Read_XY(self):
        return [float(s) for s in self.inst.query('SNAP? 1,2').rstrip().split(",")]
    
    def Get_Sens_Dict(self):
        mode = int(self.inst.query("ISRC?"))
        if mode in [0,1]:
            return self.sens_dict
        elif mode in [2,3]:
            return self.current_sens_dict
    
    def Get_Sensitivity(self):
        mode = int(self.inst.query("ISRC?"))
        if mode in [0,1]:
            return self.sens_dict[int(self.inst.query("SENS?").rstrip())]
        elif mode in [2,3]:
            return self.current_sens_dict[int(self.inst.query("SENS?").rstrip())]
    
    def Set_Sensitivity(self,sens):
        mode = int(self.inst.query("ISRC?"))
        if mode in [0,1]:
            return self.inst.write("SENS %d" % self.sens_dict_inv[sens])
        elif mode in [2,3]:
            return self.inst.write("SENS %d" % self.current_sens_dict_inv[sens])

    def Get_Time_Constant(self):
        return self.time_const_dict[int(self.inst.query("OFLT?"))]
    
    def Set_Time_Constant(self,time_const):
        self.inst.write("OFLT %d" % self.time_const_dict_inv[time_const])
    
    def Get_Phase(self):
        return float(self.inst.query("PHAS?").rstrip())
    
    def Set_Phase(self, phase):
        self.inst.write("PHAS {:.2f}".format(phase))
    
    def Get_Ref(self):
        return self.ref_dict[self.inst.query("FMOD?").rstrip()]
    
    def Get_Freq(self):
        return float(self.inst.query("FREQ?").rstrip())
    
    def Get_Trigger(self):
        return self.trigger_dict[self.inst.query("RSLP?").rstrip()]
    
    def Get_Harmonic(self):
        return int(self.inst.query("HARM?").rstrip())
    
    def Get_OutputVolt(self):
        return float(self.inst.query("SLVL?").rstrip())
    
    def Get_Input(self):
        return self.input_dict[self.inst.query("ISRC?").rstrip()]
    
    def Get_Ground(self):
        return self.ground_dict[self.inst.query("IGND?").rstrip()]
    
    def Get_Coupling(self):
        return self.coupling_dict[self.inst.query("ICPL?").rstrip()]
    
    def Get_NotchFilter(self):
        return self.notch_dict[self.inst.query("ILIN?").rstrip()]
            
    def Get_Reserve(self):
        return self.reserve_dict[self.inst.query("RMOD?").rstrip()]
    
    def Get_Filter_Slope(self):
        return self.filter_slope_dict[self.instr.query("OFSL?").rstrip()]
    
    def Reset_Buffer(self):
        self.inst.write("REST")
        
    def Increase_Sensitivity_Range(self):
        current_sens = self.Get_Sensitivity()
        sens_num = self.sens_dict_inv[current_sens]
        if sens_num < 26:
            self.Set_Sensitivity(self.sens_dict[sens_num+1])
            print("Increased sensitivity range to", self.Get_Sensitivity())
        else:
            print("At maximum sensitivity range", self.Get_Sensitivity())
        
    def Decrease_Sensitivity_Range(self):
        current_sens = self.Get_Sensitivity()
        sens_num = self.sens_dict_inv[current_sens]
        if sens_num > 0:
            self.Set_Sensitivity(self.sens_dict[sens_num-1])
            print("Decreased sensitivity range to", self.Get_Sensitivity())
        else:
            print("At minimum sensitivity range", self.Get_Sensitivity())
        
class SR844:
    ID = ''
    ref_dict = {0:"External",1:"Internal"}
    trigger_dict = {0:"Sine",1:"TTL Rising Edge",2:"TTL Falling Edge"}
    input_dict = {0:"A",1:"A-B",2:"I (1 MOhm)",3:"I (100 MOhm)"}
    ground_dict = {0:"Float",1:"Ground"}
    coupling_dict = {0:"AC",1:"DC"}
    notch_dict = {0:"None",1:"Line",2:"2xLine",3:"Both"}
    sens_dict = {0:"2 nV",1:"5 nV",2:"10 nV",3:"20 nV",4:"50 nV",5:"100 nV",
                 6:"200 nV",7:"500 nV",8:"1 uV",9:"2 uV",10:"5 uV",11:"10 uV",
                 12:"20 uV",13:"50 uV",14:"100 uV",15:"200 uV",16:"500 uV",
                 17:"1 mV",18:"2 mV",19:"5 mV",20:"10 mV",21:"20 mV",22:"50 mV",
                 23:"100 mV",24:"200 mV",25:"500 mV",26:"1 V"}
    sens_dict_inv = {v: k for k, v in sens_dict.items()}
    current_sens_dict = {1:"5 fA",2:"10 fA",3:"20 fA",4:"50 fA",5:"100 fA",
                        6:"200 fA",7:"500 fA",8:"1 pA",9:"2 pA",10:"5 pA",
                        11:"10 pA",12:"20 pA",13:"50 pA",14:"100 pA",15:"200 pA",
                        16:"500 pA",17:"1 nA",18:"2 nA",19:"5 nA",20:"10 nA",
                        21:"20 nA",22:"50 nA",23:"100 nA",24:"200 nA",25:"500 nA",
                        26:"1 uA"}
    current_sens_dict_inv = invert_dict(current_sens_dict)
    time_const_dict = {0:"10 us",1:"30 us",2:"100 us",3:"300 us",4:"1 ms",5:"3 ms",
                       6:"10 ms",7:"30 ms",8:"100 ms",9:"300 ms",10:"1 s",11:"3 s",
                       12:"10 s",13:"30 s",14:"100 s",15:"300 s",16:"1 ks",17:"3 ks",
                       18:"10 ks",19:"30 ks"}
    time_const_dict_inv = {v: k for k, v in time_const_dict.items()}
    reserve_dict = {0:"High Reserve",1:"Normal",2:"Low Noise"}
    filter_slope_dict = {0:"6dB/oct",1:"12dB/oct",2:"18dB/oct",3:"24dB/oct"} 
    
    def __init__(self,GPIB_Addr):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(GPIB_Addr)
        self.ID = self.inst.query("*IDN?")
        self.sens = self.sens_dict[int(self.inst.query("SENS?").rstrip())]
        
    def Read_XYRT(self):
        return [float(s) for s in self.inst.query('SNAP? 1,2,3,4').split(",")]
    
    def Read_XY(self):
        return [float(s) for s in self.inst.query('SNAP? 1,2').rstrip().split(",")]
    
    def Get_Sens_Dict(self):
        mode = int(self.instr.query("ISRC?"))
        if mode in [0,1]:
            return self.sens_dict
        elif mode in [2,3]:
            return self.current_sens_dict
    
    def Get_Sensitivity(self):
        mode = int(self.inst.query("ISRC?"))
        if mode in [0,1]:
            return self.sens_dict[int(self.inst.query("SENS?").rstrip())]
        elif mode in [2,3]:
            return self.current_sens_dict[int(self.inst.query("SENS?").rstrip())]
    
    def Set_Sensitivity(self,sens):
        mode = int(self.inst.query("ISRC?"))
        if mode in [0,1]:
            return self.inst.write("SENS %d" % self.sens_dict_inv[sens])
        elif mode in [2,3]:
            return self.inst.write("SENS %d" % self.current_sens_dict_inv[sens])
        
    
    def Get_Time_Constant(self):
        return self.time_const_dict[int(self.inst.query("OFLT?"))]
    
    def Set_Time_Constant(self,time_const):
        self.inst.write("OFLT %d" % self.time_const_dict_inv[time_const])
    
    def Get_Phase(self):
        return float(self.inst.query("PHAS?").rstrip())
    
    def Get_Ref(self):
        return self.ref_dict[self.inst.query("FMOD?").rstrip()]
    
    def Get_Freq(self):
        return float(self.inst.query("FREQ?").rstrip())
    
    def Get_Trigger(self):
        return self.trigger_dict[self.inst.query("RSLP?").rstrip()]
    
    def Get_Harmonic(self):
        return int(self.inst.query("HARM?").rstrip())
    
    def Get_OutputVolt(self):
        return float(self.inst.query("SLVL?").rstrip())
    
    def Get_Input(self):
        return self.input_dict[self.inst.query("ISRC?").rstrip()]
    
    def Get_Ground(self):
        return self.ground_dict[self.inst.query("IGND?").rstrip()]
    
    def Get_Coupling(self):
        return self.coupling_dict[self.inst.query("ICPL?").rstrip()]
    
    def Get_NotchFilter(self):
        return self.notch_dict[self.inst.query("ILIN?").rstrip()]
            
    def Get_Reserve(self):
        return self.reserve_dict[self.inst.query("RMOD?").rstrip()]
    
    def Get_Filter_Slope(self):
        return self.filter_slope_dict[self.instr.query("OFSL?").rstrip()]

# Probably has bugs for SR850
class SR850:
    ID = ''
    ref_dict = {0:"External",1:"Internal"}
    trigger_dict = {0:"Sine",1:"TTL Rising Edge",2:"TTL Falling Edge"}
    input_dict = {0:"A",1:"A-B",2:"I (1 MOhm)",3:"I (100 MOhm)"}
    ground_dict = {0:"Float",1:"Ground"}
    coupling_dict = {0:"AC",1:"DC"}
    notch_dict = {0:"None",1:"Line",2:"2xLine",3:"Both"}
    sens_dict = {0:"2 nV",1:"5 nV",2:"10 nV",3:"20 nV",4:"50 nV",5:"100 nV",
                 6:"200 nV",7:"500 nV",8:"1 uV",9:"2 uV",10:"5 uV",11:"10 uV",
                 12:"20 uV",13:"50 uV",14:"100 uV",15:"200 uV",16:"500 uV",
                 17:"1 mV",18:"2 mV",19:"5 mV",20:"10 mV",21:"20 mV",22:"50 mV",
                 23:"100 mV",24:"200 mV",25:"500 mV",26:"1 V"}
    sens_dict_inv = {v: k for k, v in sens_dict.items()}
    current_sens_dict = {1:"5fA",2:"10fA",3:"20fA",4:"50fA",5:"100fA",
                        6:"200fA",7:"500fA",8:"1pA",9:"2pA",10:"5pA",
                        11:"10pA",12:"20pA",13:"50pA",14:"100pA",15:"200pA",
                        16:"500pA",17:"1nA",18:"2nA",19:"5nA",20:"10nA",
                        21:"20nA",22:"50nA",23:"100nA",24:"200nA",25:"500nA",
                        26:"1uA"}
    current_sens_dict_inv = invert_dict(current_sens_dict)
    time_const_dict = {0:"10 us",1:"30 us",2:"100 us",3:"300 us",4:"1 ms",5:"3 ms",
                       6:"10 ms",7:"30 ms",8:"100 ms",9:"300 ms",10:"1 s",11:"3 s",
                       12:"10 s",13:"30 s",14:"100 s",15:"300 s",16:"1 ks",17:"3 ks",
                       18:"10 ks",19:"30 ks"}
    time_const_dict_inv = {v: k for k, v in time_const_dict.items()}
    reserve_dict = {0:"High Reserve",1:"Normal",2:"Low Noise"}
    filter_slope_dict = {0:"6dB/oct",1:"12dB/oct",2:"18dB/oct",3:"24dB/oct"} 
    def __init__(self,GPIB_Addr):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(GPIB_Addr)
        self.inst.read_termination ='\n'
        self.inst.write_termination ='\n'
        self.ID = self.inst.query("*IDN?")
        self.sens = self.sens_dict[int(self.inst.query("SENS?").rstrip())]
        
    def Read_XYRT(self):
        return [float(s) for s in self.inst.query('SNAP? 1,2,3,4').split(",")]
    
    def Read_XY(self):
        return [float(s) for s in self.inst.query('SNAP? 1,2').rstrip().split(",")]
    
    def Get_Sensitivity(self):
        mode = int(self.instr.query("ISRC?"))
        if mode in [0,1]:
            return self.sens_dict[int(self.inst.query("SENS?").rstrip())]
        elif mode in [2,3]:
            return self.current_sens_dict[int(self.inst.query("SENS?").rstrip())]
    
    def Set_Sensitivity(self,sens):
        mode = int(self.instr.query("ISRC?"))
        if mode in [0,1]:
            return self.inst.write("SENS %d" % self.sens_dict_inv[sens])
        elif mode in [2,3]:
            return self.inst.write("SENS %d" % self.current_sens_dict_inv[sens])
    
    def Get_Time_Constant(self):
        return self.time_const_dict[int(self.inst.query("OFLT?"))]
    
    def Set_Time_Constant(self,time_const):
        self.inst.write("OFLT %d" % self.time_const_dict_inv[time_const])
    
    def Get_Phase(self):
        return float(self.inst.query("PHAS?").rstrip())
    
    def Get_Ref(self):
        return self.ref_dict[self.inst.query("FMOD?").rstrip()]
    
    def Get_Freq(self):
        return float(self.inst.query("FREQ?").rstrip())
    
    def Get_Trigger(self):
        return self.trigger_dict[self.inst.query("RSLP?").rstrip()]
    
    def Get_Harmonic(self):
        return int(self.inst.query("HARM?").rstrip())
    
    def Get_OutputVolt(self):
        return float(self.inst.query("SLVL?").rstrip())
    
    def Get_Input(self):
        return self.input_dict[self.inst.query("ISRC?").rstrip()]
    
    def Get_Ground(self):
        return self.ground_dict[self.inst.query("IGND?").rstrip()]
    
    def Get_Coupling(self):
        return self.coupling_dict[self.inst.query("ICPL?").rstrip()]
    
    def Get_NotchFilter(self):
        return self.notch_dict[self.inst.query("ILIN?").rstrip()]
            
    def Get_Reserve(self):
        return self.reserve_dict[self.inst.query("RMOD?").rstrip()]
    
    def Get_Filter_Slope(self):
        return self.filter_slope_dict[self.instr.query("OFSL?").rstrip()]
    
    
class LI5640:
    def invert_dict(dict_in):
        return {v:k for k,v in dict_in.items()}
    
    source_dict = {0:"REF IN",1:"INT OSC",2:"SIGNAL"}
    source_dict_inv = {v : k for k,v in source_dict.items()} 
    edge_dict = {0:"SINE POS",1:"TTL POS",2:"TTL NEG"}
    edge_dict_inv = {v : k for k,v in edge_dict.items()}
    signal_dict = {0:"A",1:"A-B",2:"IE6",3:"IE8"}
    signal_dict_inv = {v:k for k,v in signal_dict.items()}
    coupling_dict = {0:"AC",1:"DC"}
    coupling_dict_inv = {v:k for k,v in coupling_dict.items()}
    ground_dict = {0:"FLOAT",1:"GROUND"}
    ground_dict_inv = {v:k for k,v in ground_dict.items()}
    sens_dict = {0:"2 nV",1:"5 nV",2:"10 nV",3:"20 nV",4:"50 nV",
                        5:"100 nV",6:"200 nV",7:"500 nV",8:"1 uV",9:"2 uV",10:"5 uV",
                        11:"10 uV",12:"20 uV",13:"50 uV",14:"100 uV",15:"200 uV",
                        16:"500 uV",17:"1 mV",18:"2 mV",19:"5 mV",20:"10 mV",
                        21:"20 mV",22:"50 mV",23:"100 mV",24:"200 mV",25:"500 mV",
                        26:"1 V"}
    sens_dict_inv = invert_dict(sens_dict)
    current_sens_dict = {1:"5 fA",2:"10 fA",3:"20 fA",4:"50 fA",5:"100 fA",
                        6:"200 fA",7:"500 fA",8:"1 pA",9:"2 pA",10:"5 pA",
                        11:"10 pA",12:"20 pA",13:"50 pA",14:"100 pA",15:"200 pA",
                        16:"500 pA",17:"1 nA",18:"2 nA",19:"5 nA",20:"10 nA",
                        21:"20 nA",22:"50 nA",23:"100 nA",24:"200 nA",25:"500 nA",
                        26:"1 uA"}
    current_sens_dict_inv = invert_dict(current_sens_dict)
    time_const_dict = {0:"10 us",1:"30 us",2:"100 us",3:"300 us",4:"1 ms",5:"3 ms",
                       6:"10 ms",7:"30 ms",8:"100 ms",9:"300 ms",10:"1 s",
                       11:"3 s",12:"10 s",13:"30 s",14:"100 s",15:"300 s",
                       16:"1 ks",17:"3 ks",18:"10 ks",19:"30 ks"}
    time_const_dict_inv = invert_dict(time_const_dict)
    DSMP_dict = {0:"Trigger",
                 1:"0.0625 ms",2:"0.125 ms",3:"0.250 ms", 4:"0.500 ms", 5:"1 ms", 
                 6:"2 ms", 7:"5 ms", 8:"10 ms", 9:"20 ms", 10:"50 ms", 11:"100 ms", 
                 12:"200 ms", 13:"500 ms", 14:"1 s", 15:"2 s", 16: "5 s", 17:"10 s", 18:"20 s"}
    
    
    def __init__(self, GPIB_ADDR):
        rm = pyvisa.ResourceManager()
        self.instr = rm.open_resource(GPIB_ADDR)
        # self.instr.read_termination ='\n'
        # self.instr.write_termination ='\n'
        self.ID = self.instr.query("*IDN?")
        self.sens = self.Get_Sensitivity()
    
    def Get_Sens_Dict(self):
        mode = int(self.instr.query("ISRC?"))
        if mode in [0,1]:
            return self.sens_dict
        elif mode in [2,3]:
            return self.current_sens_dict
        
    def Get_Phase(self):
        return float(self.instr.query("PHAS?").rstrip())
    
    def Set_Phase(self,phase_deg):
        self.instr.write("PHAS {:.2f}".format(phase_deg))
    
    def Auto_Phase(self):
        self.instr.write("APHS")
    
    def Get_Osc_Frequency(self):
        return float(self.instr.query("FREQ?").rstrip())
    
    def Set_Osc_Frequency(self, Freq_Hz):
        self.instr.write("FREQ {:.4f}".format(Freq_Hz))
    
    def Get_Osc_Amplitude(self):
        return float(self.instr.query("AMPTD?").rstrip())
    
    def Set_Osc_Amplitude(self,amplitude_V):
        self.instr.write("AMPTD {:.4f}".format(amplitude_V))
    
    def Get_Harmonic(self):
        return int(self.instr.query("HARM?").rstrip())
    
    def Set_Harmonic(self, harm_int):
        self.instr.write("HARM {:d}".format(harm_int))
    
    def Get_Source(self):
        return self.source_dict[int(self.instr.query("RSRC?").rstrip())]
    
    def Set_Source(self,source_str = "REF IN"):
        try:
            self.instr.write("RSRC {:d}".format(self.source_dict_inv[source_str]))
        except:
            self.Set_Source(input('Please enter "REF IN", "OSC OUT" or "SIGNAL": '))
            
    def Get_Edge(self):
        return self.edge_dict[int(self.instr.query("REDG?").rstrip())]
    
    def Set_Edge(self,edge_str = "SINE POS"):
        try:
            self.instr.write("REDG {:d}".format(self.edge_dict_inv[edge_str]))
        except:
            self.Set_Edge(input('Please enter "SINE POS", "TTL POS" or "TTL NEG"'))
    
    def Get_Signal_Input(self):
        return self.signal_dict[int(self.instr.query("ISRC?").rstrip())]
    
    def Set_Signal_Input(self,input_str):
        try:
            self.instr.write("ISRC {:d}".format(self.signal_dict_inv[input_str]))
        except:
            self.Set_Signal_Input(input('Please enter A, A-B, IE6 or IE8: '))
    
    def Get_Input_Coupling(self):
        return self.coupling_dict[int(self.instr.query("ICPL?").rstrip())]
    
    def Set_Input_Coupling(self,coupling_str):
        try:
            self.instr.write("ICPL {:d}".format(self.coupling_dict_inv[coupling_str]))
        except:
            self.Set_Input_Coupling(input('Please enter "AC" or "DC"'))
    
    def Get_Ground(self):
        return self.ground_dict[int(self.instr.query("IGND?").rstrip())]
    
    def Set_Ground(self,ground_str):
        try:
            self.instr.write("IGND {:d}".format(self.ground_dict_inv[ground_str]))
        except:
            self.Set_Ground(input('Please enter "FLOAT" or "GROUND"'))
    
    def Get_Sensitivity(self):
        mode = int(self.instr.query("ISRC?"))
        if mode in [0,1]:
            return self.sens_dict[int(self.instr.query("VSEN?").rstrip())]
        elif mode in [2,3]:
            return self.current_sens_dict[int(self.instr.query("ISEN?").rstrip())]
    
    def Set_Sensitivity(self,sens):
        mode = int(self.instr.query("ISRC?"))
        if mode in [0,1]:
            return self.instr.write("VSEN %d" % self.sens_dict_inv[sens])
        elif mode in [2,3]:
            return self.instr.write("ISEN %d" % self.current_sens_dict_inv[sens])
    
    def Auto_Sensitivity(self):
        self.instr.write("ASEN")
    
    def Get_Time_Constant(self):
        return self.time_const_dict[int(self.instr.query("TCON?").rstrip())]
    
    def Set_Time_Constant(self, time_const):
        self.instr.write("TCON %d" % self.time_const_dict_inv[time_const])
    
    def Set_Data_Read_XY(self):
        self.instr.write("OTYP 1,2")
    
    def Read_XY_Raw(self):
        return self.instr.query("DOUT?")
    
    def Read_XY(self):
        data_str = (self.instr.query("DOUT?").rstrip()).split(",")
        Vx = float(data_str[0])
        Vy = float(data_str[1])
        return Vx, Vy
    
    def Set_Data_Memory_Type(self, num):
        DMT_dict = {0:"DATA1",1:"DATA2",2:"DATA1, DATA2",3:"DATA2, AUX IN2",4:"DATA1, DATA2, FREQ",5:"DATA1, DATA2, AUX IN1, AUX IN2"}
        self.instr.write("DTYP {:d}".format(num))
        print(DMT_dict[num])
    
    def Set_DSMP(self, num):
        self.instr.write("DSMP {:d}".format(num))
        print(self.DSMP_dict[int(self.instr.query("DSMP?"))])
        
    def Set_Memory_Size(self, num):
        self.instr.write("DSIZ {:d}".format(num))
        print("Memory Size: {} K".format(2**(num+1)))
        
    def Set_Trigger(self, num):
        # 0 Enable, 1 Disable
        self.instr.write("TENB {:d}".format(num))
        
    def Store_Data(self, wait):
        self.instr.write("STRT")
        self.instr.write("*TRG")
        time.sleep(wait)
        self.instr.write("STOP")
        
    def Get_Stored_Data(self):
        pts = int(self.instr.query("SPTS?"))
        print(pts)
        if pts != 0:
            data = []
            self.instr.write("DASC? 0,{:d}".format(pts))
            for i in range(pts-1):
                row = self.instr.read_ascii_values(container=np.array)
                data.append(row)
            # data = self.instr.query_binary_values("DBIN? 0,{:d}".format(pts), header_fmt='empty', datatype='f', data_points=pts)
            return np.array(data, dtype=float)
        else:
            return 0
  


class test_lockin:
    sens_dict = {1:"5 fA",2:"10 fA",3:"20 fA",4:"50 fA",5:"100 fA",
                        6:"200 fA",7:"500 fA",8:"1 pA",9:"2 pA",10:"5 pA",
                        11:"10 pA",12:"20 pA",13:"50 pA",14:"100 pA",15:"200 pA",
                        16:"500 pA",17:"1 nA",18:"2 nA",19:"5 nA",20:"10 nA",
                        21:"20 nA",22:"50 nA",23:"100 nA",24:"200 nA",25:"500 nA",
                        26:"1 uA"}
    sens_dict_inv = invert_dict(sens_dict)
    time_const_dict = {0:"10 us",1:"30 us",2:"100 us",3:"300 us",4:"1 ms",5:"3 ms",
                       6:"10 ms",7:"30 ms",8:"100 ms",9:"300 ms",10:"1 s",
                       11:"3 s",12:"10 s",13:"30 s",14:"100 s",15:"300 s",
                       16:"1 ks",17:"3 ks",18:"10 ks",19:"30 ks"}
    time_const_dict_inv = invert_dict(time_const_dict)
    
    def __init__(self, GPIB_ADDR):
        self.ID = "Test Lock-in"
        self.phase = 0
        self.drive = 1
        self.sensitivity = 1
        self.cycle = 0
    
    def Read_XY(self):
        Vx = self.cycle*np.cos(self.phase)
        Vy = self.cycle*np.sin(self.phase)
        if self.cycle < 10:
            self.cycle += 1
        else:
            self.cycle = 0
        return Vx, Vy
    
    def Get_Sens_Dict(self):
        return self.sens_dict

    def Set_Voltage(self, V):
        self.drive = V
    
    def Get_Sensitivity(self):
        return self.sens_dict[10]
    
    def Get_Time_Constant(self):
        return self.time_const_dict[10]
    
    def Set_Phase(self, phase_deg):
        self.phase = phase_deg
    