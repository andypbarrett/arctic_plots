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

region = 'arctic_ocean'

fileList = glob.glob('/disks/arctic5_raid/abarrett/CFSR*/T/????/CFSR*.T925.arctic.avg.????.'+region+'.nc')
#year = [int(f.split('.')[4]) for f in fileList]

#ds = xr.open_mfdataset(fileList, concat_dim='time')
ds = read_netcdfs(fileList, 'time')

ds.time.encoding['units'] = 'days since 1900-01-01 00:00:00'

ds.to_netcdf('/disks/arctic5_raid/abarrett/CFSR2/T/CFSR2.T925.arctic.avg.1979to2017.'+region+'.nc')

