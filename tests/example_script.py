#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 14:14:48 2018

@author: ron
"""

from flowtracks.io import Scene


# example for calculating mean velcoity of trajectories:

s = Scene('/home/ron/Desktop/Alexey/the_dataset/traj_2.5_high.h5')

sum_v = 0.0

c = 0

for trajectory in s.iter_trajectories():
    v = trajectory.velocity()
    for i in range(len(trajectory)):
        sum_v += v[i,:]
        c += 1
        
print sum_v / c
    
    
# example for picking trajectpries:

t = []

for trajectory in s.iter_trajectories():
    p = trajectory.pos()
    
    if 0.1 < p[0,1] < 0.11:
        t.append(trajectory)