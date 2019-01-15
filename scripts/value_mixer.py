from Raupach_eq_drag_mesurments import get_drag_raupach, area_by_volume
from acc_mesurments import sum_all_acc
from functools import reduce

def prcnt_diff(vel, use_U_inf=False, version=""):

    t = get_drag_raupach(vel, area=area_by_volume)["Cd br"] \
        if not use_U_inf else get_drag_raupach(vel, area=area_by_volume)["rey stress gradient"]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key] / (-0.5 * (float(vel) ** 2) * area_by_volume), key / 10.0))
    if not use_U_inf:
        lis = lis[1:]
    raupach_data = lis[:-6]

    t = sum_all_acc(vel, only_corner=True, version=version)[1] \
        if not use_U_inf else sum_all_acc(vel, only_corner=True, version=version)[2]
    lis = []
    for key in sorted(t.keys()):
        lis.append((t[key][0], key * 10.0))
    lis = lis[1:-7 if vel == "4.0" else -7]
    acc_data = lis
    acc_data = [(-x[0], x[1]) for x in acc_data]

    raupach_over_acc = []
    for i in range(len(acc_data)):
        raupach_over_acc.append(raupach_data[i][0] / acc_data[i][0])

    raupach_over_acc = [abs(1 - x) for x in raupach_over_acc]

    return raupach_over_acc[1:-1]

print(prcnt_diff("2.5", True, "2"))
vals = prcnt_diff("2.5", True, "2")
print(str(reduce(lambda a, b: a + b, vals) / len(vals)))
