import math
import numpy as np
from scipy import stats

obser_mins = [i/60 for i in [60,45,78,12,45,78,32,45,60,59,45,55,66]]
obser_mins = [1.0530336695002134, 0.26213156559980966, 0.15467778321893783, 1.0025596695940895, 0.8740847046404023, 0.2103302952631578, 0.594668878749017, 0.0921421900660671, 0.3310456934710782, 0.16159866882428064, 0.07179865362893312, 3.7994883478345964, 0.07476461683105799, 0.14852935613938814, 0.48503541290337726, 0.3397380610702101, 0.019189440243526115, 1.0626783513287006, 2.0284169914610635]
def gen_rn_list(n):
    l = list()
    for i in range(1, n):
        l.append(np.random.uniform(low=0.0, high=1.0))
    return l

def caculate_lam(obser_mins):
    count =0
    sum=0
    for i in obser_mins:
        sum+=i
        count+=1
    return 1/(sum/count)

def gen_exp_rv_list(lam, rm_list):
    l = list()
    for i in rm_list:
        l.append((-np.log(i) / lam))
    return l


def exp_KS_test(obervations, lam, C):
    obervations.sort()
    max = 0
    count = 1
    for i in obervations:
        d1 = count / len(obervations) - stats.expon.cdf(i, scale=1/lam)
        d2 = stats.expon.cdf(i, scale=1/lam) - (count - 1) / len(obervations)
        if d1 > max:
            max = d1
        if d2 > max:
            max = d2
        count += 1
    print(max)
    print((max-0.2/len(obervations))*(math.sqrt(len(obervations))+0.26+0.5/math.sqrt(len(obervations))))
    if (max-0.2/len(obervations))*(math.sqrt(len(obervations))+0.26+0.5/math.sqrt(len(obervations))) > C:
        print("reject!")


lam= caculate_lam(obser_mins)
print(lam)
rns=gen_rn_list(20)
rvs = gen_exp_rv_list(lam,rns)
exp_KS_test(obser_mins,lam, 0.990)
