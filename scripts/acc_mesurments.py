#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:50:22 2018

@author: ron
"""

import tools as tls
import numpy as np
import flowtracks.io as ft

def group_avarage_acc(data, grouping_func,
                           filt=lambda a: True, 
                           step = 1):
    def param_f(element, i):
        return element.accel()[i]
    return tls.group_parameter(data, grouping_func, param_f, filt=filt, step=step)

def group_by_x_n_z(traj, i):
    loc = map(lambda a: round(a, 2), traj.pos()[i])
    return loc[0], loc[1]
    