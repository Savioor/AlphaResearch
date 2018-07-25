#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 09:53:15 2018

@author: ron
"""

import tools as tls
import numpy as np
import matplotlib.pyplot as pplot
from Raupach_eq_drag_mesurments import get_drag_raupach, area_by_volume
from acc_mesurments import sum_all_acc
from Cd_drag_mesurment import calc_vel_and_drag_from_data_Cd, general, air_density

def quiver_velocity(vel):
    acc = tls.read_json("raupach_data/avg_vel_by_loc_" + vel)
    fig, ax = pplot.subplots()
    matx = np.zeros((18, 18))
    matcount = np.zeros((18, 18))
    matz = np.zeros((18, 18))
 
    for key in acc.keys():
        x = int(float(key.split(", ")[0].replace("(", "")) * 100.0)
        z = int(float(key.split(", ")[1]) * 100.0)
        if x > 0:
            x *= -1
        matx[z, -x] += -acc[key][0][0] * acc[key][1]
        matz[z, -x] += acc[key][0][1] * acc[key][1]
        matcount[z, -x] += acc[key][1]

    Y = np.zeros((18, 18))
    X = np.zeros((18, 18))
    for i in xrange(len(Y)):
        for j in xrange(len(Y)):
            Y[i, j] = i / 10.0
            X[i, j] = j / 10.0
            if matcount[i, j] != 0:
                matx[i, j] /= matcount[i, j]
                matz[i, j] /= matcount[i, j]
    
    ax.quiver(X, Y, matx, matz, units="inches", scale=1)
    
    ax.set_xlabel(r"x/H")
    ax.set_ylabel(r"z/H")
    
    return fig, ax

def plot_drag(vel, mass = air_density * 0.1 * 0.01 * 0.15):
    fig, ax = pplot.subplots()
    
    t = calc_vel_and_drag_from_data_Cd(general + vel)["drag_list"]
    t = t[:-7]
    ax.plot(map(lambda a: a[1] * 10, t), map(lambda a: a[0], t), "bo-", label="Fox et. al.")
        
    t = sum_all_acc(vel, only_corner=True)[0]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key][0][0], key * 10.0))
    lis = lis[1:-7]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "co-", label="Accel local avg")
    
    t = get_drag_raupach(vel, area=area_by_volume)["rey stress gradient"]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key] * mass, key / 10.0))
    lis = lis[:-6]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: -a[0], lis), "mo-", label="Brunet et. al.")
    
    ax.legend()
    ax.set_xlabel(r"z/H")
    ax.set_ylabel("Drag (N)")
    
    return fig, ax

def plot_Cd(vel, use_U_inf=False):
    fig, ax = pplot.subplots()
    if not use_U_inf:
        ax.plot([0.5, 0.6, 0.7, 0.8, 0.9, 1], np.ones(6)*2.05, "bo-", label="Fox et. al.")
    else:
        t = calc_vel_and_drag_from_data_Cd(general + vel)["drag_list"]
        t = t[:-7]
        ax.plot(map(lambda a: a[1] * 10.0, t), map(lambda a: a[0] / (0.5 * air_density * 0.01 * 0.05 * (float(vel)**2)), t), "bo-", label="Fox et. al.")
    
    t = get_drag_raupach(vel, area=area_by_volume)["Cd br"] \
    if not use_U_inf else get_drag_raupach(vel, area=area_by_volume)["Cd"]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key], key / 10.0))
    if not use_U_inf:
        lis = lis[1:]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "mo-", label="Brunet et. al.")
    
    """
    t = sum_all_acc("2.5")[1]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key][0], key * 10.0))
    lis = lis[1:-7]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "co-", label="Accel total avg")
    """
    
    t = sum_all_acc(vel, only_corner=True)[1] \
    if not use_U_inf else sum_all_acc(vel, only_corner=True)[2]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key][0], key * 10.0))
    lis = lis[1:-7]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: -a[0], lis), "co-", label="Accel local avg")
    
    ax.legend()
    ax.set_xlabel(r"z/H")
    ax.set_ylabel(r"$\frac{F_D}{\rho A U^2_{\infty}}$", size = 15)
    
    return fig, ax