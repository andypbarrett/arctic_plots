import os, glob
import re
import xarray as xr
import datetime as dt
import argparse

root = '/disks/arctic5_raid/abarrett/CFSR2/T'
diri = os.path.join(root,'new_netcdf_files')

def read_netcdf(fili):
    """
    Reads netcdf file, extracts temperature variable and renames variable and
    coordinate names
    """
    
    varIn = 'TMP_L100'
    varOut = 'T'
    
    ds = xr.open_dataset(fili)
    
    da = ds[varIn]
    da.name = varOut  # rename variable

    # Rename coordinate names
    coord_name = {'lat': 'lat_0', 'lon': 'lon_0', 'level0': 'lv_ISBL0'}
    da = da.rename(coord_name)
    for key in coord_name.keys():
        # rename short name attribute
        da.coords[coord_name[key]].attrs['name'] = coord_name[key]
        da.coords[coord_name[key]].attrs['_FillValue'] = 1.e+20
        
    da.attrs['_FillValue'] = 1.e+20
    
    return da

def timeAvg_Wrap(da):

    daAvg = da.mean(dim='time')
    daAvg.attrs = da.attrs

    return daAvg

def gen_outfile(fili):

    m = re.compile('cdas1.([0-9]{8}).pgrbh')
    date = dt.datetime.strptime(m.search(fili).groups()[0], '%Y%m%d')
    return os.path.join(root, date.strftime('%Y'), date.strftime('%m'),
                        'CFSR2.flxf06.gdas.T.'+date.strftime('%Y%m%d')+'.nc')

def get_fileList(date_begin=None, date_end=None):

    m = re.compile('cdas1.([0-9]{8}).pgrbh')

    fileList = sorted( glob.glob( os.path.join(diri, 'cdas1.*.pgrbh.grb2.nc') ) )

    date = [dt.datetime.strptime(m.search(f).groups()[0], '%Y%m%d') for f in fileList]
    if date_begin: fileList = [f for f, d in zip(fileList, date) if d >= dt.datetime.strptime(date_begin,'%Y%m%d')]
    if date_end: fileList = [f for f, d in zip(fileList, date) if d <= dt.datetime.strptime(date_begin,'%Y%m%d')]
    return fileList

def main(date_begin=None, date_end=None, verbose=False):

    fileList = get_fileList(date_begin=date_begin, date_end=date_end)

    for fili in fileList:

        if verbose:
            print ( '%cfsr2_6hr2daily: Processing '+fili )
        
        # Make output name
        filo = gen_outfile(fili)
        
        # Read file
        if verbose: print ( '   ...reading file' )
        da = read_netcdf(os.path.join(diri,fili))

        # Get daily average
        if verbose: print ( '   ...getting time average' )
        daAvg = timeAvg_Wrap(da)

        # Write to netcdf
        if verbose: print ( '   ...writing to '+filo )
        if (os.path.exists( os.path.dirname(filo) ) == False):
            os.makedirs( os.path.dirname(filo), exist_ok=False )
        daAvg.to_netcdf(filo)

    return

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert CFSR or CFSRv2 6h files to daily')
    parser.add_argument('--date_begin', type=str, default=None, 
                        help='date to start processing YYYYMMDD')
    parser.add_argument('--date_end', type=str, default=None, 
                        help='date to end processing YYYYMMDD')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    main(date_begin=args.date_begin, date_end=args.date_end, verbose=args.verbose)
    



    
