#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 12:36:31 2018

@author: ron
"""

import tools as tls
import numpy as np
import flowtracks.io as ft

def get_reynolds_stress(data, avg_vel_by_loc, start=0, end=0.18, step=0.01):
    
    if type(avg_vel_by_loc) is str:
        avg_vel_by_loc = tls.read_json(avg_vel_by_loc)
    
    def param_f(elem, i):
        position = str(tls.group_by_location(elem, i)).replace("-0.0", "0.0")
        return -elem.velocity()[i][0] * elem.velocity()[i][1] \
                    + avg_vel_by_loc[position][0][0] * avg_vel_by_loc[position][0][1]
        
    
    return tls.group_parameter(data, 
                           lambda t, i: tls.group_by_height(t, i, start, end, step),
                           param_f)

def auto_rey_stress_calculator(speed, skip_vel = False):
    if not skip_vel:
        
        higher_avg_vel = group_avarage_velocity(
                ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_high.h5")
                , tls.group_by_location)
        print "Higher vel calculated"
        print higher_avg_vel
        
        lower_avg_vel = group_avarage_velocity(
                ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_low.h5")
                , tls.group_by_location)
        print "Lower vel calculated"
        print lower_avg_vel
        
        higer_dic = {}
        for key in higher_avg_vel.keys():
            higer_dic[str(key).replace("-0.0", "0.0")] = higher_avg_vel[key]
            
        lower_dic = {}
        for key in lower_avg_vel.keys():
            lower_dic[str(key).replace("-0.0", "0.0")] = lower_avg_vel[key]
        
        tls.save_as_json(higer_dic, "raupach_data/avg_vel_by_loc_higher_" + speed)
        tls.save_as_json(lower_dic, "raupach_data/avg_vel_by_loc_lower_" + speed)
        
        merged = tls.merge_dict(lower_dic, higer_dic, 
                   lambda a, b: [((np.array(a[0]) * a[1] 
                   + np.array(b[0]) * b[1]) / (a[1] + b[1])).tolist(), a[1] + b[1]])
        
        tls.save_as_json(merged, "raupach_data/avg_vel_by_loc_" + speed)
    
    high_stress = get_reynolds_stress(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_high.h5"),
                        "raupach_data/rey_stress_" + speed)
    print "Stress lower calculated"
    print high_stress
    
    low_stress = get_reynolds_stress(ft.Scene("/home/ron/Desktop/Alexey/the_dataset/traj_" + speed + "_low.h5"),
                        "raupach_data/rey_stress_" + speed)
    print "Stress higher calculeted"
    print low_stress
    
    tls.save_as_json(high_stress, "raupach_data/rey_stress_higher_" + speed)
    tls.save_as_json(low_stress, "raupach_data/rey_stress_lower_" + speed)
    
    merged_stress = tls.merge_dict(high_stress, low_stress, 
                               lambda a, b: [(a[0] * a[1] + b[0] * b[1]) / (a[1] + b[1]),
                                             a[1] + b[1]])
    
    tls.save_as_json(merged_stress, "raupach_data/rey_stress_" + speed)

