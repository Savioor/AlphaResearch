#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 10:34:15 2018

@author: alexey
"""

import json
import matplotlib.pyplot as pplot


root = "/home/ron/Desktop/Alexey/AlphaResearch/"
def save_as_json(data, file_name, sort_keys=False, indent=1):
    with open(root + file_name + ".json", "w") as f:
        json.dump(data, f, sort_keys=sort_keys, indent=indent)
        
def read_json(file_name):
    with open(root + file_name + ".json", "r") as f:
        return json.load(f)

"""
Created on Sun Jul 15 15:19:06 2018

usage: 
group_avarage_velocity(data, lambda t, i: group_by_height(t, i, 0, 0, 0))
where insted of 0 you put values for start end and jump

@author: alexey
"""
def group_by_height(traj, i, start, end, jump):
    val = start
    
    while (val <= end):
        if val <= traj.pos()[i, 1] < min(val + jump, end):
            return str(val) + " - " + str(min(val + jump, end))
        val += jump
    
    return "no group"

def filter_trajectories(data, filt):
    ret = []
    for traj in data.iter_trajectories():
        if filt(traj):
            ret.append(traj)
    return ret

"""
Created on Mon Jul 16 10:34:15 2018

example (avg to list of avges) -
merge_dict(file1, file2, 
lambda a, b: [ ((np.array(a[0]) * a[1] + np.array(b[0]) * b[1]) / (a[1] + b[1])).tolist(),
 a[1] + b[1]])

@author: alexey
"""
def merge_dict(dict1, dict2, merge_func, ignore_1 = False, ignore_2 = False):
    newd = {}
    for key in dict1.keys():
        if key in dict2.keys():
            newd[key] = merge_func(dict1[key], dict2[key])
        elif not ignore_1:
            newd[key] = dict1[key]
    if ignore_2:
        return newd
    for key in filter(lambda k: k not in dict1.keys(), dict2.keys()):
        newd[key] = dict2[key]
    return newd

def to_wrold_coords(vector):
    return [-vector[0], -vector[2], vector[1]]

def plot_data(x_axis, *yaxis):
    fig, ax = pplot.subplots()
    for item in yaxis:
        ax.plot(x_axis, item)
    return fig, ax

