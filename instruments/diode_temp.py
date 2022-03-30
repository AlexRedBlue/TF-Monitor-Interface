# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 15:11:51 2020

@author: kgunther
"""
import numpy as np
from datetime import datetime
from instruments.AGILENT_MULTIMETER import AGILENT_MULTIMETER

A_212=[6.429274,-7.514262,-.725882,-1.117846,-.562041,-.360239,-.229751,-.135713,-.068203,-.029755,1.294390,1.68]
A_1224=[17.244846,-7.964373,.625343,-.105068,.292196,-.344492,.271670,-.151722,.121320,-.035566,.045966,1.1123,1.38373]
A_24100=[82.017868,-59.064244,-1.356615,1.055396,.837341,.431875,.440840,-.061588,.209414,-.120882,.055734,-.035974,.909416,1.122751]
A_100500=[306.592351,-205.393808,-4.69568,-2.031603,-.071792,-.437682,.176352,-.182516,.064687,-.027019,.010019,.07,.99799]
# parms A(0) -> A(n) and ZL,ZU
def Diode_Fit(Z):
    if Z <= .909416:
        A=A_100500
    elif Z <= 1.11230:
        A=A_24100
    elif Z <= 1.29439:
        A=A_1224
    else:
        A=A_212
    x=((Z-A[len(A)-2])-(A[len(A)-1]-Z))/(A[len(A)-1]-A[len(A)-2])
    T=0
    for i in range(len(A)-2):
        T=T+A[i]*np.cos(i*np.arccos(x))
    return T
    
if __name__ == "__main__":
    Diode_Fit_Vec = np.vectorize(Diode_Fit)
    
    multimeter=AGILENT_MULTIMETER("GPIB0::3::INSTR")
    
    V = multimeter.Read_V()
    
    print("\nTime: {:s}\nDiode Voltage: {:.4f} V\nTemperature:   {:.2f} K".format(datetime.now().strftime("%H:%M:%S %m/%d/%y"), V, Diode_Fit_Vec(V)))