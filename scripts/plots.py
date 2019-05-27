#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 09:53:15 2018

@author: Alexey
"""

import tools as tls
import numpy as np
import matplotlib.pyplot as pplot
from Raupach_eq_drag_mesurments import get_drag_raupach, get_drag_raupach_err, area_by_volume
from acc_mesurments import sum_all_acc, mass
from Cd_drag_mesurment import calc_vel_and_drag_from_data_Cd, general, air_density, nb
import Cd_drag_mesurment as cdCode
from get_statistics import get_std_h

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
    
    for i in range(11):
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
    for i in range(len(Y)):
        for j in range(len(Y)):
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
        
    ax.errorbar(
    list(map(lambda a: a[1] * 10, data2)),
    list(map(lambda a: a[0], data2)),
    fmt="c+-",
    label="2.5 m/s",
    yerr=get_error_bars("Statistics/vel_mult_avgs_2.5", data2))
    
    ax.errorbar(list(map(lambda a: a[1] * 10, data4)),
    list(map(lambda a: a[0], data4)),
    fmt="g+-",
    label="4.0 m/s",
    yerr=get_error_bars("Statistics/vel_mult_avgs_4.0", data4))
    
    ax.errorbar(list(map(lambda a: a[1] * 10, data2nb)),
    list(map(lambda a: a[0], data2nb)),
    fmt="co--",
    label="2.5 m/s near building",
    yerr=get_error_bars("Statistics/vel_nb_mult_avgs_2.5", data2nb))
    
    ax.errorbar(list(map(lambda a: a[1] * 10, data4nb)),
    list(map(lambda a: a[0], data4nb)),
    fmt="go--",
    label="4.0 m/s near building",
    yerr=get_error_bars("Statistics/vel_nb_mult_avgs_4.0", data4nb))

    ax.set_ylabel("Velocity (m/s)")
    ax.set_xlabel("z/H")
    ax.legend()

    return fig, ax


def get_error_bars(file_name, data):
    lower_err = []
    upper_err = []
    for v in data:
        err = get_error(file_name, v[1])
        print v[1]
        lower_err.append(abs(v[0] - err[0]))
        upper_err.append(abs(err[1] - v[0]))
    return [lower_err, upper_err]


def get_error(file_name, h, mult=1.0):
    data = tls.read_json(file_name)
    for key in data.keys():
        splat = key.split(" - ")
        firstNum = float(splat[0])
        secondNum = float(splat[1])
        if h > firstNum and h < secondNum:
            rel_array = data[key]
            rel_array.sort(key=lambda a: a[0])
            return np.array([rel_array[0][0], rel_array[-1][0]]) * mult

    
def plot_drag(vel, mass = air_density * 0.1 * 0.01 * 0.15):
    fig, ax = pplot.subplots()
    
    t = calc_vel_and_drag_from_data_Cd(general + vel)["drag_list"]
    t = t[:-7]
    ax.errorbar(map(lambda a: a[1] * 10, t), map(lambda a: a[0], t), fmt="bo-",
        label="Fox et. al.",
        yerr=cdCode.get_error_bars("Statistics/vel_mult_avgs_" + vel, t, air_density, float(vel)))
        
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

# For the graphs in the paper use 'use_U_inf=True' and 'version="2"'
def plot_Cd(vel, use_U_inf=False, version = ""):
    fig, ax = pplot.subplots()
    if not use_U_inf:
        ax.plot([0.5, 0.6, 0.7, 0.8, 0.9, 1], np.ones(6)*2.05, "bo-", label="Fox et. al.")
    else:
        t = calc_vel_and_drag_from_data_Cd(general + vel)["drag_list"]
        t = t[:-7]
        ax.errorbar(map(lambda a: a[1] * 10.0, t), 
            map(lambda a: a[0] / (0.5 * air_density * 0.01 * 0.05 * (float(vel)**2)), t), fmt="bo-",
            label="Fox et. al.",
            yerr=cdCode.get_error_bars("Statistics/vel_mult_avgs_" + vel, t, air_density, float(vel)))

    t = get_drag_raupach(vel, area=area_by_volume)["Cd br"] \
    if not use_U_inf else get_drag_raupach(vel, area=area_by_volume)["rey stress gradient"]
    e = get_drag_raupach_err(vel, area=area_by_volume)["rey stress gradient h"]
    v = float(vel)
    lis = []
    err_lis = [[],[]]
    
    for key in sorted(t.keys()):
        value = (t[key] / (-0.5 * (v ** 2) * area_by_volume))
        err_value = abs(value - (e[key] / (-0.5 * (v ** 2) * area_by_volume)))
        err_lis[0].append(err_value)
        err_lis[1].append(err_value)
        lis.append((value, key / 10.0))
    
    if not use_U_inf:
        err_lis[0] = err_lis[0][1:]
        err_lis[1] = err_lis[1][1:]
        lis = lis[1:]
    err_lis[0] = err_lis[0][:-6]
    err_lis[1] = err_lis[1][:-6]
    lis = lis[:-6]
    ax.errorbar(map(lambda a: a[1], lis), map(lambda a: a[0], lis), fmt="mo-", label="Brunet et. al.",
        yerr=err_lis)
    
    """
    t = sum_all_acc("2.5")[1]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key][0], key * 10.0))
    lis = lis[1:-7]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "co-", label="Accel total avg")
    """
    
    error = sum_all_acc(vel, only_corner=True, version=version)[3]
    t = sum_all_acc(vel, only_corner=True, version=version)[1] \
    if not use_U_inf else sum_all_acc(vel, only_corner=True, version=version)[2]
    t.pop(sorted(t.keys())[0])
    error.pop(sorted(error.keys())[0])

    lis = []
    err_lis = [[], []]
        
    for key in sorted(t.keys()):
        err_lis[0].append(error[key][0])
        err_lis[1].append(error[key][1])
        lis.append((t[key][0], key * 10.0))
    lis = lis[0 if vel == "4.0" else 1:-7 if vel == "4.0" else -8]
    err_lis[0] = err_lis[0][0 if vel == "4.0" else 1:-7 if vel == "4.0" else -8]
    err_lis[1] = err_lis[1][0 if vel == "4.0" else 1:-7 if vel == "4.0" else -8]

    ax.errorbar(map(lambda a: a[1], lis), map(lambda a: -a[0], lis), fmt="co-", label="Accel local avg", yerr=err_lis)

    ax.legend(loc=2)
    ax.set_xlabel(r"z/H", size=12)
    ax.set_ylabel(r"$\frac{2\cdot F_D}{\rho A U^2_{\infty}}$", size = 18)
    
    return fig, ax


def plot_acc_drag(use_U_inf=False, version = ""):
    
    fig, ax = pplot.subplots()
    
    vel = "2.5"
    
    error = sum_all_acc(vel, only_corner=True, version=version)[3]
    t = sum_all_acc(vel, only_corner=True, version=version)[1] \
    if not use_U_inf else sum_all_acc(vel, only_corner=True, version=version)[2]
    t.pop(sorted(t.keys())[0])
    error.pop(sorted(error.keys())[0])
    t.pop(sorted(t.keys())[0])
    error.pop(sorted(error.keys())[0])

    lis = []
    err_lis = [[], []]
        
    for key in sorted(t.keys()):
        err_lis[0].append(error[key][0])
        err_lis[1].append(error[key][1])
        lis.append((t[key][0], key * 10.0))
    lis = lis[:-7 if vel == "4.0" else -8]
    err_lis[0] = err_lis[0][:-7 if vel == "4.0" else -8]
    err_lis[1] = err_lis[1][:-7 if vel == "4.0" else -8]
    
    # <temp>
    avg = 0
    count = len(err_lis[0])
    for i in range(count):
        avg += (err_lis[0][i] + err_lis[1][i]) / 2.0
    print "2.5"
    print avg / count
    # </temp>

    ax.errorbar(map(lambda a: a[1], lis), map(lambda a: -a[0], lis), fmt="co-", label=vel, yerr=err_lis)
    
    vel = "4.0"
    
    error = sum_all_acc(vel, only_corner=True, version=version)[3]
    t = sum_all_acc(vel, only_corner=True, version=version)[1] \
    if not use_U_inf else sum_all_acc(vel, only_corner=True, version=version)[2]
    t.pop(sorted(t.keys())[0])
    error.pop(sorted(error.keys())[0])
    t.pop(sorted(t.keys())[0])
    error.pop(sorted(error.keys())[0])

    lis = []
    err_lis = [[], []]
        
    for key in sorted(t.keys()):
        err_lis[0].append(error[key][0])
        err_lis[1].append(error[key][1])
        lis.append((t[key][0], key * 10.0))
    lis = lis[:-7 if vel == "4.0" else -8]
    err_lis[0] = err_lis[0][:-7 if vel == "4.0" else -8]
    err_lis[1] = err_lis[1][:-7 if vel == "4.0" else -8]
    
    # <temp>
    avg = 0
    count = len(err_lis[0])
    for i in range(count):
        avg += (err_lis[0][i] + err_lis[1][i]) / 2.0
    print "4.0"
    print avg / count
    # </temp>
    
    ax.errorbar(map(lambda a: a[1], lis), map(lambda a: -a[0], lis), fmt="go-", label=vel, yerr=err_lis)
    
    ax.legend(loc=2)
    ax.set_xlabel(r"z/H", size=12)
    ax.set_ylabel(r"$\frac{2\cdot F_D}{\rho A U^2_{\infty}}$", size = 18)
    
    return fig, ax
        

def plot_rey_stress():
    fig, ax = pplot.subplots()
    rs25 = get_drag_raupach("2.5", area=area_by_volume)["rey stress gradient"]
    rs25err = get_drag_raupach_err("2.5", area=area_by_volume)["rey stress gradient h"]
    rs40 = get_drag_raupach("4.0", area=area_by_volume)["rey stress gradient"]
    rs40err = get_drag_raupach_err("4.0", area=area_by_volume)["rey stress gradient h"]

    lis = []
    err_lis = [[], []]
    for key in sorted(rs25.keys()):
        value = (rs25[key] / (-0.5 * (2.5 ** 2) * area_by_volume))
        err_value = abs(value - (rs25err[key] / (-0.5 * (2.5 ** 2) * area_by_volume)))
        err_lis[0].append(err_value)
        err_lis[1].append(err_value)
        lis.append((value, key / 10.0))
    err_lis[0] = err_lis[0][:-6]
    err_lis[1] = err_lis[1][:-6]
    lis = lis[:-6]
    ax.errorbar(map(lambda a: a[1], lis), map(lambda a: a[0], lis), fmt="cs-", label="2.5 m/s", yerr=err_lis)
    lis = []
    
    err_lis = [[], []]
    for key in sorted(rs40.keys()):
        value = (rs40[key] / (-0.5 * (4.0 ** 2) * area_by_volume))
        err_value = abs(value - (rs40err[key] / (-0.5 * (4.0 ** 2) * area_by_volume)))
        err_lis[0].append(err_value)
        err_lis[1].append(err_value)
        lis.append((value, key / 10.0))
    err_lis[0] = err_lis[0][:-6]
    err_lis[1] = err_lis[1][:-6]
    lis = lis[:-6]
    ax.errorbar(map(lambda a: a[1], lis), map(lambda a: a[0], lis), fmt="gs-", label="4.0 m/s", yerr=err_lis)

    ax.legend()
    ax.set_xlabel("z/H")
    ax.set_ylabel(r"$\frac{2\cdot F_D}{\rho A U^2_{\infty}}$", size = 16)

    return fig, ax

if __name__ == '__main__':
    #   fig, ax = plot_Cd("2.5", True, "2")
    #fig.show()
    fig, ax = plot_acc_drag(True, "2")
    #fig.show()

    #pplot.show()
    