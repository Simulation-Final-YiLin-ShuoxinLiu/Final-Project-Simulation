import math

import numpy as np
from scipy import stats




def gen_rn_list(n):
    l = list()
    for i in range(0, n):
        l.append(np.random.uniform(low=0.0, high=1.0))
    return l


def caculate_lam(obser_mins):
    count = 0
    sum = 0
    for i in obser_mins:
        sum += i
        count += 1
    return 1 / (sum / count)


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
        d1 = count / len(obervations) - stats.expon.cdf(i, scale=1 / lam)
        d2 = stats.expon.cdf(i, scale=1 / lam) - (count - 1) / len(obervations)
        if d1 > max:
            max = d1
        if d2 > max:
            max = d2
        count += 1
    print((max - 0.2 / len(obervations)) * (math.sqrt(len(obervations)) + 0.26 + 0.5 / math.sqrt(len(obervations))))
    if (max - 0.2 / len(obervations)) * (math.sqrt(len(obervations)) + 0.26 + 0.5 / math.sqrt(len(obervations))) > C:
        print("reject!")



