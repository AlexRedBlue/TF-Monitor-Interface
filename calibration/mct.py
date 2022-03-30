import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt

# Measured 1/11/22
b1=-4951.893
b2=16442.018
b3=-11489.555

# plt.figure()
# x=np.linspace(.0009,.300, 1000)

an3 = -1.3855442E-12
an2 = 4.557026E-9
an1 = -6.4430869E-6
a0 = 3.4467434E0
a1 = -4.416438E0
a2 = 1.5427437E1
a3 = -3.5789853E1
a4 = 7.1499125E1
a5 = -1.0414379E2
a6 = 1.0518538E2
a7 = -6.9443767E1
a8 = 2.6833087E1
a9 = -4.5875709E0

# y=(((an3*x**-3) + (an2*x**-2) + (an1*x**-1) + (a0*x**0) + (a1*x**1) + (a2*x**2) + (a3*x**3) + (a4*x**4) + (a5*x**5) + (a6*x**6) + (a7*x**7) + (a8*x**8) + (a9*x**9)))

# plt.plot(x, y)

# From Astrov D.N., Ermakov N.B. VNIIFTRI (Russia)
# P is in MPa, T is in K
# an3 = 2.7452234E-4
# an2 = -2.2158311E-2
# an1 = 0.7393473
# a0 = -9.8654414
# a1 = 1.4166019E2
# a2 = -1.0229806E3
# a3 = 4.9025185E3
# a4 = -1.5897102E4
# a5 = 3.5040167E4
# a6 = -5.1639017E4
# a7 = 4.8645161E4
# a8 = -2.6460530E4
# a9 = 6.3173899E3

# y=(((an3*x**-3) + (an2*x**-2) + (an1*x**-1) + (a0*x**0) + (a1*x**1) + (a2*x**2) + (a3*x**3) + (a4*x**4) + (a5*x**5) + (a6*x**6) + (a7*x**7) + (a8*x**8) + (a9*x**9)))

# plt.plot(x, y)

x=np.linspace(.0009,.300,1000)
y=(((an3*x**-3) + (an2*x**-2) + (an1*x**-1) + (a0*x**0) + (a1*x**1) + (a2*x**2) + (a3*x**3) + (a4*x**4) + (a5*x**5) + (a6*x**6) + (a7*x**7) + (a8*x**8) + (a9*x**9)))
tck = interpolate.splrep(-1*y,x)


def MCT_V2T(Vin, C):
    # pOffset = -0.00016
    pOffset = 0
    Cap = (.00165)*Vin + C
    # Convert to MPa 0.0068948 MPa/psi
    p = ((b1 + (b2*Cap) + (b3*(Cap**2)))) * 0.0068948 + pOffset 
    T=interpolate.splev(-1*p,tck)
    return T, p


MCT_V2Tv = np.vectorize(MCT_V2T)

# if __name__ == "__main__":
    # from instruments.AGILENT_MULTIMETER import AGILENT_MULTIMETER
    # dvm = AGILENT_MULTIMETER("GPIB0::7::INSTR")
    # V = dvm.Read_V()
    # print("V: ", V)
    # V = 0
    # print('Temperature: {:.4f} K\nPressure: {:.4f} MPa'.format(*MCT_V2T(V, 0.5111)))
    
    # x=np.linspace(.010,.750, 1000)
    # y=(((an3*x**-3) + (an2*x**-2) + (an1*x**-1) + (a0*x**0) + (a1*x**1) + (a2*x**2) + (a3*x**3) + (a4*x**4) + (a5*x**5) + (a6*x**6) + (a7*x**7) + (a8*x**8) + (a9*x**9)))

    # plt.figure()
    # plt.plot(x, y)