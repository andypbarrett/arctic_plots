
import numpy as np
import datetime as dt
import calc_fdd

for yr in np.arange(1980, 2019):

    date = dt.datetime(yr,3,31).strftime('%Y%m%d')
    calc_fdd.calc_fdd(date, verbose=True)

    
