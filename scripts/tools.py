#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 12:30:55 2018

@author: alexey
"""

#import flowtracks.io as ft
import numpy as np
import json
import matplotlib.pyplot as pplot

root = "C:/Users/theem/Desktop/Projects/alpha offline/AlphaResearch/"
def save_as_json(data, file_name, sort_keys=True, indent=4):
    with open(root + file_name + ".json", "w") as f:
        json.dump(data, f, sort_keys=sort_keys, indent=indent)
        
def read_json(file_name):
    with open(root + file_name + ".json", "r") as f:
        return json.load(f)
    
fig = None
ax = None
def p():
    global fig
    global ax
    fig, ax = pplot.subplots()
    
"""
Created on Sun Jul 15 15:19:06 2018

usage: 
    group_avarage_velocity(data, lambda t, i: group_by_height(t, i, 0, 0, 0))
where insted of 0 you put values for start end and jump

@author: alexey
"""
def group_by_height(traj, i, start, end, jump, unsafe = False):
    val = start
    if (start > 0.1 or end > 0.2 or jump > 0.05) and not unsafe:
        print("start = {}, end = {}, jump = {}. all in cm. are you sure you are correct?".format(start, end, jump)
              + " if so please use unsafe mode")
        raise Exception('Suspicious values inserted in unsafe mode')
    
    while (val <= end):
        if val <= traj.pos()[i, 1] < min(val + jump, end):
            return str(val) + " - " + str(min(val + jump, end))
        val += jump
    
    return "no group"

"""
Created on Mon Jul 16 10:34:15 2018

gets a flowtracks.Scene and a filter and return all trejectories that match
the filter (in a list)

@author: alexey
"""
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

def is_in_corner(traj):
       return -traj.pos()[0, 0] > 0.05 and -traj.pos()[0, 2] > 0.075

"""
Created on Mon Jul 16 10:34:15 2018

common use to get x vel from dict:
    get_data_from_dict(dic, lambda a: -a[0][0])

@author: alexey
"""
def get_data_from_dict(dic, func):
    ret = []
    for key in sorted(dic.keys()):
        ret.append(func(dic[key]))
    return ret

#   def to_wrold_coords(vector):
#      return [-vector[0], -vector[2], vector[1]]

# TODO make not super bad
def plot_data(x_axis, *yaxis):
    fig, ax = pplot.subplots()
    for item in yaxis:
        ax.plot(x_axis, item)
    return fig, ax

"""
Created on Sun Jul 15 15:19:06 2018

data - an array of trajectory objects

grouping_func - some function that takes a trajectory and an index and returns
a string. The index is the "time frame" that shold be refrenced. The string
should represent the group which the particle belongs to.

filter - A function that gets a trajectory and returns False to skip it

parameter_func - the function that gets the parameter to put in the groups

return value - a dictionery where the keys are the name of the groups and the
values are the parameter

@author: alexey
"""    
def group_parameter(data, grouping_func, parameter_func,
                    average = True,
                    filt=lambda a: True, 
                    step = 1):
    count = {}
    total = {}
    iterable = None
    c = 0
    
    if type(data) is ft.Scene:
        iterable = data.iter_trajectories()
    else:
        iterable = data
    
    for element in iterable:
        c += 1
        if c % step != 0:
            continue
        if c % 200000 == 0:
            print("200,000 units are ready, with a million more well on the way")
        if not filt(element):
            continue
        point_count = len(element.velocity())
        for i in xrange(point_count):
            loc = grouping_func(element, i)
            if loc in count.keys():
                count[loc] += 1.0
                total[loc] += parameter_func(element, i)
            else:
                count[loc] = 1.0
                total[loc] = parameter_func(element, i)
    if not average:
        return total
    for key in count.keys():
        total[key] = [(total[key] / count[key]), count[key]]
    return total

"""
Created on Sun Jul 15 15:19:06 2018

usage - 
    group_avarage_velocity(data, group_by_location)

@author: alexey
"""
def group_by_location(traj, i):
    return tuple(map(lambda a: round(a, 2), traj.pos()[i]))

def plot_def(prop, filt = lambda a: a, start = 0, end = None, mod = lambda a: a):
    lis = []
    for key in sorted(_.keys()):
        k = mod(key)  
        lis.append((filt(_[key]), k))
    lis = lis[start:end]
    ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), prop)

"""
copy paste tools

lis = []
for h in xrange(0, 16, 1):
    key = h + 0.5
    if key in _.keys():    
        lis.append((_[key], key / 100.0))
        
ax.plot(map(lambda a: a[1], lis), map(lambda a: a[0], lis), "mo-")

"""
