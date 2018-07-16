#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 15:19:06 2018

@author: alexey
"""

import flowtracks.io as ft
import numpy as np
import json
#import pyplotlib.pyplot as pplot

air_density = 1.2041 # kg / m^3
area_tall = 0.1 * 0.05 # cm^2
area_short = 0.05 * 0.05 # cm^2
drag_coefficient = 2.05

"""
Created on Sun Jul 15 15:19:06 2018

data - an array of trajectory objects

grouping_func - some function that takes a trajectory and an index and returns
a string. The index is the "time frame" that shold be refrenced. The string
should represent the group which the particle belongs to.

filter - A function that gets a trajectory and returns False to skip it

return value - a dictionery where the keys are the name of the groups and the
values are the average velocity in that group

@author: alexey
"""    
def group_avarage_velocity(data, grouping_func,
                           filter=lambda a: True, isList = False):
    
    count = {}
    total = {}
    iterable = None
    
    if isList:
        iterable = data
    else:
        iterable = data.iter_trajectories()
    
    for element in iterable:
        
        if not filter(element):
            continue
        
        point_count = len(element.velocity())
        for i in xrange(point_count):
            loc = grouping_func(element, i)
            if loc in count.keys():
                count[loc] += 1
                total[loc] += element.velocity()[i]
            else:
                count[loc] = 1
                total[loc] = element.velocity()[i]
    
    for key in count.keys():
        total[key] = [(total[key] / count[key]).tolist(), count[key]]
    
    return total

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
      
def estimate_drag_Cd(velocity, area, density=air_density, coefficient=drag_coefficient):
    return 0.5 * coefficient * (velocity ** 2) * area * density
  
root = "/home/ron/Desktop/Alexey/"
def save_as_json(data, file_name, sort_keys=False, indent=1):
    with open(root + file_name + ".json", "w") as f:
        json.dump(data, f, sort_keys=sort_keys, indent=indent)
        
def read_json(file_name):
    with open(root + file_name + ".json", "r") as f:
        return json.load(f)
