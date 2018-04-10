import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import xarray as xr
#import datetime as dt
    
def read_netcdfs(fileList, dim):
        def process_one_path(path):
                with xr.open_dataset(path) as ds:
                        ds.load()
                        return ds

        paths = sorted(fileList)
        datasets = [process_one_path(p) for p in paths]
        combined = xr.concat(datasets, dim)

        return combined

fileList = glob.glob('/disks/arctic5_raid/abarrett/CFSR*/T/????/CFSR*.T925.arctic.avg.????.nc')
#year = [int(f.split('.')[4]) for f in fileList]

#ds = xr.open_mfdataset(fileList, concat_dim='time')
ds = read_netcdfs(fileList, 'time')

ds.time.encoding['units'] = 'days since 1900-01-01 00:00:00'

print ds
print ds['T925'].values
exit()

#fig, ax = plt.subplots(figsize=(20,7))
#ds['T925'].plot(ax=ax)
#ax.set_xlim(dt.datetime(1978,1,1),dt.datetime(2017,12,31))
#fig.savefig('/disks/arctic5_raid/abarrett/CFSR2/T/CFSRx.T925.arctic.avg.1979to2017.png')

ds.to_netcdf('/disks/arctic5_raid/abarrett/CFSR2/T/CFSR2.T925.arctic.avg.1979to2017.nc')

