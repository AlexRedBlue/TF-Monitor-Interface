# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 13:25:07 2022

@author: alexd
"""
from tuning_fork import Lorentz_Fitting as LF

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from scipy import interpolate

import time

mpl.rcParams['figure.dpi'] = 288

f = np.linspace(3268000, 32720, 500)

Gamma = np.linspace(80, 100, 400)
f_0 = np.linspace(32700, 32650, 400)
a = 1
V = 1
m = 1/(4*np.pi)
q = f_0/Gamma
I = a**2 * (V/Gamma) / (4*np.pi*m)

tck_Iq = interpolate.splrep(I[::-1], q[::-1])

tck_I = interpolate.splrep(f_0[::-1], I[::-1])

# Ix = LF.Lorentz_x(np.linspace(f_0[99]-50, f_0[99]+50, 100), [f_0[99], I[99], Gamma[99], 0, 0, 0])
# plt.figure()
# plt.plot(Ix, interpolate.splev(Ix, tck_Iq))

# %%

# I_f0 = []
# inflection = []
# single_point = []

# meff_list = []
# measured_f_list = []
change = []
# minimized_f_list = []

# measured_f = f_0[0]
# measured_Ix = I[0]

# def find_meff(input_f, input_Ix):
#     interp_q_000 = interpolate.splev(input_f, tck_q)
#     meff_0000 = (V/input_Ix)*a**2/(4*np.pi)*(interp_q_000/input_f)
#     return meff_0000

# mvac = find_meff(f_0[0], I[0])

# # measured_f = f_0[100]
# # measured_Ix = I[100]

# # f_range = np.linspace(measured_f-50, measured_f+50, 300)
# # previous_I = measured_Ix
# # measured_Ix = LF.Lorentz_x(measured_f, [f_0[99], I[99], Gamma[99], 0, 0, 0])

# # i_range = np.linspace(measured_Ix, previous_I, 100)

# # f_mesh, i_mesh = np.meshgrid(f_range, i_range)

# # meff = find_meff(f_mesh, i_mesh)
# # a = np.abs(meff-mvac)
# # print(np.abs(meff-mvac).min())
# # ind = np.unravel_index(np.argmin(a, axis=None), a.shape)
# # print(ind)
# # print(f_mesh[0, ind[1]], "\n", i_mesh[ind[0], 0])
# # print(f_0[99], "\n", I[99])

# from matplotlib import cm
# from matplotlib.ticker import LinearLocator


# # fig, ax = plt.subplots(subplot_kw={"projection": "3d"})


# # # Plot the surface.
# # surf = ax.plot_surface(f_mesh, i_mesh, np.abs(meff-mvac), cmap=cm.coolwarm,
# #                        linewidth=0, antialiased=False)

# # # Add a color bar which maps values to colors.
# # fig.colorbar(surf, shrink=0.5, aspect=5)

# %%

measured_f = f_0[0]
measured_Ix = I[0]
q_0 = interpolate.splev(measured_Ix, tck_Iq)

fig, ax = plt.subplots()

for idx, G in enumerate(Gamma):
    
    # for item in ax:  
    #     item.clear()
    ax.clear()
    # ax[0].plot(f, Ix)
    # ax[0].scatter(f_0[idx], Ix.max(), color='firebrick')
    # ax[0].scatter(f_0[idx]-G/2, Ix.max()/2, color='green')
    # ax[0].scatter(f[250], Ix[250], color='purple')
    # ax[0].set_xlim([f[0], f[-1]])
    # ax[0].set_ylim([I[-1]-0.01, I[0]])
    
    # I_f0.append(Ix.max())
    # inflection.append(Ix.max()/2)
    # single_point.append(Ix[250])
    # ax[1].plot(np.arange(0, idx+1, 1), I_f0, color='firebrick')
    # ax[1].plot(np.arange(0, idx+1, 1), inflection, color='green')
    # ax[1].plot(np.arange(0, idx+1, 1), single_point, color='purple')
    
    # previous_I = measured_Ix
    measured_Ix = LF.Lorentz_x(measured_f, [f_0[idx], I[idx], G, 0, 0, 0])
    
    q = interpolate.splev(measured_Ix, tck_Iq)
    change.append(q-q_0)
    # entrained_mass = find_entrained_mass(measured_f, measured_Ix)

    # meff_list.append(find_meff(measured_f, measured_Ix))
    # print(measured_Ix, previous_I)
    # f_range = np.linspace(measured_f-25, measured_f+25, 100)
    # i_range = np.linspace((1-1E-3)*measured_Ix, (1+1E-3)*previous_I, 1000)
    
    # f_mesh, i_mesh = np.meshgrid(f_range, i_range)
    # meff = find_meff(f_mesh, i_mesh)
    
    # a = np.abs(meff-mvac)

    # ind = np.unravel_index(np.argmin(a, axis=None), a.shape)

    # minimized_f = f_mesh[0][ind[1]]
    # i_range[ind[0]][0]
    
    # measured_f = minimized_f

    # measured_f_list.append(measured_f-f_0[idx])
    
    # surf = ax.plot_surface(f_mesh, i_mesh, np.abs(meff-mvac), cmap=cm.coolwarm,
    #                        linewidth=0, antialiased=False)
    
    # ax[1].plot(np.arange(0, idx+1, 1), measured_f_list, color='firebrick')
    
    # ax[2].plot(np.arange(0, idx+1, 1), np.asarray(meff_list))
    # ax[0].scatter(minimized_f, i_mesh[ind[0], 0], color='red')
    ax.plot(change)
    plt.pause(0.5)
    # time.sleep(0.1)
