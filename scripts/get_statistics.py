import flowtracks.io as ft
from Cd_drag_mesurment import calc_vel_and_drag_from_data_Cd, general, nb
from tools import save_as_json, read_json, merge_dict, group_by_height, is_in_corner
import acc_mesurments
from math import sqrt
import random

root = "C:\\Users\\theem\\Desktop\\Projects\\alpha offline\\Data\\"
def main():
      
    #print "doing vel 2"
    #save_as_json(average_acc_in_groups(ft.Scene(root + "traj_2.5_high.h5")), "Statistics/acc_nb_xz_mult_avgs_higher_2.5")
    #save_as_json(average_acc_in_groups(ft.Scene(root + "traj_2.5_low.h5")), "Statistics/acc_nb_xz_mult_avgs_lower_2.5")
    #print "2.5 done!"
    #save_as_json(average_acc_in_groups(ft.Scene(root + "traj_4.0_high.h5")), "Statistics/acc_nb_xz_mult_avgs_higher_4.0")
    #save_as_json(average_acc_in_groups(ft.Scene(root + "traj_4.0_low.h5")), "Statistics/acc_nb_xz_mult_avgs_lower_4.0")
    #print "Done!"
    
    lower25 = read_json("Statistics/acc_nb_xz_mult_avgs_higher_2.5")
    higher25 = read_json("Statistics/acc_nb_xz_mult_avgs_lower_2.5")
    save_as_json(merge_dict(lower25, higher25, merge_long_dict), "Statistics/acc_nb_xz_mult_avgs_2.5")
    
    lower40 = read_json("Statistics/acc_nb_xz_mult_avgs_higher_4.0")
    higher40 = read_json("Statistics/acc_nb_xz_mult_avgs_lower_4.0")
    save_as_json(merge_dict(lower40, higher40, merge_long_dict), "Statistics/acc_nb_xz_mult_avgs_4.0")
    
    


         
def merge_long_dict(elem1, elem2):
    return [
    [
    (elem1[i][0]*elem1[i][1] + elem2[i][0]*elem2[i][1]) 
    / (elem1[i][1] + elem2[i][1] if elem1[i][1] + elem2[i][1] != 0 else 1),
    
    elem1[i][1] + elem2[i][1]
    ] for i in xrange(len(elem1))]

    
def average_acc_in_groups(data,
            filt=lambda a: True, 
            step = 1,
            groups=5):
    count = {}
    total = {}
    iterable = None
    c = 0
    
    if type(data) is ft.Scene:
        iterable = data.iter_trajectories()
    else:
        iterable = data
    
    grouping_func = lambda a, b: str(acc_mesurments.group_by_x_n_z2(a, b))
    
    print "Started running"
    
    for element in iterable:
        c += 1
        if c % step != 0:
            continue
        if c % 200000 == 0:
            print("200,000 units are ready, with a million more well on the way")
        if not filt(element):
            continue
        point_count = len(element.accel())
        
        for i in xrange(point_count):
            loc = grouping_func(element, i)
            if loc in count.keys():
                home_ind = random.choice(xrange(groups))
                count[loc][home_ind] += 1.0
                total[loc][home_ind] -= element.accel()[i][0]
         
            else:
                count[loc] = [0.0 for j in xrange(groups)]
                total[loc] = [0.0 for j in xrange(groups)]
                home_ind = random.choice(xrange(groups))
                count[loc][home_ind] += 1.0
                total[loc][home_ind] -= element.accel()[i][0]
    
    for key in total.keys():
        total[key] = [(total[key][i] / (count[key][i] if count[key][i] != 0 else 1.0), count[key][i]) for i in xrange(groups)]
    
    return total 

def average_w_vel_in_groups(data,
            filt=lambda a: True, 
            step = 1,
            groups=10):
    count = {}
    total = {}
    iterable = None
    c = 0
    
    if type(data) is ft.Scene:
        iterable = data.iter_trajectories()
    else:
        iterable = data
    
    grouping_func = lambda t, i: group_by_height(t, i, 0, 0.18, 0.01)
    
    print "Started running"
    
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
                home_ind = random.choice(xrange(groups))
                count[loc][home_ind] += 1.0
                total[loc][home_ind] += element.velocity()[i][1]
         
            else:
                count[loc] = [0.0 for j in xrange(groups)]
                total[loc] = [0.0 for j in xrange(groups)]
                home_ind = random.choice(xrange(groups))
                count[loc][home_ind] += 1.0
                total[loc][home_ind] += element.velocity()[i][1]
    
    for key in total.keys():
        total[key] = [(total[key][i] / (count[key][i] if count[key][i] != 0 else 1.0), count[key][i]) for i in xrange(groups)]
    
    return total
    
def average_vel_in_groups(data,
            filt=lambda a: True, 
            step = 1,
            groups=10):
    count = {}
    total = {}
    iterable = None
    c = 0
    
    if type(data) is ft.Scene:
        iterable = data.iter_trajectories()
    else:
        iterable = data
    
    grouping_func = lambda t, i: group_by_height(t, i, 0, 0.18, 0.01)
    
    print "Started running"
    
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
                home_ind = random.choice(xrange(groups))
                count[loc][home_ind] += 1.0
                total[loc][home_ind] -= element.velocity()[i][0]
         
            else:
                count[loc] = [0.0 for j in xrange(groups)]
                total[loc] = [0.0 for j in xrange(groups)]
                home_ind = random.choice(xrange(groups))
                count[loc][home_ind] += 1.0
                total[loc][home_ind] -= element.velocity()[i][0]
    
    for key in total.keys():
        total[key] = [(total[key][i] / (count[key][i] if count[key][i] != 0 else 1.0), count[key][i]) for i in xrange(groups)]
    
    return total
   
std_root = "sum_of_sqr_diff_from_avg_"
def get_std_h(h, vel):
    data = read_json(std_root + str(vel))
    relevant = str(filter(lambda a: abs(h - float(a)) < 0.0001, data.keys())[0])
    print relevant
    return sqrt(data[relevant][0] / (data[relevant][1] - 1))
    

def find_avg(h, file_path):
    avgs = calc_vel_and_drag_from_data_Cd(file_path)["x_velocities"]
    relevant =  filter(lambda a: abs(h - a[1]) < 0.0001, avgs)
    if len(relevant) == 0:
        return 0
    return relevant[0][0]
    
def get_std_v(data, velocity,
            average = False,
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
    
    grouping_func = lambda t, i: group_by_height(t, i, 0, 0.18, 0.01)
    
    print "Started running"
    
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
            rel_avg = find_avg(loc, general + velocity)
            if loc in count.keys():
                count[loc] += 1.0
                total[loc] += (element.velocity()[i][0] + rel_avg)**2
            else:
                count[loc] = 1.0
                total[loc] = (element.velocity()[i][0] + rel_avg)**2
    if not average:
        for key in count.keys():
            total[key] = [total[key], count[key]]
        return total
    for key in count.keys():
        total[key] = [(total[key] / count[key]), count[key]]
    return total


if __name__ == "__main__":
    main()
