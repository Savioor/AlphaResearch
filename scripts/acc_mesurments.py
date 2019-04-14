#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:50:22 2018

@author: Alexey
"""

import tools as tls
import numpy as np
import matplotlib.pyplot as pplot
from Cd_drag_mesurment import air_density
import Raupach_eq_drag_mesurments as raupach
import math


def group_avarage_acc(data, grouping_func,
                      filt=lambda a: True,
                      step=1):
    def param_f(element, i):
        return element.accel()[i]

    return tls.group_parameter(data, grouping_func, param_f, filt=filt, step=step)


def group_by_x_n_z(traj, i):
    loc = map(lambda a: round(a, 2), traj.pos()[i])
    return loc[0], loc[1]


def group_by_x_n_z2(traj, i):
    loc = map(lambda a: round(a - 0.005, 2) + 0.005, traj.pos()[i])
    return loc[0], loc[1]


def get_acc2(vel):
    sl = ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + vel + "_low.h5")
    sh = ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + vel + "_high.h5")

    acc_low = group_avarage_acc(sl, group_by_x_n_z2)
    acc_to_save = {}
    for key in acc_low.keys():
        acc_to_save[str(key)] = [acc_low[key][0].tolist(), acc_low[key][1]]
    tls.save_as_json(acc_to_save, "accel2_by_x_and_z_" + vel + "_lower")
    print("Lower done")

    acc_high = group_avarage_acc(sh, group_by_x_n_z2)
    acc_to_save = {}
    for key in acc_high.keys():
        acc_to_save[str(key)] = [acc_high[key][0].tolist(), acc_high[key][1]]
    tls.save_as_json(acc_to_save, "accel2_by_x_and_z_" + vel + "_higher")
    print("Higher done")

    m = tls.merge_dict(tls.read_json("accel2_by_x_and_z_" + vel + "_higher"),
                       tls.read_json("accel2_by_x_and_z_" + vel + "_lower"),
                       lambda a, b: [((np.array(a[0]) * a[1] + np.array(b[0]) * b[1]) / (a[1] + b[1])).tolist(),
                                     a[1] + b[1]])
    tls.save_as_json(m, "accel2_by_x_and_z_" + vel)
    print("DONE")


def get_acc(vel):
    sl = ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + vel + "_low.h5")
    sh = ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + vel + "_high.h5")

    acc_low = group_avarage_acc(sl, group_by_x_n_z)
    acc_to_save = {}
    for key in acc_low.keys():
        acc_to_save[key] = [acc_low[key][0].tolist(), acc_low[key][1]]
    tls.save_as_json(acc_to_save, "accel_by_x_and_z_" + vel + "_lower")
    print("Lower done")

    acc_high = group_avarage_acc(sh, group_by_x_n_z)
    acc_to_save = {}
    for key in acc_high.keys():
        acc_to_save[key] = [acc_high[key][0].tolist(), acc_high[key][1]]
    tls.save_as_json(acc_to_save, "accel_by_x_and_z_" + vel + "_higher")
    print("Higher done")

    m = tls.merge_dict(tls.read_json("accel_by_x_and_z_" + vel + "_higher"),
                       tls.read_json("accel_by_x_and_z_" + vel + "_lower"),
                       lambda a, b: [((np.array(a[0]) * a[1] + np.array(b[0]) * b[1]) / (a[1] + b[1])).tolist(),
                                     a[1] + b[1]])
    tls.save_as_json(m, "accel_by_x_and_z_" + vel)
    print("DONE")


def draw_quiver(vel):
    acc = tls.read_json("accel_by_x_and_z_" + vel)
    fig, ax = pplot.subplots()
    matx = np.zeros((18, 18))
    matz = np.zeros((18, 18))

    for key in acc.keys():
        if acc[key][1] < 10000:
            continue
        x = int(float(key.split(", ")[0].replace("(", "")) * 100)
        if x > 0:
            continue
        z = int(float(key.split(", ")[1].replace(")", "")) * 100)
        matx[z, -x] = math.sqrt(abs(-acc[key][0][0])) * np.sign(-acc[key][0][0])
        matz[z, -x] = math.sqrt(abs(acc[key][0][1])) * np.sign(acc[key][0][1])

    Y = np.zeros((18, 18))
    X = np.zeros((18, 18))
    for i in xrange(len(Y)):
        for j in xrange(len(Y)):
            Y[i, j] = i / 10.0
            X[i, j] = j / 10.0

    ax.quiver(X, Y, matx, matz, units="inches", scale=8)

    ax.set_xlabel(r"x/H")
    ax.set_ylabel(r"z/H")

    return fig, ax


def plot_accl(vel):
    fig, ax = pplot.subplots()
    scale, sax = pplot.subplots()
    acc = tls.read_json("accel_by_x_and_z_" + vel)
    vals_raw = []

    for item in acc.keys():
        if acc[item][1] < 10000:
            continue
        x = int(float(item.split(", ")[0].replace("(", "")) * 100)
        if x > 0:
            continue
        vals_raw.append(-acc[item][0][0])

    maximum = max(vals_raw)
    minimum = min(vals_raw)
    mat = np.zeros(shape=(18, 18, 3)).tolist()
    mat_s = np.zeros(shape=(1, 99, 3)).tolist()

    for key in acc.keys():
        x = int(float(key.split(", ")[0].replace("(", "")) * 100)
        if x > 0:
            continue
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

    sax.imshow(mat_s, extent=[minimum, maximum, 0, 1], aspect='auto')
    sax.set_xticks(map(lambda a: round(a, 2), np.linspace(minimum, maximum, 12)))
    ax.imshow(mat, extent=[0, 1.8, 0, 1.8], origin="lower", aspect='auto')

    ax.set_xlabel(r"$x/H$")
    ax.set_ylabel(r"$z/H$")

    return fig, ax, scale, sax


"""
Created on Mon Jul 23 12:50:22 2018

