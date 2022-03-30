# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 11:51:40 2021

@author: physics-svc-mkdata
"""

import numpy as np
import matplotlib.pyplot as plt

def lorentzian(w, w0, G):
    G = G/2
    return (G/np.pi)/((w-w0)**2 + G**2)

def func_2L_diff(w, w0, G, delta):
    # G = G/2
    amp = (w*delta + G*delta + delta**2)/((w-w0)**2 + (G**2))**2
    return amp

def func_d1d2(w, w0, G, d1, d2, order=1):
    G, d2 = G/2, d2/2
    A = (-2*(w-w0)*d1 + d1**2 + 2*G*d2 + d2**2)/((w-w0)**2 + G**2)
    series = 0
    for i in range(1, order+1):
        series += (-A)**i
    return -(((G+d2)*series + d2)/np.pi) / ((w-w0)**2 + G**2)

    
w = np.linspace(30,35, 1000)
delta_1 = np.linspace(.010/30, 10*.010/30, 5)
delta_2 = np.linspace(.10/30, 10*.10/30, 5)
# A = []
# for idx, d in enumerate(delta_1):
#     A.append(func_d1d2(w, 50, 10, delta_1[idx], delta_2[idx]))

# plt.figure()
# for i, d in enumerate(delta_1):
#     plt.plot(w, np.asarray(A)[i, :])
# idx = 0
# A = lorentzian(w, 32.500, .150) - lorentzian(w, 32.500+delta_1[idx], .150+delta_2[idx])
# B = []
# for i in range(1, 2):
#     print(i)
#     B.append(func_d1d2(w, 32.500, .150, delta_1[idx], delta_2[idx], order=i))
colors = ['red', 'blue', 'green', 'purple', 'orange']
plt.figure()
for idx, other_thing in enumerate(delta_1):
    A = lorentzian(w, 32.500, .150) - lorentzian(w, 32.500+delta_1[idx], .150+delta_2[idx])
    B = []
    for i in range(1, 2):
        print(i)
        B.append(func_d1d2(w, 32.500, .150, delta_1[idx], delta_2[idx], order=i))
    plt.plot(w, A, c=colors[idx])
    for thing in B:
        plt.plot(w, thing, c=colors[idx])



# (G+d2)/(((w - w0) - d1)**2 + (G + d2)**2)

# (G + d2)/((w - w0)**2 - 2*(w - w0)*d1 + d1**2 + G**2 + 2*G*d2 + d2**2)

# (G + d2)/((w - w0)**2 + G**2 + (2*(w - w0)*d1 + d1**2 + 2*G*d2 + d2**2))

# A = (2*(w0-w)*d1 - d1**2 - 2*G*d2 - d2**2)

# G/((w0-w)**2 + G**2) - (G + d2)/((w0-w)**2 + G**2) * (1/( 1 - A/((w0-w)**2 + G**2))) 

# - d2*(2*(w0-w)*d1 - d1**2 - 2*G*d2 - d2**2)/((w0-w)**2 + G**2)**2

# - (2*(w0-w)*d1*d2 - 2*G*d2**2)/((w0-w)**2 + G**2)**2

