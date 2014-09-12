"""
header


******************************************

This is a work in progress and will be replaced by the actual process BNG data script.

******************************************
"""

import netCDF4 as nc
import numpy as np
#import matplotlib.pyplot as plt
import sys

def find_points(infile, maskfile):
    """
    find the lat lon points from the mask file
    :param infile:
    :param maskfile:
    :return:
    """

    inf=nc.Dataset(infile,'r')

    mf=nc.Dataset(maskfile,'r')

    nxin=len(inf.dimensions['x'])
    nyin=len(inf.dimensions['y'])

    latin=inf.variables['latitude'][:].flatten()
    lonin=inf.variables['longitude'][:].flatten()

    latm=mf.variables['lat'][:]
    lonm=mf.variables['lon'][:]

    thresh=5e-5

    lat_point_index = np.empty(len(latin))
    lon_point_index = np.empty(len(lonin))


    lat_sorted = sorted([[lat, i] for lat, i in zip(latin, range(len(latin)))], key=lambda a: a[0])
    lat_sorted_vals = [x[0] for x in lat_sorted]
    lat_sorted_index = [x[1] for x in lat_sorted]

    lon_sorted = sorted([[lon, i] for lon, i in zip(lonin, range(len(lonin)))], key=lambda a: a[0])
    lon_sorted_vals = [x[0] for x in lon_sorted]
    lon_sorted_index = [x[1] for x in lon_sorted]


    #lat_sorted_vals = np.sort(latin)

    lon_sorted = np.argsort(lonin)
    lat_sorted = np.argsort(latin)

    min_lat = min(latin)
    min_lon = min(lonin)

    # for x  in range(latm.shape[0]):
    #     for y in range(latm.shape[1]):
    #         if y%100 == 0:
    #             print "%s, %s" % (x, y)
    #         if latm[x, y] < min_lat or lonm[x, y] < min_lon:
    #             pass
    #         else:
    #
    #             lon_start = np.searchsorted(lon_sorted_vals, lonm[x, y] - thresh, 'left')
    #             lon_end = np.searchsorted(lon_sorted_vals, lonm[x, y] + thresh, 'right')
    #
    #             lat_start = np.searchsorted(lat_sorted_vals, latm[x,y] - thresh, 'left')
    #             lat_end = np.searchsorted(lat_sorted_vals, latm[x,y] + thresh, 'right')
    #
    #             #pos_lat = np.where( np.abs(latm[x,y] - lat_sorted_vals) < thresh)
    #             #pos_lon = np.where( np.abs(lonm[x,y] -lon_sorted) < thresh)
    #
    #             union = np.intersect1d(lat_sorted_index[lat_start:lat_end], lon_sorted_index[lon_start:lon_end])
    #
    #             if len(union) == 1:
    #                 lon_point_index[len(union)] = x
    #                 lat_point_index[len(union)] = y
    #             elif len(union) > 1:
    #                 print "Error: not one point was %d"%(len(union))
    #                 sys.exit(2)

    lat_point_index = []
    lon_point_index = []
    for i in range(nxin*nyin):
        if i%1000 == 0:
            print i
        indx = np.where( np.logical_and(np.abs(latm-latin[i]) < thresh, np.abs(lonm-lonin[i]) <thresh))
        if len(indx[0])==0:
            print "Error: point %d (%s %s) not found"%(i,latin[i],lonin[i])
            sys.exit(2)
        elif len(indx[0])>1:
            print "Error: point %d (%s %s) been found %d times"%(i,latin[i],lonin[i],len(indx[0]))
            sys.exit(3)
        else:
            lat_point_index.append(indx[0][0])
            lon_point_index.append(indx[1][0])
            print "%d, %d" %(indx)

    return lat_point_index, lon_point_index


def create_2D_file(infile, maskfile, outfile):

    VARIABLE_NOT_TO_MAP = []
    nyout = 105
    nxout = 65
    ys, xs = find_points(infile, maskfile)



    pts=[]

    inf=nc.Dataset(infile,'r')
    #dimlensin={}
    #for dim in inf.dimensions:
        #dimlensin[dim]=len(inf.dimensions[dim])


    outf=nc.Dataset(outfile,'w')
    #dimlensout={}

    for dim in inf.dimensions:
        if dim == 'y':
            dimlen = nyout
        elif dim == 'x':
            dimlen = nxout
        else:
            dimlen = len(inf.dimensions[dim])
        outf.createDimension(dim, dimlen)

    mapvars=[]
    outdata={}
    for var in inf.variables:
        #special arrtibutes
        if '_FillValue' in inf.variables[var].ncattrs():
            outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions,fill_value=inf.variables[var]._FillValue)
        elif 'fill_value' in inf.variables[var].ncattrs():
            outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions,fill_value=inf.variables[var].fill_value)
        elif 'missing_value' in inf.variables[var].ncattrs():
            outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions,fill_value=inf.variables[var].missing_value)
        else:
            outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions)

        #other attributes
        for attr in inf.variables[var].ncattrs():
            if attr not in ('_FillValue','fill_value','missing_value'):
                outf.variables[var].setncattr(attr,inf.variables[var].getncattr(attr))

        #map the variables
        if var not in VARIABLE_NOT_TO_MAP:
            mapvars.append(var)
            if '_FillValue' in outf.variables[var].ncattrs():
                mv=outf.variables[var]._FillValue
            else:
                mv=-99999.0

            outdata[var]=np.ma.masked_equal(np.ones(outf.variables[var].shape)*mv,mv)
        else:
            outf.variables[var][:]=inf.variables[var][:]

    for var in mapvars:
        if len(outf.variables[var].shape)==2:
            outdata[var][ys,xs]=inf.variables[var][:].flatten()
        elif len(outf.variables[var].shape)==3:
            for t in range(outdata[var].shape[0]):
                outdata[var][t,ys,xs]=inf.variables[var][t,:,:].flatten()
        elif len(outf.variables[var].shape)==4:
            for t in range(outdata[var].shape[0]):
                for z in range(outdata[var].shape[1]):
                    outdata[var][t,z,ys,xs]=inf.variables[var][t,z,:,:].flatten()
        else:
            print "Error: too many dimensions"
            sys.exit(2)


    inf.close()

    for var in mapvars:
        outf.variables[var][:]=outdata[var][:]

    outf.close()

    print "Done, please look at %s for some lovely mapped data"%outfile


if __name__ == '__main__':
    inputFolder = "/home/johhol/project/jules-jasmin/job_runner/job_runner_test/run/run10/output/majic.surf_roff_daily.nc"
    outputFolder = "/home/johhol/project/jules-jasmin/job_runner/job_runner_test/run/run10/processed/majic.surf_roff_daily.nc"

    mask ="/home/johhol/project/jules-jasmin/job_runner/job_runner_test/run/run10/data/CHESS/ancils/chess_lat_lon.nc"

    create_2D_file(inputFolder, mask, outputFolder)
