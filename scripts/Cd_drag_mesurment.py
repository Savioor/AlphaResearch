#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 15:19:06 2018

@author: alexey
"""

from functools import reduce
import tools as tls
import matplotlib.pyplot as pplot
#import flowtracks.io as ft
import numpy as np

air_density = 1.2041 # kg / m^3
area_tall = 0.1 * 0.05 # cm^2
area_short = 0.05 * 0.05 # cm^2
drag_coefficient = 2.05 


def group_avarage_velocity(data, grouping_func,
                           filt=lambda a: True, 
                           step = 1):
    def param_f(element, i):
        return element.velocity()[i]
    return tls.group_parameter(data, grouping_func, param_f, filt=filt, step=step)
        
def plot_Cd_Fox():
    fig, ax = pplot.subplots()
    vfig, vax = pplot.subplots()
    drags = [
        calc_vel_and_drag_from_data_Cd(general + "2.5")["drag_list"][:-7],
        calc_vel_and_drag_from_data_Cd(general + "4.0")["drag_list"][:-7],
        calc_vel_and_drag_from_data_Cd(nb + "2.5")["drag_list"],
        calc_vel_and_drag_from_data_Cd(nb + "4.0")["drag_list"]
       ]
    vels = [
        calc_vel_and_drag_from_data_Cd(general + "2.5")["x_velocities"][:-7],
        calc_vel_and_drag_from_data_Cd(general + "4.0")["x_velocities"][:-7],
        calc_vel_and_drag_from_data_Cd(nb + "2.5")["x_velocities"],
        calc_vel_and_drag_from_data_Cd(nb + "4.0")["x_velocities"]
    ]
    lines = [
        "c+-",
        "g+-",
        "co--",
        "go--"
    ]
    labels = [
        "2.5 m/s total avg",
        "4.0 m/s total avg",
        "2.5 m/s near building avg",
        "4.0 m/s near building avg"
    ]
    vel = [
        2.5,
        4.0,
        2.5,
        4.0
    ]
    for t in range(len(drags)):
        ax.plot(list(map(lambda a: a[1] * 10.0, drags[t])),
                list(map(lambda a: a[0] / (0.5 * air_density * 0.01 * 0.05 * (vel[t] ** 2)), drags[t])), lines[t], label=labels[t])
        vax.plot(list(map(lambda a: a[1] * 10.0, vels[t])),
                 list(map(lambda a: a[0], drags[t])), lines[t],
                 label=labels[t])

    vax.legend()
    vax.set_xlabel("z/H")
    vax.set_ylabel("Velocity (m/s)")
    ax.legend()
    ax.set_xlabel("z/H")
    ax.set_ylabel(r"$\frac{2\cdot F_D}{\rho A U^2_{\infty}}$", size = 16)

    return fig, ax, vfig, vax


def estimate_drag_Cd(velocity, area, density=air_density, coefficient=drag_coefficient):
    return 0.5 * coefficient * (velocity ** 2) * area * density

def get_average_velocity(speed):
    low_speed = group_avarage_velocity(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_low.h5"),
                           lambda t, i: tls.group_by_height(t, i, 0, 0.18, 0.01))
    high_speed = group_avarage_velocity(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_high.h5"),
                           lambda t, i: tls.group_by_height(t, i, 0, 0.18, 0.01))        
    
    tls.save_as_json(low_speed, "cd_data/avg_vel_by_height_" + speed + "_lower")
    tls.save_as_json(high_speed, "cd_data/avg_vel_by_height_" + speed + "_higher")
    
    mrg = tls.merge_dict(low_speed, high_speed, 
    lambda a, b: [ ((np.array(a[0]) * a[1] + np.array(b[0]) * b[1]) / (a[1] + b[1])).tolist(),
     a[1] + b[1]])
    
    tls.save_as_json(mrg, "cd_data/avg_vel_by_height_" + speed)
    
minimum_acc = 10 ** 4
general = "cd_data/avg_vel_by_height_"
nb = "cd_data/nb_"
def calc_vel_and_drag_from_data_Cd(data, area=0.0005, acc=minimum_acc):
    ret = {}
    
    if type(data) is str:
        data = tls.read_json(data)
        
    x_vel = []
    for key in sorted(data.keys()):
        if data[key][1] < acc or key == "no group":
            continue
        
        key_splat = key.split(' - ')
        height = (float(key_splat[0]) + float(key_splat[1])) / 2
        x_vel.append([-data[key][0][0], height])
    
    ret["x_velocities"] = x_vel
    
    drag_list = []
    for elem in x_vel:
        drag_list.append([estimate_drag_Cd(elem[0], area), elem[1]])
    
    ret["drag_list"] = drag_list
    
    ret["drag"] = reduce(lambda a, b: a + b[0], drag_list, 0)
    
    return ret

fig, ax, vfig, vax = plot_Cd_Fox()
fig.show()
vfig.show()
pplot.show()
