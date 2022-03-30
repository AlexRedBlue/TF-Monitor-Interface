# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 15:56:06 2021

@author: physics-svc-mkdata
"""

import numpy as np
import matplotlib.pyplot as plt

import pyvisa
from instruments.LAKESHORE import LS370

lakeshore = LS370("GPIB0::6::INSTR")

# %%
curve = 14
points = 200
L_Ohm, Temp = np.empty(200), np.empty(200)

for point in range(points):
    cmd_str = "CRVPT? {},{}".format(curve, point)
    L_Ohm[point], Temp[point] = lakeshore.inst.query(cmd_str).rstrip().split(',')

L_Ohm = L_Ohm.astype(float)
Temp = Temp.astype(float)

# %%

plt.figure()
plt.plot(np.power(10, L_Ohm[Temp>1E-5]), Temp[Temp>1E-5]/10)
# plt.plot(np.power(10, L_Ohm[Temp>0]), Temp[Temp>0]/10)
# plt.plot(L_Ohm[Temp>0], Temp[Temp>0])
plt.xlabel('Resistance, $\Omega$')
plt.ylabel('Temperature, K')
plt.title('Resistance Temperature curve {}'.format(curve))

# %%

np.savetxt(r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration\R8_RT_Curve.dat", 
           np.transpose([np.power(10, L_Ohm[Temp>1E-5]), Temp[Temp>1E-5]/10]),
           delimiter="\t",
           header="R, Ohms\tT, K")
