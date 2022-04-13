# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 14:41:15 2021

@author: 358561
"""

"""
Created on Thu Jan 28 17:16:10 2021
@author: physics-svc-mkdata
"""

import numpy as np

etaTHe3 = 1.8312E-7 # kgK^2/ms
rhoHe3 = 81.898 # kg/m^3

foVac_commFork = 32756.5 # Hz
rhoq = 2659 # kg/m^3
L = 3.1E-3
W = 0.1E-3
T = 0.25E-3
C = 0.57
S = 2*(T+W)*L
mvac = 0.24267*rhoq*L*W*T # after Blaauwgeers

def Meas_Viscosity(width,frequency):
    return (((width*mvac*2)/(C*S*(frequency/foVac_commFork)**2))**2)*((np.pi)/(frequency*rhoHe3))

def Meas_Temp(width,frequency):
    return np.sqrt(etaTHe3/Meas_Viscosity(width,frequency))

if __name__ == "__main__":
    print(Meas_Temp(width=45.7,frequency=32.37*1E3))