#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 12:36:31 2018

@author: ron
"""

import tools as tls
import numpy as np

def get_reynolds_stress(data, avg_vel_by_loc, start=0, end=0.14, step=0.01):
    
    if type(avg_vel_by_loc) is str:
        avg_vel_by_loc = tls.read_json(avg_vel_by_loc)
    
    def param_f(elem, i):
        try:
            position = str(tls.group_by_location(elem, i))
            return -elem.velocity()[i][0] * elem.velocity()[i][1] \
                    + avg_vel_by_loc[position][0][0] * avg_vel_by_loc[position][0][1]
        except KeyError:
            return 0
    
    return tls.group_parameter(data, 
                           lambda t, i: tls.group_by_height(t, i, start, end, step),
                           param_f)
