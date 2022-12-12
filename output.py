import numpy as np
import scipy.stats as st
import statistics
def output_analyze(list):
    m = np.mean(list)
    v = statistics.variance(list)
    print(st.t.interval(alpha=0.95, df=len(list) - 1, loc=m, scale=st.sem(list)))
    print(m)
    print(v)


