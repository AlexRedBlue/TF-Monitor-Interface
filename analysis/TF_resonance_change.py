import numpy as np

TF_f0 = 32776.8 # Cell
TF_silver_f0 = 32852.0 # Silver

# f0 proportional to 1/l

def find_f0():
    # beta = 0.141 # t=w
    # beta = 0.333 # t<<w
    G = 3.11E10
    rhoq = 2659
    l = 3.1E-3
    w = 0.1E-3
    t = 0.25E-3
    beta = np.sqrt(0.02*(1+4.5*(t/w)**2))
    f0 = 1/(2*l)*np.sqrt(3*G/rhoq * beta*w**2/(t**2+w**2))
    return f0

print(find_f0())
    

print("l1/l0", (TF_f0/TF_silver_f0))

print("m1/m0", (0.88))