my test:
    sum_all_acc("2.5", air_density * 0.01 * 0.01 * 0.1)

@author: Alexey
"""
mass = air_density * 0.01 * 0.01 * 0.1


def sum_all_acc(vel, area=0.05 * 0.01, mult=mass, only_corner=True, version="2"):
    acc = tls.read_json("accel" + version + "_by_x_and_z_" + vel)
    acc_err = tls.read_json("Statistics/acc_nb_xz_mult_avgs_" + vel)
    total = {}
    count = {}
    num = {}
    err = {}
    Cd = {}
    Cd_g = {}
    for key in acc.keys():

        if only_corner and -float(key.split(", ")[0].replace('(', "")) <= 0.12:
            continue
        
        if key not in acc_err.keys():
            print key + " is missing"
            continue
        
        h = float(key.split(", ")[1].replace(")", ""))
        if h in total.keys():
            total[h] += np.array(acc[key][0]) * mult
            err[h][0] += sorted(acc_err[key], key=lambda a: a[0])[0][0] * mult
            err[h][1] += sorted(acc_err[key], key=lambda a: a[0])[-1][0] * mult
            count[h] += acc[key][1]
            num[h] += 1.0
        else:
            total[h] = np.array(acc[key][0]) * mult
            count[h] = acc[key][1]
            err[h] = [0, 0]
            err[h][0] = sorted(acc_err[key], key=lambda a: a[0])[0][0] * mult
            err[h][1] = sorted(acc_err[key], key=lambda a: a[0])[-1][0] * mult
            num[h] = 1.0
    tmp = raupach.get_drag_raupach(vel)["v"]
    for key in total.keys():
        total[key] = [total[key] / num[key], count[key]]
        Cd_g[key] = (-total[key][0][0] * 2) / (air_density * (float(vel) ** 2) * area), count[key]
        err[key][0] = abs((((err[key][0] / num[key]) * 2) / (air_density * (float(vel) ** 2) * area)) - Cd_g[key][0])
        err[key][1] = abs((((err[key][1] / num[key]) * 2) / (air_density * (float(vel) ** 2) * area)) - Cd_g[key][0])
        try:
            Cd[key] = (-total[key][0][0] * 2) / (air_density * (tmp[round(key * 100.0) - 0.5] ** 2) * area), count[key]
        except KeyError:
            pass
    return total, Cd, Cd_g, err
    
if __name__ == '__main__':
    pass
    #print sum_all_acc("2.5")
