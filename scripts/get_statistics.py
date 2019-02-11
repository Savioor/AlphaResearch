import flowtracks.io as ft
from Cd_drag_mesurment import calc_vel_and_drag_from_data_Cd, general, nb
from tools import save_as_json, read_json, merge_dict
from math import sqrt

root = "C:\\Users\\theem\\Desktop\\Projects\\alpha offline\\Data\\"
def main():
    save_as_json({"some_key": 5, "another_key": {"and another": 3, "and another one": 1}}, "test")
    lower_25 = get_std_v(ft.Scene(root + "traj_2.5_low.h5"), "2.5")
    save_as_json(lower_25, "sum_of_sqr_diff_from_avg_lower_2.5")
    higher_25 = get_std_v(ft.Scene(root + "traj_2.5_high.h5"), "2.5")
    save_as_json(higher_25, "sum_of_sqr_diff_from_avg_higer_2.5")
    merged_25 = merge_dict(lower_25, higher_25, 
            lambda a, b: [a[0] + b[0],
            a[1] + b[1]])
    save_as_json(merged_25, "sum_of_sqr_diff_from_avg_2.5")
    
    print "\n2.5 done!\n"
    
    lower_40 = get_std_v(ft.Scene(root + "traj_4.0_low.h5"), "4.0")
    save_as_json(lower_40, "sum_of_sqr_diff_from_avg_lower_4.0")
    higher_40 = get_std_v(ft.Scene(root + "traj_4.0_high.h5"), "4.0")
    save_as_json(higher_40, "sum_of_sqr_diff_from_avg_higer_4.0")
    merged_40 = merge_dict(lower_40, higher_40, 
            lambda a, b: [a[0] + b[0], a[1] + b[1]])
    save_as_json(merged_40, "sum_of_sqr_diff_from_avg_4.0")
   
std_root = "sum_of_sqr_diff_from_avg_"
def get_std_h(h, vel):
    data = read_json(std_root + str(vel))
    relevant = str(filter(lambda a: abs(h - float(a)) < 0.0001, data.keys())[0])
    print relevant
    return sqrt(data[relevant][0] / (data[relevant][1] - 1))
    

def group_by_height(traj, i, start, end, jump, unsafe = False):
    val = start
    
    if (start > 0.1 or end > 0.2 or jump > 0.05) and not unsafe:
        print("start = {}, end = {}, jump = {}. all in m. are you sure you are correct?".format(start, end, jump)
              + " if so please use unsafe mode")
        raise Exception('Suspicious values inserted in unsafe mode')
    
    while (val <= end):
        if val <= traj.pos()[i, 1] < min(val + jump, end):
            return (val + min(val + jump, end)) * 0.5
        val += jump
    
    return "no group"

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
