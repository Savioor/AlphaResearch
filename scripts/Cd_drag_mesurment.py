#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 15:19:06 2018

@author: alexey
"""

import tools as tls

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
        

def estimate_drag_Cd(velocity, area, density=air_density, coefficient=drag_coefficient):
    return 0.5 * coefficient * (velocity ** 2) * area * density
    

minimum_acc = 10 ** 4
def calc_vel_and_drag_from_data_Cd(data, area, acc=minimum_acc):
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
