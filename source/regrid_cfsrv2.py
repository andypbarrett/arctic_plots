import os
import re
import pandas as pd
import datetime as dt
import argparse

root = "/disks/arctic5_raid/abarrett/CFSR2"
esmf_grid_dir = '/disks/arctic5_raid/abarrett/CFSR2'
ffmt = {'T':  'CFSR2.flxf06.gdas.T.{:s}.nc',}
var = {'T': {'varIn': 'T', 'varOut': 'T'},}

def parse_date(date, freq='D'):

    if ( len(date) == 1 ):
        m = re.search('(\d+)\.\.(\d+)',date[0])
        if m:
            dateList = [d.strftime('%Y%m%d') for d in pd.date_range(m.group(1), m.group(2), freq=freq)]
        else:
            dateList = date
    else:
        dateList = date
        
    return dateList

def make_filename(d, var):

    dob = dt.datetime.strptime(d,'%Y%m%d')
    return os.path.join(root,var,dob.strftime('%Y'),dob.strftime('%m'),
                        ffmt[var].format(d))
                        
def regrid_cfsrv2(dateList, variable, outgrid, verbose=False, doplot=False):
    """
    Batch process to regrid CFSRv2 data. Currently calls NCL routine:

    esmf_regrid_latlon_to_unstructured_cfsr2_1var.v1.ncl

    N.B. This may be converted to ESMPy routine in future
    
    Arguments
    ---------
    dateList - list of dates of files to regrid
    variable - name of variable to regrid
    outgrid  - name of output grid
    """
    
    # Loop through files to regrid
    for d in dateList:

        fili = make_filename(d, variable)
        if (not os.path.isfile(fili)):
            print ('WARNING: %{:s} does not exist - skipping'.format(fili))
            continue
        
        argList = r'fili=\""{:s}\"" ingrid_name=\""CFSR2\"" outgrid_name=\""{:s}\""  varIn=\""{:s}\"" varOut=\""{:s}\"" verbose={:} overwrite=True esmf_grid_dir=\""{:s}\"" doplot={:}'\
                  .format(fili, outgrid, var[variable]['varIn'], var[variable]['varOut'],
                          verbose, esmf_grid_dir, doplot)
        script = '/home/apbarret/src/NCL/esmf_regrid_latlon_to_unstructured_cfsr2_1var.v1.ncl'
        nclcmd = 'ncl ' + argList + ' ' + script
        os.system(nclcmd)
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Regrid CFSRv2 data')
    parser.add_argument('variable', type=str, 
                        help='variable to process')
    parser.add_argument('outgrid', type=str,
                        help='Name of outgrid (e.g. EASE_NH50km)')
    parser.add_argument('date', type=str, nargs='+', 
                        help='single date, list of dates or date range (YYYYMMDD YYYYMMDD... or YYYYMMDD..YYYYMMDD')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--doplot', action='store_true')
    args = parser.parse_args()

    dateList = parse_date(args.date)
    
    regrid_cfsrv2(dateList, args.variable, args.outgrid, verbose=args.verbose, doplot=args.doplot)
