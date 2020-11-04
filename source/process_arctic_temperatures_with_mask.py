def arctic_ocean_mask(region='Nof80'):
    
    import xarray as xr
    import os
    
    mdiri = "/oldhome/apbarret/projects/ancillary/masks"
    mfili = "arctic_mask_cfsr.nc"
    
    ds = xr.open_dataset(os.path.join(mdiri, mfili))
    
    if (region == "rims_arctic"):
        return ds['arctic_mask'].where(ds['arctic_mask'] == 6)*0. + 1.
    elif (region == "arctic_ocean"):
        return ds['arctic_mask'].where((ds['arctic_mask'] == 6) | 
                                       ((ds['lat'] > 66.5) & 
                                        (ds['lon'] > 180) & (ds['lon'] < 310.) &
                                        (ds['arctic_mask'] == 0)))*0. + 1.
    elif (region == "Nof80"):
        return ds['arctic_mask'].where(ds['lat'] > 80.)
    else:
        print ("arctic_ocean_mask: Unknown region")
        return None

def get_weight(region='Nof80'):

        import numpy as np
        import xarray as xr

        mask = arctic_ocean_mask(region=region)

        latwgt = np.cos(mask['lat'] * np.pi/180.)
        lonwgt = xr.DataArray(np.ones(mask['lon'].size), [mask.coords['lon']])
        weight = (latwgt * lonwgt * mask) / (latwgt * lonwgt * mask).sum()

        return weight.rename({'lat':'lat_0', 'lon':'lon_0'})

def arctic_avg_Wrap(ds, region='Nof80'):

        weight = get_weight(region=region)

        arctic_avg = (ds['T'][:,4,:,:] * weight).sum(dim=['lat_0','lon_0'])
        arctic_avg.name = 'T925'

        return arctic_avg
	
import numpy as np
import xarray as xr
import datetime as dt
import os
from glob import glob

region = 'arctic_ocean'

weight = get_weight(region=region)

for year in np.arange(2018,2019):

       diri = '/disks/arctic5_raid/abarrett'
       if year < 2011:
               reanalysis = 'CFSR'
       else:
               reanalysis = 'CFSR2'

       globstr = os.path.join(diri,reanalysis,'T',repr(year),'??',reanalysis+'.flxf06.gdas.T.'+repr(year)+'????.nc')

       fileList = sorted(glob(globstr))

       ds = xr.open_mfdataset(fileList, concat_dim='time')
       ds.load()

       ds['time']=[dt.datetime.strptime(f.split('.')[4],'%Y%m%d') for f in fileList]
       ds.time.encoding['units'] = 'days since 1900-01-01 00:00:00'

       tavg = (ds['T'][:,4,:,:] * weight).sum(dim=['lat_0','lon_0'])
       tavg.name = 'T925'

       filo = reanalysis+'.T925.arctic.avg.'+repr(year)+'.'+region+'.nc'
       outstr = os.path.join(diri,reanalysis,'T',repr(year),filo)

       print ('Writing data from '+repr(year)+' to '+outstr)
       tavg.to_netcdf(outstr, mode='w')
