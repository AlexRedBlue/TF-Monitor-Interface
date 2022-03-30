# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:37:17 2020
Lorentz Fitting for Tuning Forks
@author: physics-svc-mkdata
"""
import numpy as np
from scipy import optimize

def Lorentz_x(f, coeffs):
    """Returns the in-phase/absorption lorentzian curve from an array, f and coefficients
    , coeff, where coeff has the form [frequency,height,width,phase,bgrdint,bgrdslp]"""
    frequency, height, width, phase, bgrgint, bgrdslp = coeffs
    X = (height*f**2*width**2)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*f*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    return X*np.cos(phase)+Y*np.sin(phase)-(bgrgint+bgrdslp*f)

# X = (height *  f**2      *    width**2    ) / ((f_0**2 - f**2)**2 + (f*width)**2)
# Y = (height *  f * width * (f_0**2 - f**2)) / ((f_0**2 - f**2)**2 + (f*width)**2)

def Lorentz_y(f, coeffs):
    """Returns the out-of-phase/disperson Lorentzian curve from the array f and coefficients
    coeff:[frequency,height,width,phase,bgrdint,bgrdslp]"""
    frequency, height, width, phase, bgrgint, bgrdslp = coeffs
    X = (height*f**2*width**2)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*f*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    return Y*np.cos(phase)-X*np.sin(phase)-(bgrgint+bgrdslp*f)

def Lorentz_x_quad(f, coeffs):
    """Returns the in-phase/absorption lorentzian curve from an array, f and coefficients
    , coeff, where coeff has the form [frequency,height,width,phase,bgrdint,bgrdslp]"""
    frequency, height, width, phase, bgrgint, bgrdslp, bgrdquad = coeffs
    X = (height*f**2*width**2)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*f*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    # return X*np.cos(coeffs[3])+Y*np.sin(coeffs[3])-(coeffs[4]+coeffs[5]*(f-f[0])+coeffs[6]*(f-f[0])**2)
    return X*np.cos(phase)+Y*np.sin(phase)-(bgrgint + bgrdslp*f + bgrdquad*f**2)

def Lorentz_y_quad(f, coeffs):
    """Returns the out-of-phase/disperson Lorentzian curve from the array f and coefficients
    coeff:[frequency,height,width,phase,bgrdint,bgrdslp]"""
    frequency, height, width, phase, bgrgint, bgrdslp, bgrdquad = coeffs
    X = (height*f**2*width**2)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*f*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    # return Y*np.cos(coeffs[3])-X*np.sin(coeffs[3])-(coeffs[4] + coeffs[5]*(f-f[0]) + coeffs[6]*(f-f[0])**2)
    return Y*np.cos(phase)-X*np.sin(phase)-(bgrgint + bgrdslp*f + bgrdquad*f**2)

def Lorentz_x_noBgrd(f, coeffs):
    """Returns the in-phase/absorption lorentzian curve from an array, f and coefficients
    , coeff, where coeff has the form [frequency,height,width,phase,bgrdint,bgrdslp]. This version
    does not subtract the background"""
    frequency, height, width, phase = coeffs
    X = (height*f**2*width)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*f*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    return X*np.cos(phase)+Y*np.sin(phase)

def Lorentz_x_noBgrd(f, coeffs):
    """Returns the in-phase/absorption lorentzian curve from an array, f and coefficients
    , coeff, where coeff has the form [frequency,height,width,phase,bgrdint,bgrdslp]. This version
    does not subtract the background"""
    frequency, height, width, phase = coeffs
    X = (height*f**2*width)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*f*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    return Y*np.cos(phase)-X*np.sin(phase)

def Lorentz_x_Curve(f, freq, height, width, bgrdint, bgrdslp, phase):
    """Returns the Lorentzian line shape defined by the input parameters"""
    X = (height*freq*f*width**2)/((freq**2-f**2)**2+(f*width)**2)
    Y = (height*freq*width*(freq**2-f**2))/((freq**2-f**2)**2+(f*width)**2)
    return X*np.cos(phase)+Y*np.sin(phase)-(bgrdint+bgrdslp*(f))

def residuals_x(coeffs, v, f):
    return v - Lorentz_x(f, coeffs)

def residuals_y(coeffs, v, f):
    return v - Lorentz_y(f, coeffs)

def residuals_x_quad_bgr(coeffs, v, f):
    return v - Lorentz_x_quad(f, coeffs)

def residuals_y_quad_bgr(coeffs, v, f):
    return v - Lorentz_y_quad(f, coeffs)

def Lorentz_Fit_X_quad(x,y,guess):
    return optimize.leastsq(residuals_x_quad_bgr, guess, args=(y, x))

def Lorentz_Fit_Y_quad(x,y,guess):
    return optimize.leastsq(residuals_y_quad_bgr, guess, args=(y, x))

def Lorentz_Fit_X(x,y,guess):
    return optimize.leastsq(residuals_x, guess, args=(y, x))

def Lorentz_Fit_X_Curve(x,y,guess):
    return optimize.curve_fit(Lorentz_x_Curve,x,y,p0=guess)
    
def Lorentz_Fit_Y(x,y,guess):
    return optimize.leastsq(residuals_y, guess, args=(y, x))


###### DO NOT USE ###### OLD FUNCTIONS ######

def Lorentz_x_quad_old(f, coeffs):
    """Returns the in-phase/absorption lorentzian curve from an array, f and coefficients
    , coeff, where coeff has the form [frequency,height,width,phase,bgrdint,bgrdslp]"""
    frequency, height, width, phase, bgrgint, bgrdslp, bgrdquad = coeffs
    X = (height*frequency*f*width**2)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*frequency*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    # return X*np.cos(coeffs[3])+Y*np.sin(coeffs[3])-(coeffs[4]+coeffs[5]*(f-f[0])+coeffs[6]*(f-f[0])**2)
    return X*np.cos(phase)+Y*np.sin(phase)-(bgrgint + bgrdslp*f + bgrdquad*f**2)

def Lorentz_y_quad_old(f, coeffs):
    """Returns the out-of-phase/disperson Lorentzian curve from the array f and coefficients
    coeff:[frequency,height,width,phase,bgrdint,bgrdslp]"""
    frequency, height, width, phase, bgrgint, bgrdslp, bgrdquad = coeffs
    X = (height*frequency*f*width**2)/((frequency**2-f**2)**2+(f*width)**2)
    Y = (height*frequency*width*(frequency**2-f**2))/((frequency**2-f**2)**2+(f*width)**2)
    # return Y*np.cos(coeffs[3])-X*np.sin(coeffs[3])-(coeffs[4] + coeffs[5]*(f-f[0]) + coeffs[6]*(f-f[0])**2)
    return Y*np.cos(phase)-X*np.sin(phase)-(bgrgint + bgrdslp*f + bgrdquad*f**2)

"""
measured_X = Xcos+Ysin-bgrdX
measured_Y = Ycos-Xsin-bgrdY

(mX+bgrd)/sin = Xcot + Y
(mY+bgrd)/cos = Y - Xtan

(mX+bgrdX)/sin - (mY+bgrdY)/cos = Xcos/sin + Xsin/cos
(mX+bgrdX)/cos + (mY+bgrdY)/sin = Ysin/cos + Ycos/sin

X = [(mX+bgrd)/sin - (mY+bgrd)/cos]/(cot+tan)
Y = [(mX+bgrd)/cos + (mY+bgrd)/sin]/(tan+cot)
"""

def residuals_x_quad_bgr_old(coeffs, v, f):
    return v - Lorentz_x_quad_old(f, coeffs)

def residuals_y_quad_bgr_old(coeffs, v, f):
    return v - Lorentz_y_quad_old(f, coeffs)

def Lorentz_Fit_X_quad_old(x,y,guess):
    return optimize.leastsq(residuals_x_quad_bgr_old, guess, args=(y, x))

def Lorentz_Fit_Y_quad_old(x,y,guess):
    return optimize.leastsq(residuals_y_quad_bgr_old, guess, args=(y, x))


###### END OF DO NOT USE ######
