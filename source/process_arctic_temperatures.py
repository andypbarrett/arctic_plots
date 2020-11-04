def arctic_avg_Wrap(ds):

        import numpy as np
        import xarray as xr

        latwgt = np.cos(ds['lat_0'].where(ds['lat_0'] > 80.) * np.pi/180.)
        lonwgt = xr.DataArray(np.ones(ds['lon_0'].size), [ds.coords['lon_0']])
        weight = (latwgt * lonwgt) / (latwgt*lonwgt).sum()

        arctic_avg = (ds['T'][:,4,:,:] * weight).sum(dim=['lat_0','lon_0'])
        arctic_avg.name = 'T925'

        return arctic_avg
	
import numpy as np
import xarray as xr
import datetime as dt
import os
from glob import glob

for year in np.arange(2017,2018):

       diri = '/disks/arctic5_raid/abarrett'
       if year < 2011:
               reanalysis = 'CFSR'
       else:
               reanalysis = 'CFSR2'

       globstr = os.path.join(diri,reanalysis,'T',repr(year),'??',reanalysis+'.flxf06.gdas.T.'+repr(year)+'????.nc')

       fileList = sorted(glob(globstr))
       ds = xr.open_mfdataset(fileList, concat_dim='time')

       ds['time']=[dt.datetime.strptime(f.split('.')[4],'%Y%m%d') for f in fileList]
       ds.time.encoding['units'] = 'days since 1900-01-01 00:00:00'

       tavg = arctic_avg_Wrap(ds)

       filo = reanalysis+'.T925.arctic.avg.'+repr(year)+'.nc'
       outstr = os.path.join(diri,reanalysis,'T',repr(year),filo)

       print 'Writing data from '+repr(year)+' to '+outstr
       tavg.to_netcdf(outstr, mode='w')
