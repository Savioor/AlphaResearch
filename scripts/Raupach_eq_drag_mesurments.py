#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 12:36:31 2018

@author: ron
"""

import tools as tls
import numpy as np
import flowtracks.io as ft
from Cd_drag_mesurment import group_avarage_velocity

def calculate_midpoint_derivative(prev, nex, h):
    return (1.0 / (2.0*h)) * (nex - prev)

def calculate_start_derivative(first, second, third, h):
    return (1.0 / (2.0*h)) * (-3 * first + 4 * second - third)

def calculate_end_derivative(last, prelast, preprelast, h):
    return (1.0 / (2.0*h)) * (preprelast - 4*prelast + 3*last)


def_accuracy = 10 ** 4
area_by_volume = (0.01*0.05)/(0.1*0.15*0.01)
def get_drag_raupach(velocity, linear = False, area = 0.0005, accuracy=def_accuracy):
    
    to_ret = {}
    
    velocity_data = tls.read_json("cd_data/avg_vel_by_height_" + velocity)
    z_dir_vel = {}
    x_dir_vel = {}
    for key in velocity_data.keys():
        if velocity_data[key][1] < accuracy:
            continue
        ind = (float(key.split(" - ")[0]) * 100 + float(key.split(" - ")[1]) * 100) / 2.0
        x_dir_vel[ind] = -velocity_data[key][0][0]
        z_dir_vel[ind] = velocity_data[key][0][1]
    
    to_ret["v"] = x_dir_vel
    to_ret["w"] = z_dir_vel
    
    rey_data = tls.read_json("raupach_data/rey_stress_" + velocity)
    rey_stress = {}
    
    for key in rey_data:
        if rey_data[key][1] < accuracy:
            continue
        ind = (float(key.split(" - ")[0]) * 100 + float(key.split(" - ")[1]) * 100) / 2.0
        rey_stress[ind] = rey_data[key][0]
        
    disp_data = tls.read_json("raupach_data/disp_stress_" + velocity)
    disp_stress = {}
    
    for key in disp_data:
        if disp_data[key][1] < accuracy:
            continue
        ind = (float(key.split(" - ")[0]) * 100 + float(key.split(" - ")[1]) * 100) / 2.0
        disp_stress[ind] = disp_data[key][0]
        
    to_ret["rey stress"] = rey_stress
    to_ret["disp stress"] = disp_stress
    
    dv = {}
    drs = {}
    dds = {}
    
    skv = sorted(x_dir_vel.keys())
    skrs = sorted(rey_stress.keys())
    skds = sorted(disp_stress.keys())
    
    if not linear:
        for h in range(0, 16, 1):
            key = h + 0.5
            
            v = x_dir_vel
            if key in skv:
                if skv.index(key) == 0:
                    dv[key] = calculate_start_derivative(v[key], v[key + 1], v[key + 2], 0.01)
                elif skv.index(key) == len(skv) - 1:
                    dv[key] = calculate_end_derivative(v[key], v[key - 1], v[key - 2], 0.01)
                else:
                    dv[key] = calculate_midpoint_derivative(v[key - 1], v[key + 1], 0.01)
            
            rs = rey_stress
            if key in skrs:
                if skrs.index(key) == 0:
                    drs[key] = calculate_start_derivative(rs[key], rs[key + 1], rs[key + 2], 0.01)
                elif skrs.index(key) == len(skv) - 1:
                    drs[key] = calculate_end_derivative(rs[key], rs[key - 1], rs[key - 2], 0.01)
                else:
                    drs[key] = calculate_midpoint_derivative(rs[key - 1], rs[key + 1], 0.01)
            
            ds = disp_stress
            if key in skds:
                if skds.index(key) == 0:
                    dds[key] = calculate_start_derivative(ds[key], ds[key + 1], ds[key + 2], 0.01)
                elif skv.index(key) == len(skv) - 1:
                    dds[key] = calculate_end_derivative(ds[key], ds[key - 1], ds[key - 2], 0.01)
                else:
                    dds[key] = calculate_midpoint_derivative(ds[key - 1], ds[key + 1], 0.01)
    else:
        for h in range(0, 16, 1):
            key = h + 0.5
            dv[key] = (x_dir_vel[skv[-1]] - x_dir_vel[skv[0]]) / ((skv[-1] - skv[0]) / 100.0)
            drs[key] = (rey_stress[skrs[-1]] - rey_stress[skrs[0]]) / ((skrs[-1] - skrs[0]) / 100.0)
            dds[key] = (disp_stress[skds[-1]] - disp_stress[skds[0]]) / ((skds[-1] - skds[0]) / 100.0)
            
    
    to_ret["v gradient"] = dv
    to_ret["rey stress gradient"]  = drs
    to_ret["disp stress gradient"] = dds
    
    pressure_grad = 0.0
    c = 0
    for key in drs:
        if key > 12:
            c += 1
            pressure_grad += drs[key]
    pressure_grad /= c
    pressure_grad *= -1
    to_ret["p grad"] = pressure_grad
    pressure_grad = 0.0
    
    drag = {}
    z_times_dv = {}
    
    for h in range(0, 10, 1):
        key = h + 0.5
        if key in x_dir_vel.keys() and key in rey_stress.keys() and key in disp_stress.keys():
            z_times_dv[key] = z_dir_vel[key]*dv[key]    
            drag[key] = z_dir_vel[key]*dv[key] + drs[key] + dds[key] + pressure_grad
    
    to_ret["w*dv"] = z_times_dv
    to_ret["drag"] = drag
    
    c_d = {}
    c_d_b = {}
    
    for key in drag.keys():
        c_d[key] = drs[key] / (-0.5 * (float(velocity) ** 2) * area)
        c_d_b[key] = drs[key] / (-0.5 * area * (x_dir_vel[key]**2))
    
    to_ret["Cd"] = c_d
    to_ret["Cd br"] = c_d_b
    
    return to_ret
    
    

def get_reynolds_stress(data, avg_vel_by_loc, start=0, end=0.18, step=0.01):
    
    if type(avg_vel_by_loc) is str:
        avg_vel_by_loc = tls.read_json(avg_vel_by_loc)
    
    def param_f(elem, i):
        position = str(tls.group_by_location(elem, i)).replace("-0.0", "0.0")
        return (avg_vel_by_loc[position][0][0] - elem.velocity()[i][0]) * \
                (-avg_vel_by_loc[position][0][1] + elem.velocity()[i][1])
        
    
    return tls.group_parameter(data, 
                           lambda t, i: tls.group_by_height(t, i, start, end, step),
                           param_f)

def get_dispersive_stress(data, avg_vel_by_loc, avg_vel_by_h, start=0, end=0.18, step=0.01):
    
    if type(avg_vel_by_loc) is str:
        avg_vel_by_loc = tls.read_json(avg_vel_by_loc)
    if type(avg_vel_by_h) is str:
        avg_vel_by_h = tls.read_json(avg_vel_by_h)
    
    def param_f(elem, i):
        position = tls.group_by_location(elem, i)
        pos_str = str(position).replace("-0.0", "0.0")
        height = str(abs(position[1])) + " - " + str(abs(position[1]) + step)
        if height not in avg_vel_by_h.keys():
            height = str(abs(position[1]) - step) + " - " + str(abs(position[1]))
        return (-avg_vel_by_loc[pos_str][0][0] + avg_vel_by_h[height][0][0]) * \
                (avg_vel_by_loc[pos_str][0][1] - avg_vel_by_h[height][0][1])
        
    
    return tls.group_parameter(data, 
                           lambda t, i: tls.group_by_height(t, i, start, end, step),
                           param_f)

def auto_disp_stress_calculator(speed):
    
    high_stress = get_dispersive_stress(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_high.h5"),
                        "raupach_data/avg_vel_by_loc_" + speed,
                        "cd_data/avg_vel_by_height_" + speed)
    print("Stress higher calculated")
    print(high_stress)
    
    low_stress = get_dispersive_stress(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_low.h5"),
                        "raupach_data/avg_vel_by_loc_" + speed,
                        "cd_data/avg_vel_by_height_" + speed)
    print("Stress lower calculeted")
    print(low_stress)
    
    tls.save_as_json(high_stress, "raupach_data/disp_stress_higher_" + speed)
    tls.save_as_json(low_stress, "raupach_data/disp_stress_lower_" + speed)
    
    merged_stress = tls.merge_dict(high_stress, low_stress,
                               lambda a, b: [(a[0] * a[1] + b[0] * b[1]) / (a[1] + b[1]),
                                             a[1] + b[1]])
    
    tls.save_as_json(merged_stress, "raupach_data/disp_stress_" + speed)

def auto_rey_stress_calculator(speed, skip_vel = True):
    if not skip_vel:
        get_velocity_by_loc(speed)
    
    high_stress = get_reynolds_stress(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_high.h5"),
                        "raupach_data/avg_vel_by_loc_" + speed)
    print("Stress higher calculated")
    print(high_stress)
    
    low_stress = get_reynolds_stress(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_low.h5"),
                        "raupach_data/avg_vel_by_loc_" + speed)
    print("Stress lower calculeted")
    print(low_stress)
    
    tls.save_as_json(high_stress, "raupach_data/rey_stress_higher_" + speed)
    tls.save_as_json(low_stress, "raupach_data/rey_stress_lower_" + speed)
    
    merged_stress = tls.merge_dict(high_stress, low_stress, 
                               lambda a, b: [(a[0] * a[1] + b[0] * b[1]) / (a[1] + b[1]),
                                             a[1] + b[1]])
    
    tls.save_as_json(merged_stress, "raupach_data/rey_stress_" + speed)


def get_velocity_by_loc(speed, groups=1, prefix=""):

    higher_avg_vel = group_avarage_velocity(
        ft.Scene("C:/Users/theem/Desktop/Projects/alpha offline/Data/traj_" + speed + "_high.h5")
                , tls.group_by_location, groups=groups)
    print("Higher vel calculated")
        
    higer_dic = {}
    for key in higher_avg_vel.keys():
        higer_dic[str(key).replace("-0.0", "0.0")] = higher_avg_vel[key]
        
        
    tls.save_as_json(higer_dic, "raupach_data/" + prefix + "avg_vel_by_loc_higher_" + speed)

        
    lower_avg_vel = group_avarage_velocity(
            ft.Scene("C:/Users/theem/Desktop/Projects/alpha offline/Data/traj_" + speed + "_low.h5")
            , tls.group_by_location, groups=groups)
    print("Lower vel calculated")
        
        
    lower_dic = {}
    for key in lower_avg_vel.keys():
        lower_dic[str(key).replace("-0.0", "0.0")] = lower_avg_vel[key]
    
    tls.save_as_json(lower_dic, "raupach_data/" + prefix + "avg_vel_by_loc_lower_" + speed)
    
    merged = tls.merge_dict(lower_dic, higer_dic, 
               lambda a, b: [((np.array(a[0]) * a[1] 
               + np.array(b[0]) * b[1]) / (a[1] + b[1])).tolist(), a[1] + b[1]])
    
    tls.save_as_json(merged, "raupach_data/" + prefix + "avg_vel_by_loc_" + speed)

if __name__ == "__main__":
    print "started"
    get_velocity_by_loc("2.5", groups=10, prefix="goruped_")
    