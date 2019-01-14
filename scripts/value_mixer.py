from Raupach_eq_drag_mesurments import get_drag_raupach, area_by_volume
from acc_mesurments import sum_all_acc

def prcnt_diff(vel):
    diffs = []

    ourData = [sum_all_acc(vel)[2][x] for x in sorted(sum_all_acc(vel)[2].keys())][1:]
    raupachData = get_drag_raupach(vel)["Cd"]

    print("\n\n\n\n\n\n\n\n\n\n")

    print(ourData)
    print(raupachData)

prcnt_diff("2.5")