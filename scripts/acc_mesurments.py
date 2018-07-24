#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:50:22 2018

@author: Alexey
"""

import tools as tls
import numpy as np
import matplotlib.pyplot as pplot
import flowtracks.io as ft
import math

def group_avarage_acc(data, grouping_func,
                           filt=lambda a: True, 
                           step = 1):
    def param_f(element, i):
        return element.accel()[i]
    return tls.group_parameter(data, grouping_func, param_f, filt=filt, step=step)

def group_by_x_n_z(traj, i):
    loc = map(lambda a: round(a, 2), traj.pos()[i])
    return loc[0], loc[1]

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
        matx[z, -x] = math.sqrt(math.sqrt(abs(-acc[key][0][0]))) * np.sign(-acc[key][0][0])
        matz[z, -x] = math.sqrt(math.sqrt(abs(acc[key][0][1]))) * np.sign(acc[key][0][1])
    
    ax.quiver(matx, matz, units="xy")
    
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
    mat_s = np.zeros(shape=(1, 18, 3)).tolist()
    
    for key in acc.keys():
        if acc[key][1] < 10000:
            continue
        x = int(float(key.split(", ")[0].replace("(", "")) * 100)
        if x > 0:
            continue
        z = int(float(key.split(", ")[1].replace(")", "")) * 100)
        val = ((-acc[key][0][0] - minimum) / (maximum - minimum)) * 255.0
        mat[z][-x][0] = np.ubyte(val)
        mat[z][-x][1] = np.ubyte(255 - val)
        mat[z][-x][2] = np.ubyte(0)
        ax.text(-x, z, round(-acc[key][0][0], 1), ha="center", va="center", color="w")
    
    val = 255
    ind = 0
    while val >= 0:
        mat_s[0][ind][0] = np.ubyte(val)
        mat_s[0][ind][1] = np.ubyte(255 - val)
        mat_s[0][ind][2] = np.ubyte(0)
        ind += 1
        val -= 15
        
    sax.imshow(mat_s,  extent=[minimum, maximum, 0, 1], aspect='auto')
    sax.set_xticks(map(lambda a: round(a, 2), np.linspace(minimum, maximum, 12)))
    ax.imshow(mat, origin="lower", aspect='auto')
    
    return fig, ax, scale, sax
    

"""
Created on Mon Jul 23 12:50:22 2018

my test:
    sum_all_acc("2.5", air_density * 0.01 * 0.01 * 0.1)

@author: Alexey
"""
mass = air_density * 0.01 * 0.01 * 0.1
def sum_all_acc(vel, mult=mass, only_corner = False):
    acc = tls.read_json("accel_by_x_and_z_" + vel)
    total = {}
    count = {}
    for key in acc.keys():
        
        if only_corner and -float(key.split(", ")[0].replace('(', "")) <= 0.1:
            continue
            
        h = float(key.split(", ")[1].replace(")", ""))
        if h in total.keys():
            total[h] += np.array(acc[key][0])*mult
            count[h] += acc[key][1]
        else:
            total[h] = np.array(acc[key][0])*mult
            count[h] = acc[key][1]
    for key in total.keys():
        total[key] = [total[key], count[key]]
    return total
        