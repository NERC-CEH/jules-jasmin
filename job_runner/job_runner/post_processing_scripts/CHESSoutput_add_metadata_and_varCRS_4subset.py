#-------------------------------------------------------------------------------
# Name:        CHESSoutput_add_metadata_and_varCRS.py
# Purpose:     Add crs, latitude and longitude variables
#              to original file and adds the appropriate metadata
#              to CHESS output files.
#              The files need to be previously trasnformed to a 2D grid
#              (you can use Emma Robinson's code for that).
#
# Author:      Maliko Tanguy (malngu@ceh.ac.uk)
#
# Created:     18/09/2014
#
#-------------------------------------------------------------------------------

import netCDF4
import numpy as np
import datetime
import mpl_toolkits.basemap.pyproj as pyproj
import math



# Function to convert from datetime date to netcdf date
def datetime2netcdf(netcdfUnits,date):
	import netcdftime
	import datetime
	cdftime = netcdftime.utime(netcdfUnits)
	t = cdftime.date2num(date)
	return t

# Function to convert from netcdf date to datetime date
def netcdf2datetime(t,netcdfUnits):
	import netcdftime
	import datetime
	cdftime = netcdftime.utime(netcdfUnits)
	date = cdftime.num2date(t)
	return date

#--------------------------------------------------------------------------

