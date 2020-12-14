import numpy as np
import os
import sys
from presto.psr_utils import rrat_period
from datetime import datetime as dt
import pytz
utc = pytz.utc
data = sys.argv[1]
times = np.load(data,allow_pickle=1)['new_source_time']
cutoff = utc.localize(dt(2019,12,1))
a=[]
for time in times:
    if time>cutoff:
        a.append(time)
times=a
print(times)
ts = list(time.timestamp() for time in times)

min_seperation = 30
altered_ts=[]
for i,t in enumerate(ts):
    if i>0:
        if (t-ts[i-1])>min_seperation:
            altered_ts.append(t)
print(len(altered_ts))
rrat_period(altered_ts)
