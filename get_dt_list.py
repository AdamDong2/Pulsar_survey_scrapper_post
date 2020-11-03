import numpy as np
from datetime import datetime as dt

times = np.load('data.npz',allow_pickle=1)['new_source_time']
time_sec =[]
print(times)
for time in times:
    time=time.replace(tzinfo=None)
    if (time>dt(2020,2,3)) & (time<dt(2020,2,4)):
        sec = (time-dt(2020,2,3)).total_seconds()
        time_sec.append(sec)

print(time_sec)