def lastPostProcessCHESS(inputFolder,outputFolder,inputnetCDF):
    """
    This is the main fonction.
    inputnetCDF is the path to the netCDF file that needs processing.

    """

    zlibOp = True # True if compression wanted.

    verbose = True # Set to False if you don't want text on your screen.

    # At the moment, a copy of the original netCDF file is created, and the original
    # one is not deleted
    outputnetCDF = outputFolder + inputnetCDF

    fh = netCDF4.Dataset(inputFolder + inputnetCDF, mode='r')
    outnc = netCDF4.Dataset(outputnetCDF, mode='w', format = "NETCDF4")

    # Loops through existing dimensions
    for dim in fh.dimensions.values():

        names = str(dim).split("'")
        name = names[3]

        sizes = str(dim).split(' ')
        size = sizes[len(sizes)-1]
        if verbose == True:
            print 'Creating dimension ' + name + ' of size '+ size
        if name=='time':
            outnc.createDimension('Time',int(size))
        else:
            outnc.createDimension(name,int(size))
        if name=='x':
            xsize = int(size)
        elif name=='y':
            ysize = int(size)



    # find the indices of the first and last unmasked array
    print isinstance(fh.variables['latitude'][0,0], np.ma.core.MaskedArray)
    print xsize, ysize


    #maskedLat = np.ma.masked_invalid(fh.variables['latitude'])
    print 'Calculating coordinates of first land point'
    for ypos in range(ysize):
        for xpos in range(xsize):
            if isinstance(fh.variables['latitude'][ypos,xpos], np.ma.core.MaskedArray)==False:
                break
        if isinstance(fh.variables['latitude'][ypos,xpos], np.ma.core.MaskedArray)==False:
            break

    print xpos, ypos
    firstLandLat = fh.variables['latitude'][ypos,xpos]
    firstLandLon = fh.variables['longitude'][ypos,xpos]

    # define coordinate systems
    wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum
    osgb36=pyproj.Proj("+init=EPSG:27700") # UK Ordnance Survey, 1936 datum

    firstLandX, firstLandY = pyproj.transform(wgs84, osgb36, firstLandLon, firstLandLat)
    #print firstLandX, firstLandY

    # coordinate of origin in BNG
    iniX = int(round(firstLandX/1000))*1000 - 1000*xpos
    iniY = int(round(firstLandY/1000))*1000 - 1000*ypos
    print iniX, iniY


    # Loops through existing global attributes
    for globAtt in fh.ncattrs():
        setattr(outnc, globAtt, getattr(fh,globAtt))

    # Add metadata
    setattr(outnc, 'title', 'CHESS output data')
    setattr(outnc, 'institution', 'CEH-Wallingford - NERC')
    setattr(outnc, 'grid_mapping', 'crs')
    setattr(outnc, 'source', 'run using MAJIC')
    setattr(outnc, 'reference', '')
    setattr(outnc, 'summary', 'Output data for JULES run with CHESS driving data for the UK')
    setattr(outnc, 'keywords', 'CHESS, JULES')
    setattr(outnc, 'date_created', str(datetime.datetime.now())[:10] )
    setattr(outnc, 'date_modified', str(datetime.datetime.now())[:10] )
    setattr(outnc, 'date_issued', str(datetime.datetime.now())[:10] )
    setattr(outnc, 'creator_name', 'MAJIC')
    setattr(outnc, 'creator_url', 'https://majic.ceh.ac.uk/')
    setattr(outnc, 'creator_email', 'majic@ceh.ac.uk')
    setattr(outnc, 'geospatial_lat_min', 49.766808 )
    setattr(outnc, 'geospatial_lat_max', 61.026794 )
    setattr(outnc, 'geospatial_lon_min', -7.55716 )
    setattr(outnc, 'geospatial_lon_max', 3.554013 )
    setattr(outnc, 'licence', 'Licensing conditions apply (datalicensing@ceh.ac.uk)')
    setattr(outnc, 'publisher_name', 'Centre for Ecology and Hydrology')
    setattr(outnc, 'publisher_url', 'http://www.ceh.ac.uk')
    setattr(outnc, 'publisher_email', 'enquiries@ceh.ac.uk')
    setattr(outnc, 'conventions', 'CF-1.6')
    setattr(outnc, 'version', 'unknown')
    setattr(outnc, 'spatial_resolution_distance', 1000)
    setattr(outnc, 'spatial_resolution_unit', 'urn:ogc:def:uom:EPSG::9001')
    setattr(outnc, 'id', '') # http://www.guidgenerator.com/
    setattr(outnc, 'history', 'created on ' + str(datetime.datetime.now())[:10])

    # Create variable Time
    outncvar = outnc.createVariable('Time', np.float32, 'Time' , zlib=zlibOp, fill_value=-99999)
    outncvar[:] = fh.variables['time'][:]
    for att in fh.variables['time'].ncattrs():
        if att != '_FillValue':
            if verbose==True:
                print '    ' + att
            setattr(outnc.variables['Time'], att, getattr(fh.variables['time'],att))

    # List of variables that have already been defined (or will be later)
    NoList = ['time','latitude','longitude']

    # Loop through the remaining variables
    for var in fh.variables:
        if var not in NoList:
            if verbose==True:
                print '\nVariable: ' + var
            line = str(fh.variables[var]).split('\n')[1]
            parenthesis = line.split('(')[1][:-1]
            elements = parenthesis.split(',')
            newDim = []
            for k in range(len(elements)):
                newDim.append(elements[k].strip())
            newDim = ['Time' if x=='time' else x for x in newDim]

            if verbose==True:
                print '  Dimensions: ' + str(newDim)

            outncvar = outnc.createVariable(var, np.float_, newDim , zlib=zlibOp, fill_value=-99999)
            outncvar[:] = fh.variables[var][:]

            # Add all the variable attributes
            for att in fh.variables[var].ncattrs():
                if att != '_FillValue':
                    if verbose==True:
                        print '    ' + att
                    setattr(outnc.variables[var], att, getattr(fh.variables[var],att))

    # create variable x
    print '\nVariable: x'

    varX = outnc.createVariable("x",np.float_, ["x"])
    varX.units = 'm'
    varX.long_name = 'easting - OSGB36 grid reference'
    varX.standard_name = 'projection_x_coordinate'
    varX.point_spacing = "even"
    rangeX = np.arange(iniX,iniX+xsize*1000,1000)
    varX[:] = rangeX

    # create variable y
    print '\nVariable: y'

    varY = outnc.createVariable("y",np.float_, ["y"])
    varY.units = 'm'
    varY.long_name = 'northing - OSGB36 grid reference'
    varY.standard_name = 'projection_x_coordinate'
    varY.point_spacing = "even"
    #rangeY = np.arange(0,1057000,1000)
    rangeY = np.arange(iniY,iniY+ysize*1000,1000)
    varY[:] = rangeY

    # create variable crs
    print '\nVariable: crs'
    coord = outnc.createVariable("crs",np.int16)
    coord.long_name = 'coordinate_reference_system'
    coord.grid_mapping_name = "transverse_mercator"
    coord.semi_major_axis = np.float_(6377563.396)
    coord.semi_minor_axis = np.float_(6356256.910)
    coord.inverse_flattening = np.float_(299.3249646)
    coord.latitude_of_projection_origin = np.float_(49.0)
    coord.longitude_of_projection_origin = np.float_(-2.0)
    coord.false_easting = np.float_(400000.0)
    coord.false_northing = np.float_(-100000.0)
    coord.scale_factor_at_projection_origin = np.float_(0.9996012717)
    coord.EPSG_code = "EPSG:27700"

    # fill in variables lat and lon
    print '\nVariable: lat and lon'

    realLatFull = np.load('Lat.npy')
    realLonFull = np.load('Lon.npy')
    realLat = realLatFull[iniY/1000:ysize,iniX/1000:xsize]
    realLon = realLonFull[iniY/1000:ysize,iniX/1000:xsize]

    latr = outnc.createVariable("latitude",np.double, ["y","x"])
    latr.long_name = 'latitude'
    latr.standard_name = 'latitude'
    latr.units = 'degrees_north'
    latr[:] = realLat

    lonr = outnc.createVariable("longitude",np.double, ["y","x"])
    lonr.long_name = 'longitude'
    lonr.standard_name = 'longitude'
    lonr.units = 'degrees_east'
    lonr[:] = realLon


    fh.close()
    outnc.close()

if __name__ == '__main__':

    inputFolder = '/scratch/emrobi/majic/eg_output/'
    #inputFolder = '/prj/lwis/maliko/CHESS_data/output_examples/'
    outputFolder = '/prj/lwis/maliko/CHESS_data/output_examples/'
    inputnetCDF = 'chess_r4_026.snapshot_2d.nc'
    #inputnetCDF = 'chess_r4.month.2012.nc'

    lastPostProcessCHESS(inputFolder,outputFolder,inputnetCDF)


'''
## If Lat.npy and Lon.npy ever need to be recreated,
## run these few lines of code

import mpl_toolkits.basemap.pyproj as pyproj

# define coordinate systems
wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum
osgb36=pyproj.Proj("+init=EPSG:27700") # UK Ordnance Survey, 1936 datum

realLat = np.zeros((1057,656))
realLon = np.zeros((1057,656))
for y in range(1057):
    if y%100 == 0:
        print y
    for x in range(656):
        Lon, Lat = pyproj.transform(osgb36, wgs84, outnc.variables['x'][x], outnc.variables['y'][y])
        #print Lon, Lat
        #print y,x
        realLat[y,x] = Lat
        realLon[y,x] = Lon
'''

