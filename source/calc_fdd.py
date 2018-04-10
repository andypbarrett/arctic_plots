import xarray as xr
import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt

root = '/disks/arctic5_raid/abarrett'

def cfsr_str(year):
    if year > 2010:
        return 'CFSR2'
    else:
        return 'CFSR'

def cfsr_filename(date, var):
    fname = os.path.join(root,
                         cfsr_str(date.year),
                         var,
                         date.strftime('%Y'),date.strftime('%m'),
                         '{:s}.flxf06.gdas.{:s}.{:s}.EASE_NH50km.nc'.format(cfsr_str(date.year),
                                                                            var,
                                                                            date.strftime('%Y%m%d')))
    return fname

def outfile(end_date):

    date = dt.datetime.strptime(end_date,'%Y%m%d')
    fname = os.path.join(root,
                         cfsr_str(date.year),
                         'T',
                         date.strftime('%Y'),
                         '{:s}.flxf06.gdas.FDD.{:s}.EASE_NH50km.nc'.format(cfsr_str(date.year),
                                                                            date.strftime('%Y%m%d')))
    return fname

    

def dateList(end_date, freq='D'):
    """
    Generate a list of dates starting on 1 Oct and ending on end date.
    If end_date is after Jan 1 and before Oct 1, start date is 1 Oct of previous year
    otherwise it is 1 Oct of year of end date
    """

    end = dt.datetime.strptime(end_date, '%Y%m%d')
    if end < dt.datetime(end.year,10,1):
        start = dt.datetime(end.year-1, 10, 1)
    else:
        start = dt.datetime(end.year,10,1)
        
    return pd.date_range(start, end, freq=freq)

def fileList(end_date, var):
    """
    Returns list of CFSR files for FDD calculation
    """
    return [cfsr_filename(d, var) for d in dateList(end_date)]

    
def calc_fdd(end_date, threshold=0., verbose=False):
    """
    Calculate FDD sum for a period that starts 1 Oct and ends on end_date for
    a given winter period.
    """

    if verbose: print ('%calc_fdd: getting data for period ending {:s}'.format(end_date))
    ds = xr.open_mfdataset(fileList(end_date, 'T'), concat_dim='time')
    lat = ds['lat'][0,:,:].load()
    lon = ds['lon'][0,:,:].load()
    da = ds['T'][:,4,:,:].load()
    attrs = da.attrs
    ds.close()

    if verbose: print ('%calc_fdd: calculating freezing degree days')
    da = da - 273.15 # Convert to degrees celsius
    fdd = da.where(da < threshold).sum(dim='time') * -1.
    fdd.attrs = attrs
    fdd.attrs['units'] = 'C days'
    fdd.attrs['number of vertical levels'] = 1

    ds = xr.Dataset({'FDD': fdd, 'lat': lat, 'lon': lon})

    filo = outfile(end_date)
    if verbose: print ('%calc_fdd: writing data to {:s}'.format(filo))
    ds.to_netcdf(filo)
    
    return

if __name__ == "__main__":

    import argparse

    #parser = argparse.Argument

    #calc_fdd(args.end_date, threshold=args.threshold)
    calc_fdd('20180331', verbose=True)

    
