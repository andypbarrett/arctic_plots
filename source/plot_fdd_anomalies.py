
import xarray as xr
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import matplotlib.colors as colors

import calc_fdd #.outfile as get_fdd_filename

# projection class
class EASE_North(ccrs.Projection):

    def __init__(self):

        # see: http://www.spatialreference.org/ref/epsg/3408/
        proj4_params = {'proj': 'laea',
            'lat_0': 90.,
            'lon_0': 0,
            'x_0': 0,
            'y_0': 0,
            'a': 6371228,
            'b': 6371228,
            'units': 'm',
            'no_defs': ''}

        super(EASE_North, self).__init__(proj4_params)

    @property
    def boundary(self):
        coords = ((self.x_limits[0], self.y_limits[0]),(self.x_limits[1], self.y_limits[0]),
                  (self.x_limits[1], self.y_limits[1]),(self.x_limits[0], self.y_limits[1]),
                  (self.x_limits[0], self.y_limits[0]))

        return ccrs.sgeom.Polygon(coords).exterior

    @property
    def threshold(self):
        return 1e5

    @property
    def x_limits(self):
        #return (-9030575.88125, 9030575.88125)
        #return (-9000000, 9000000)
        return (-8999241.475, 8999241.475)
    @property
    def y_limits(self):
        #return (-9030575.88125, 9030575.88125)
        #return (-9000000, 9000000)
        return (-8999241.475, 8999241.475)

def get_projection_info():

    # Define extent
    C= 200.5402*1e3/4.
    r0 = 179.5
    extent = [-1*r0*C, r0*C, -1*r0*C, r0*C]

    origin = 'upper'

    projection = EASE_North()

    return extent, origin, projection

def get_climatology(clmbeg, clmend):
    
    fileList = [calc_fdd.outfile(dt.datetime(yr,3,31).strftime('%Y%m%d')) for yr in np.arange(clmbeg,clmend)]

    # Get data for calculating climatology
    ds = xr.open_mfdataset(fileList, concat_dim='time')
    lat = ds['lat'][0,:,:].load()
    lat= lat.where(lat > -998.)
    lon = ds['lon'][0,:,:].load()
    lon = lon.where(lat > -998.)
    fdd = ds['FDD'].load().where(lat > -998.)
    ds.close()

    # Calculate climatology
    fddClm = fdd.mean(dim='time')
    fddStd = fdd.std(dim='time')
    
    return fddClm, fddStd

#----------------------------------------------------------------------
# Main code
#----------------------------------------------------------------------

def plot_fdd_anomalies(year, standardize=False, verbose=False):

    if verbose: print ('Calculating climatology')
    fddClm, fddStd = get_climatology(1981,1990)

    fdd = xr.open_dataset(calc_fdd.outfile(dt.datetime(year,3,31).strftime('%Y%m%d')))

    if standardize:
        if verbose: print ('Calculating standardized anomalies for {:d}'.format(year))
        anom = (fdd['FDD'] - fddClm) / fddStd
        bounds = np.linspace(-5,5,11)
    else:
        if verbose: print ('Calculating anomalies for {:d}'.format(year))
        anom = fdd['FDD'] - fddClm
        bounds = np.linspace(-1200,1200,9)

    extent, origin, projection = get_projection_info()

    lim = 3000000
    fig, ax = plt.subplots(figsize=(8,8),
                           subplot_kw={'projection': EASE_North(),
                                       'xlim': [-lim,lim],
                                       'ylim': [-lim,lim]})

    ax.coastlines()
    ax.set_extent([-180, 180, 65, 90], ccrs.PlateCarree())

    cmap = plt.get_cmap('RdYlBu_r')
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)

    img = ax.imshow(anom.data, cmap=cmap, norm=norm, 
                    interpolation='none', origin=origin, extent=extent, transform=projection)
#    img = ax.pcolormesh(fdd.lon, fdd.lat, anom.data, transform=ccrs.PlateCarree(),
#                        cmap=cmap, norm=norm)
    ax.set_title('FDD Anomalies 1 Oct {:d} to 31 March {:d}'.format(year-1,year), fontsize=15)

    cb = plt.colorbar(img, extend='both')
    if standardize:
        cb.set_label('Standard Deviation', fontsize=15)
    else:
        cb.set_label('Deg. C days', fontsize=15)
    
    plt.show()

    if standardize:
        filo = 'fdd_anomalies_{:d}_standardized.png'.format(year)
    else:
        filo = 'fdd_anomalies_{:d}.png'.format(year)
    if verbose: print ('Saving plot to {:s}'.format(filo))
    fig.savefig(filo)
    


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Plots Freezing Degree Day Anomalies')
    parser.add_argument('year', type=int, help='year to plot')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--standardize', action='store_true')
    args = parser.parse_args()

    plot_fdd_anomalies(args.year, standardize=args.standardize, verbose=args.verbose)







