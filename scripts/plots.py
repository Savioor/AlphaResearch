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
from Cd_drag_mesurment import calc_vel_and_drag_from_data_Cd, general, air_density, nb

def heat_map_velocity(vel):
    fig, ax = pplot.subplots()
    scale, sax = pplot.subplots()
    acc_raw = tls.read_json("raupach_data/avg_vel_by_loc_" + vel)
    acc = {}
     
    for key in acc_raw.keys():
        newk = ", ".join(key.split(", ")[:-1])
        if newk in acc.keys():
            acc[newk] += np.array([np.array(acc_raw[key][0]) * acc_raw[key][1], acc_raw[key][1]])
        else:
            acc[newk] = np.array([np.array(acc_raw[key][0]) * acc_raw[key][1], acc_raw[key][1]])
    
    for key in acc.keys():
        acc[key][0] /= acc[key][1]
        
    vals_raw = []
    for item in acc.keys():
         if acc[item][1] < 10000:
            continue
         x = int(float(item.split(", ")[0].replace("(", "")) * 100)
         vals_raw.append(-acc[item][0][0])
         
    maximum = max(vals_raw)
    minimum = min(vals_raw)
    mat = np.zeros(shape=(18, 18, 3)).tolist()
    mat_s = np.zeros(shape=(1, 99, 3)).tolist()
    
    for key in acc.keys():
        x = int(float(key.split(", ")[0].replace("(", "")) * 100)
        if x > 0:
             x = -x
        if acc[key][1] < 10000:
            continue
        z = int(float(key.split(", ")[1].replace(")", "")) * 100)
        val = ((-acc[key][0][0] - minimum) / (maximum - minimum))
        mat[z][-x][0] = val
        mat[z][-x][1] = 0
        mat[z][-x][2] = 1.0 - val
        ax.text(-x / 10.0 + 0.05, z / 10.0 + 0.05, round(-acc[key][0][0], 1), ha="center",
                va="center", color="w", size=7.8)
    
    for i in xrange(11):
        if i <= 5:
            mat[i][7] = [1, 1, 1]
        mat[i][15] = [1, 1, 1]
    
    val = 0.01
    ind = 0
    while val <= 1:
        mat_s[0][ind][0] = val
        mat_s[0][ind][1] = 0
        mat_s[0][ind][2] = 1 - val
        ind += 1
        val += 0.01
        
    sax.imshow(mat_s,  extent=[minimum, maximum, 0, 1], aspect='auto')
    sax.set_xticks(map(lambda a: round(a, 2), np.linspace(minimum, maximum, 12)))
    ax.imshow(mat, extent=[0, 1.8, 0, 1.8], origin="lower", aspect='auto')
    
    ax.set_xlabel(r"$x/H$")
    ax.set_ylabel(r"$z/H$")
    
    return fig, ax, scale, sax

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


def plot_velocity():
    fig, ax = pplot.subplots()

    data2 = calc_vel_and_drag_from_data_Cd(general + "2.5")["x_velocities"][:-7]
    data2nb = calc_vel_and_drag_from_data_Cd(nb + "2.5")["x_velocities"]

    data4 = calc_vel_and_drag_from_data_Cd(general + "4.0")["x_velocities"][:-7]
    data4nb = calc_vel_and_drag_from_data_Cd(nb + "4.0")["x_velocities"]

    ax.plot(list(map(lambda a: a[1] * 10, data2)), list(map(lambda a: a[0], data2)), "c+-", label="2.5 m/s")
    ax.plot(list(map(lambda a: a[1] * 10, data4)), list(map(lambda a: a[0], data4)), "g+-", label="4.0 m/s")
    ax.plot(list(map(lambda a: a[1] * 10, data2nb)), list(map(lambda a: a[0], data2nb)), "co--", label="2.5 m/s near building")
    ax.plot(list(map(lambda a: a[1] * 10, data4nb)), list(map(lambda a: a[0], data4nb)), "go--", label="4.0 m/s near building")

    ax.set_ylabel("Velocity (m/s)")
    ax.set_xlabel("z/H")
    ax.legend()

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

def plot_Cd(vel, use_U_inf=False, version = ""):
    fig, ax = pplot.subplots()
    if not use_U_inf:
        ax.plot([0.5, 0.6, 0.7, 0.8, 0.9, 1], np.ones(6)*2.05, "bo-", label="Fox et. al.")
    else:
        t = calc_vel_and_drag_from_data_Cd(general + vel)["drag_list"]
        t = t[:-7]
        ax.plot(map(lambda a: a[1] * 10.0, t), map(lambda a: a[0] / (0.5 * air_density * 0.01 * 0.05 * (float(vel)**2)), t), "bo-", label="Fox et. al.")

    t = get_drag_raupach(vel, area=area_by_volume)["Cd br"] \
    if not use_U_inf else get_drag_raupach(vel, area=area_by_volume)["rey stress gradient"]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key] / (-0.5 * (float(vel) ** 2) * area_by_volume), key / 10.0))
    if not use_U_inf:
        lis = lis[1:]
    lis = lis[:-6]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "mo-", label="Brunet et. al.")
    
    """
    t = sum_all_acc("2.5")[1]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key][0], key * 10.0))
    lis = lis[1:-7]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "co-", label="Accel total avg")
    """
    
    t = sum_all_acc(vel, only_corner=True, version=version)[1] \
    if not use_U_inf else sum_all_acc(vel, only_corner=True, version=version)[2]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key][0], key * 10.0))
    lis = lis[1:-7 if vel == "4.0" else -8]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: -a[0], lis), "co-", label="Accel local avg")

    ax.legend(loc=2)
    ax.set_xlabel(r"z/H", size=12)
    ax.set_ylabel(r"$\frac{2\cdot F_D}{\rho A U^2_{\infty}}$", size = 18)
    
    return fig, ax

def plot_rey_stress():
    fig, ax = pplot.subplots()
    rs25 = get_drag_raupach("2.5", area=area_by_volume)["rey stress gradient"]
    rs40 = get_drag_raupach("4.0", area=area_by_volume)["rey stress gradient"]
    lis = []
    for key in sorted(rs25.keys()):
        lis.append((rs25[key] / (-0.5 * (2.5 ** 2) * area_by_volume), key / 10.0))
    lis = lis[:-6]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "cs-", label="2.5 m/s")
    lis = []
    for key in sorted(rs40.keys()):
        lis.append((rs40[key] / (-0.5 * (2.5 ** 2) * area_by_volume), key / 10.0))
    lis = lis[:-6]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "gs-", label="4.0 m/s")

    ax.legend()
    ax.set_xlabel("z/H")
    ax.set_ylabel(r"$\frac{2\cdot F_D}{\rho A U^2_{\infty}}$", size = 16)

    return fig, ax

fig, ax = plot_velocity()
fig.show()
pplot.show()