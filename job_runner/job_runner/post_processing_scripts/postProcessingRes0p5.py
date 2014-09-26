"""  Script to convert JULES output Data netCDF files to gridded netCDF files

  Version : modified by Maliko Tanguy (malngu@ceh.ac.uk)
              Changes made for the code to be more generic, so that it can
              handle different timesteps, and any number of variables.

              Changes made on 2014-07-2014

  Simon Wright
  CEH Lancaster
  2014-05-23
"""

import sys
import os
import datetime
import timeit
import time
from dateutil import rrule
from datetime import date, timedelta
import calendar
import csv
from shapely.geometry import Point, MultiPoint
import numpy as np
import netCDF4
from osgeo import ogr
import mpl_toolkits.basemap.pyproj as pyproj
from dateutil.rrule import rrule, MONTHLY, DAILY, HOURLY


# ======================================================================================================================
##  mapToPixel function, and associated functions, plus approach bastardised from:
##  http://gis-lab.info/qa/extract-values-rasters-eng.html.  For EcoMaps both the
##  sample vector points and Land Cover Map raster are in British National Grid
##  (EPSG 27700) projection so don't need to worry about re-projecting between
##  different projection systems.

def mapToPixel(mX, mY, geoTransform):
    """Convert map coordinates to pixel coordinates.

    @param mX              Input map X coordinate (double)
    @param mY              Input map Y coordinate (double)
    @param geoTransform    Input geotransform (six doubles)
    @return pX, pY         Output coordinates (two doubles)

    Bastardised from:  http://gis-lab.info/qa/extract-values-rasters-eng.html

    """
    if geoTransform[2] + geoTransform[4] == 0:
        pX = (mX - geoTransform[0] ) / geoTransform[1]
        pY = (mY - geoTransform[3] ) / geoTransform[5]
    else:
        pX, pY = applyGeoTransform(mX, mY, invertGeoTransform(geoTransform))
    ##return int(pX + 0.5), int(pY + 0.5)
    ##return int(round(pX + 0.5)), int(round(pY + 0.5))
    return int(pX + 0.0), int(pY + 0.0)


def applyGeoTransform(inX, inY, geoTransform):
    """Apply a geotransform to coordinates.

    @param inX             Input coordinate (double)
    @param inY             Input coordinate (double)
    @param geoTransform    Input geotransform (six doubles)
    @return outX, outY     Output coordinates (two doubles)

    Bastardised from:  http://gis-lab.info/qa/extract-values-rasters-eng.html

    """
    outX = geoTransform[0] + inX * geoTransform[1] + inY * geoTransform[2]
    outY = geoTransform[3] + inX * geoTransform[4] + inY * geoTransform[5]
    return outX, outY


def invertGeoTransform(geoTransform):
    """Invert standard 3x2 set of geotransform coefficients.

    @param geoTransform        Input GeoTransform (six doubles - unaltered)
    @return outGeoTransform    Output GeoTransform ( six doubles - updated )
                               on success, None if the equation is uninvertable

    Bastardised from:  http://gis-lab.info/qa/extract-values-rasters-eng.html

    """
    # we assume a 3rd row that is [ 1 0 0 ]
    # compute determinate
    det = geoTransform[1] * geoTransform[5] - geoTransform[2] * geoTransform[4]
    if abs(det) < 0.000000000000001:
        return
    invDet = 1.0 / det
    # compute adjoint and divide by determinate
    outGeoTransform = [0, 0, 0, 0, 0, 0]
    outGeoTransform[1] = geoTransform[5] * invDet
    outGeoTransform[4] = -geoTransform[4] * invDet
    outGeoTransform[2] = -geoTransform[2] * invDet
    outGeoTransform[5] = geoTransform[1] * invDet
    outGeoTransform[0] = (geoTransform[2] * geoTransform[3] - geoTransform[0] * geoTransform[5] ) * invDet
    outGeoTransform[3] = (-geoTransform[1] * geoTransform[3] + geoTransform[0] * geoTransform[4] ) * invDet
    return outGeoTransform


##  End of functions bastardised from:
##  http://gis-lab.info/qa/extract-values-rasters-eng.html

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
# ======================================================================================================================


def convert1Din2D(inputFolder, outputFolder, inputFileName, verbose=False):
    """
    Convert 1D data into a 2D grid
    :param inputFolder: folder in which orginal file is stored
    :param outputFolder:  folder to output new file to
    :param inputFileName: filename of the file
    :param verbose: True to print more information on convert
    :return: nothing
    """

    # Names of special dimensions
    # The time dimension as it must appear in the final file
    DIM_TIME_FINAL = 'Time'

    #The time timension that should be replaced if it appears in 1D file
    DIM_TIME_ORIGINAL = 'time'

    MISSINGVALUE = -9999.99

    ROOTFOLDER = inputFolder

    netcdffolder = ROOTFOLDER

    # Define WGS84proj
    wgs84proj = pyproj.Proj('+init=EPSG:4326')

    #  Set spatial resolution
    resolution = 0.5

    #  Define coordinate netcCDF file
    coordinatenetCDFFile = os.path.join(ROOTFOLDER, inputFileName)

    #  Open cordinate netCDF file
    fh = netCDF4.Dataset(coordinatenetCDFFile, mode='r')

    print 'Dimensions:'
    for elem in fh.dimensions:
        print elem

    yDim = fh.dimensions[u'y']

#######################################################################
####################### IF JULES OUTPUT IS 1D #########################
#######################################################################

    if len(yDim) == 1:

        #  Create multipoint geometry object
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)

        #  Define arrays to hold point longitude, latitude and Z values

        longitude = fh.variables['longitude'][:]
        latitude = fh.variables['latitude'][:]

        if verbose==True:
            print '\n\nMISSINGVALUE:\t\t\t\t\t{0}'.format(MISSINGVALUE)
            print '\n\nROOTFOLDER:\t\t\t\t\t\t{0}'.format(ROOTFOLDER)
            print '\n\nnetcdffolder:\t\t\t\t\t{0}'.format(netcdffolder)
            print '\n\nwgs84proj.srs:\t\t\t\t\t{0}'.format(wgs84proj.srs)
            print '\n\nresolution:\t\t\t\t\t\t{0}'.format(resolution)
            print '\n\ncoordinatenetCDFFile:\t\t\tS{0}'.format(coordinatenetCDFFile)
            print '\n\nlongitude:\t\t\t\t\t\t{0}'.format(longitude)
            print 'latitude:\t\t\t\t\t\t{0}'.format(latitude)

        #  Close coordinates netCDF file
        fh.close()

        #  Add netCDF coordinate file points to multipoint geometry object
        for i in range(0, longitude.size):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(float(longitude[0][i]), float(latitude[0][i]))
            multipoint.AddGeometry(point)
            del point
        del i

        #  Delete point longitude, latitude and Z arrays
        del longitude, latitude

        #  Examine multipoint geomtery object
        if verbose==True:
            print '\n\nmultipoint.GetGeometryCount():\t{0}'.format(multipoint.GetGeometryCount())
            print '\n\nmultipoint.GetEnvelope():\t\t{0}'.format(multipoint.GetEnvelope())


        # Get bottom left corner and upper right corner in EPSG:4326 ((WGS1984) from multipoint envelope
        llcornerll = (multipoint.GetEnvelope()[0], multipoint.GetEnvelope()[2])
        urcornerll = (multipoint.GetEnvelope()[1], multipoint.GetEnvelope()[3])
        if verbose==True:
            print '\n\nnllcornerll:\t\t\t\t\t{0}'.format(llcornerll)
            print 'urcornerll:\t\t\t\t\t\t{0}'.format(urcornerll)


        ylength = multipoint.GetEnvelope()[3] - multipoint.GetEnvelope()[2]
        rows = (ylength / resolution) + 1

        xlength = multipoint.GetEnvelope()[1] - multipoint.GetEnvelope()[0]
        cols = (xlength / resolution) + 1

        if verbose==True:
            print '\n\nrows:\t\t\t\t\t\t\t{0}'.format(rows)
            print 'cols:\t\t\t\t\t\t\t{0}'.format(cols)


        #  Define arrays for coordinate x and y values
        yi = np.linspace(multipoint.GetEnvelope()[2], multipoint.GetEnvelope()[3], num=rows, endpoint=True)
        xi = np.linspace(multipoint.GetEnvelope()[0], multipoint.GetEnvelope()[1], num=cols, endpoint=True)

        # Set geotransformation tuple for converting coordinates to array indices.
        # For the WATCH Forcing Data (WFD) no transformation is required as not
        # converting between different projections just creating gridded netCDF
        # files from 1-dimensional netCDF files.
        gt = (multipoint.GetEnvelope()[0], resolution, 0.0, multipoint.GetEnvelope()[2], 0.0, resolution)


        #  Set NetCDF format
        netcdfformat = 'NETCDF4'
        #  Set compression option for NetCDF4 files
        zlib = True
        #  Check NetCDF format and compression option are compatible
        if netcdfformat == 'NETCDF3_CLASSIC' and zlib:
            print '\n' * 5 + \
                  '*' * 5 + \
                  '  Cannot use compression with NETCDF3_CLASSIC NetDCF format files!  ' + \
                  '*' * 5 + \
                  '\n' * 5
            sys.exit()

        #  Define source folder
        sourcefolder = ROOTFOLDER
        if verbose==True:
            print '\n\nsourcefolder:\t\t\t\t\t{0}'.format(sourcefolder)
            #
            #  Processing loop
            print '\n\nLooping...'
        #
        #  Define input netCDF file
        inputnetCDF = os.path.join(sourcefolder, inputFileName)
        #
        #   Open input netCDF file
        fh = netCDF4.Dataset(inputnetCDF, mode='r')

        #
        #  Create out NetCDF file
        outputnetcdffile = os.path.join(outputFolder, inputFileName)
        #outputnetcdffile = inputFileName[:-3] + '_2D.nc'
        if verbose==True:
            print '\t\t#\n\t\toutputnetcdffile:\t\t{0}\n\t\t#'.format(outputnetcdffile)

        if os.path.exists(outputnetcdffile):
            os.remove(outputnetcdffile)
        outnc = netCDF4.Dataset(outputnetcdffile, 'w', format=netcdfformat)

        #
        #  Create out NetDCF file attributes
        setattr(outnc, 'title', 'WATCH OUTPUT Data')
        setattr(outnc, 'institution', 'Centre for Ecology & Hydrology (CEH) Wallingford')
        setattr(outnc, 'source', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'reference', 'reference')
        setattr(outnc, 'description', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'grid_mapping', 'crs')
        setattr(outnc, 'history', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'summary', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'keywords', 'WATCH, Output Data, WFD')
        setattr(outnc, 'date_created', date.today().strftime('%Y-%m-%d'))
        setattr(outnc, 'date_modified', date.today().strftime('%Y-%m-%d'))
        setattr(outnc, 'date_issued', date.today().strftime('%Y-%m-%d'))
        setattr(outnc, 'creator_name', 'MAJIC')
        setattr(outnc, 'creator_url', 'https://majic.ceh.ac.uk/')
        setattr(outnc, 'creator_email', 'majic@ceh.ac.uk')
        setattr(outnc, 'geospatial_lon_min', multipoint.GetEnvelope()[0] - (resolution * 0.5))
        setattr(outnc, 'geospatial_lat_min', multipoint.GetEnvelope()[2] - (resolution * 0.5))
        setattr(outnc, 'geospatial_lon_max', multipoint.GetEnvelope()[1] + (resolution * 0.5))
        setattr(outnc, 'geospatial_lat_max', multipoint.GetEnvelope()[3] + (resolution * 0.5))

        setattr(outnc, 'licence', 'https://majic.ceh.ac.uk/docs/majic_terms_and_conditions.pdf')
        setattr(outnc, 'publisher_name', 'Centre for Ecology & Hydrology')
        setattr(outnc, 'publisher_url', 'http://www.ceh.ac.uk')
        setattr(outnc, 'publisher_email', 'enquiries@ceh.ac.uk')
        setattr(outnc, 'Conventions', 'CF-1.6')
        setattr(outnc, 'comment', 'Created using Python script converting WATCH WFD 1-Dimensinal to gridded netCDF fiels')
        #
        #  Define varibales to hold minimum and maximum parameter values (for output
        #  netCDF file valid_min and valid_max attributes
        parameterminvalue = MISSINGVALUE * MISSINGVALUE
        parametermaxvalue = MISSINGVALUE
        #
        #  Define list for time steps
        timelist = []
        #
        #  Interval output flag
        outputinterval = False

        #
        # Create netCDF dimensions (the same as in the original file,
        # except x and y)
        for dim in fh.dimensions.values():

            names = str(dim).split("'")
            name = names[3]
            if (name != 'x') and (name != 'y'):
                sizes = str(dim).split(' ')
                size = sizes[len(sizes)-1]
                if verbose == True:
                    print 'Creating dimension ' + name + ' of size '+ size
                if (name == DIM_TIME_ORIGINAL):
                    name = DIM_TIME_FINAL
                outnc.createDimension(name, int(size))

    ##
    ##    #
    ##    #  Create out netCDF file time dimension
    ##    outncdimtime = outnc.createDimension('Time', len(timelist))
        #
        #  Create out netCDF file latitude dimension
        outncdimy = outnc.createDimension('Latitude', rows)
        #
        #  Create out netCDF file longitude dimension
        outncdimx = outnc.createDimension('Longitude', cols)

    ##     #  Create out netCDF file longitude dimension
    ##    outncdimx = outnc.createDimension('nt', 2)
        #
        #  Create out netCDF file time bounds variable
        outncvartime = outnc.createVariable('time_bounds', 'f8', (DIM_TIME_FINAL,'nt'), zlib=zlib)
        outncvartime[:] = fh.variables['time_bounds']
        for att in fh.variables['time_bounds'].ncattrs():
            setattr(outncvartime, att, getattr(fh.variables['time_bounds'],att))

        #  Create out netCDF file time variable
        outncvartime = outnc.createVariable('Time', 'f8', (DIM_TIME_FINAL), zlib=zlib)
        outncvartime[:] = fh.variables[DIM_TIME_ORIGINAL]
        for att in fh.variables[DIM_TIME_ORIGINAL].ncattrs():
            setattr(outncvartime, att, getattr(fh.variables[DIM_TIME_ORIGINAL],att))
        intervals = len(outncvartime)
        if verbose==True:
            print '\t\t#\n\t\tintervals:\t\t\t\t{0}'.format(intervals)

        #
        # Transform netcdf time units into datetime units
        if intervals > 0:
            t1 = outncvartime[0]
            t2 = outncvartime[intervals-1]
        else:
            t1 = 0
            t2 = 0

        netcdfUnits = getattr(fh.variables[DIM_TIME_ORIGINAL],'units')

        startdatetime = netcdf2datetime(t1, netcdfUnits)
        enddatetime = netcdf2datetime(t2, netcdfUnits)
        setattr(outnc, 'time_coverage_start', str(startdatetime))
        setattr(outnc, 'time_coverage_end', str(enddatetime))

        #
        #  Create out netCDF file latitude variable
        outncvary = outnc.createVariable('Latitude', 'f8', ('Latitude'), zlib=zlib)
        outncvary[:] = yi
        setattr(outncvary, 'long_name', 'Latitude')
        setattr(outncvary, 'units', 'degrees_north')
        #
        #  Create out netCDF file longitude variable
        outncvarx = outnc.createVariable('Longitude', 'f8', ('Longitude'), zlib=zlib)
        outncvarx[:] = xi
        setattr(outncvarx, 'long_name', 'Longitude')
        setattr(outncvarx, 'units', 'degrees_east')

        # List of variables that have already been defined
        NoList = [DIM_TIME_ORIGINAL,'time_bounds','Time','longitude','Longitude','latitude','Latitude']

        # Loop through the remaining variables
        for var in fh.variables:
            if var not in NoList:
                if verbose==True:
                    print '\nVariable: ' + var
                #
                # Define new variable shape
                varShape = np.shape(fh.variables[var])

                outVarShape = []
                for i in range(len(varShape)-2):
                    outVarShape.append(varShape[i])
                outVarShape.append(rows)
                outVarShape.append(cols)


                #
                # Define new variable dimensions

                line = str(fh.variables[var]).split('\n')[1]
                parenthesis = line.split('(')[1][:-1]
                elements = parenthesis.split(',')
                newDim = []
                for k in range(len(elements)-2):
                    if elements[k].strip() != DIM_TIME_ORIGINAL:
                        newDim.append(elements[k].strip())
                    else:
                        newDim.append(DIM_TIME_FINAL)
                newDim.append('Latitude')
                newDim.append('Longitude')
                if verbose==True:
                    print '  Dimensions: ' + str(newDim)

                #
                #  Define the empty month array
                #array = np.empty((intervals, rows, cols), dtype=np.float)
                array = np.empty(outVarShape, dtype=np.float)

                array.fill(MISSINGVALUE)
                if verbose==True:
                    print '\t\t#\n\t\tarray.shape:\t\t\t{0}'.format(array.shape)
                    print '\t\tarray.size:\t\t\t\t{0}'.format(array.size)

                values = None
                #
                # If variable is 3 dimensional
                if len(newDim)==3:
                    # Loop through timesteps
                    for i in range(intervals):
                        values = fh.variables[var][i]
                        #  Update minimum and maximum parameter values
                        parameterminvalue = min(parameterminvalue, float(np.amin(values)))
                        parametermaxvalue = max(parametermaxvalue, float(np.amax(values)))

                        #
                        #  Print interval
                        if outputinterval:
                            if verbose == True:
                                print '\t\t\t{0:>3}:\t\t\t\t{1}'.format(i, dh)

                        #  Loop for all points in multipoint geomtery object
                        for j in range(0, multipoint.GetGeometryCount()):
                            point = multipoint.GetGeometryRef(j)

                            xpixel, ypixel = mapToPixel(point.GetX(), point.GetY(), gt)

                            array[i][ypixel][xpixel] = values[0][j]

                #
                # If variable is 4 dimensional
                if len(newDim)==4:
                    secondDim=outVarShape[1]

                    # Loop through timesteps
                    for tile in range(int(secondDim)):
                        for i in range(intervals):
                            values = fh.variables[var][i][tile]
                            #  Update minimum and maximum parameter values
                            parameterminvalue = min(parameterminvalue, float(np.amin(values)))
                            parametermaxvalue = max(parametermaxvalue, float(np.amax(values)))

                            #
                            #  Print interval
                            if outputinterval:
                                if verbose == True:
                                    print '\t\t\t{0:>3}:\t\t\t\t{1}'.format(i, dh)

                            #  Loop for all points in multipoint geomtery object
                            for j in range(0, multipoint.GetGeometryCount()):
                                point = multipoint.GetGeometryRef(j)

                                xpixel, ypixel = mapToPixel(point.GetX(), point.GetY(), gt)

                                array[i][tile][ypixel][xpixel] = values[0][j]

                #
                # If variable is 5 dimensional
                if len(newDim)==5:
                    secondDim = outVarShape[1]
                    thirdDim = outVarShape[2]

                    # Loop through timesteps
                    for tile2 in range(int(thirdDim)):
                        for tile in range(int(secondDim)):
                            for i in range(intervals):
                                values = fh.variables[var][i][tile][tile2]
                                #  Update minimum and maximum parameter values
                                parameterminvalue = min(parameterminvalue, float(np.amin(values)))
                                parametermaxvalue = max(parametermaxvalue, float(np.amax(values)))

                                #
                                #  Print interval
                                if outputinterval:
                                    if verbose == True:
                                        print '\t\t\t{0:>3}:\t\t\t\t{1}'.format(i, dh)

                                #  Loop for all points in multipoint geomtery object
                                for j in range(0, multipoint.GetGeometryCount()):
                                    point = multipoint.GetGeometryRef(j)

                                    xpixel, ypixel = mapToPixel(point.GetX(), point.GetY(), gt)

                                    array[i][tile][tile2][ypixel][xpixel] = values[0][j]
                #
                # If variable is 6 dimensional
                if len(newDim)==6:
                    secondDim = outVarShape[1]
                    thirdDim = outVarShape[2]
                    fourthDim = outVarShape[3]

                    # Loop through timesteps
                    for tile3 in range(int(fourthDim)):
                        for tile2 in range(int(thirdDim)):
                            for tile in range(int(secondDim)):

                                for i in range(intervals):
                                    values = fh.variables[var][i][tile][tile2][tile3]
                                    #  Update minimum and maximum parameter values
                                    parameterminvalue = min(parameterminvalue, float(np.amin(values)))
                                    parametermaxvalue = max(parametermaxvalue, float(np.amax(values)))

                                    #
                                    #  Print interval
                                    if outputinterval:
                                        if verbose == True:
                                            print '\t\t\t{0:>3}:\t\t\t\t{1}'.format(i, dh)

                                    #  Loop for all points in multipoint geomtery object
                                    for j in range(0, multipoint.GetGeometryCount()):
                                        point = multipoint.GetGeometryRef(j)

                                        xpixel, ypixel = mapToPixel(point.GetX(), point.GetY(), gt)

                                        array[i][tile][tile2][tile3][ypixel][xpixel] = values[0][j]

                #
                # If variable is 7 dimensional
                if len(newDim)==7:
                    secondDim = outVarShape[1]
                    thirdDim = outVarShape[2]
                    fourthDim = outVarShape[3]
                    fifthDim = outVarShape[4]

                    # Loop through timesteps
                    for tile4 in range(int(fifthDim)):
                        for tile3 in range(int(fourthDim)):
                            for tile2 in range(int(thirdDim)):
                                for tile in range(int(secondDim)):

                                    for i in range(intervals):
                                        values = fh.variables[var][i][tile][tile2][tile3][tile4]
                                        #  Update minimum and maximum parameter values
                                        parameterminvalue = min(parameterminvalue, float(np.amin(values)))
                                        parametermaxvalue = max(parametermaxvalue, float(np.amax(values)))

                                        #
                                        #  Print interval
                                        if outputinterval:
                                            if verbose == True:
                                                print '\t\t\t{0:>3}:\t\t\t\t{1}'.format(i, dh)

                                        #  Loop for all points in multipoint geomtery object
                                        for j in range(0, multipoint.GetGeometryCount()):
                                            point = multipoint.GetGeometryRef(j)

                                            xpixel, ypixel = mapToPixel(point.GetX(), point.GetY(), gt)

                                            array[i][tile][tile2][tile3][tile4][ypixel][xpixel] = values[0][j]

                # If variable has more than 7 dimensions: unsupported
                if len(newDim) > 7:
                    print 'Variables with 8 dimensions or greater are unsupported. \n\
                            The array will be left empty'

                #  Delete values numpy array
                if values is not None:
                    del values

                #  Create out netCDF parameter variable
                #outncvar = outnc.createVariable(var, 'f8', ('Time', 'Latitude', 'Longitude'), zlib=zlib, fill_value=MISSINGVALUE)
                outncvar = outnc.createVariable(var, 'f8', newDim, zlib=zlib, fill_value=MISSINGVALUE)

                if len(newDim) <= 7:
                    outncvar[:] = array

                for att in fh.variables[var].ncattrs():
                    if att != '_FillValue':
                        if verbose==True:
                            print '    ' + att
                        setattr(outncvar, att, getattr(fh.variables[var],att))

        if outputinterval:
            print '\t\t#'

        #
        #  Close input netCDF file and delete fh object
        fh.close()
        del fh
        #
        #  Delete paramater minimum and maximum values
        del parameterminvalue, parametermaxvalue
        #
        #  Delete outnc dimensions and variables
        #del outncdimtime
        del outncdimy, outncdimx
        del outncvartime, outncvary, outncvarx, outncvar
        #
        #  Close the out netCDF file and delete outnc object
        outnc.close()
        del outnc
        #
        #  Delete the empty month array
        del array
        #
        #  Delete the time list
        del timelist
        #
        if verbose==True:
            print '\t#\nLooped.'

        #  Delete arrays for evenly-space coordinate x and y values
        del yi, xi

        #  Delete multipoint object
        del multipoint

#######################################################################
####################### IF JULES OUTPUT IS 2D #########################
#######################################################################

    elif len(yDim) > 1:

        #  Create multipoint geometry object
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)

        #  Define arrays to hold point longitude, latitude and Z values

        longitude = fh.variables['longitude'][:]
        latitude = fh.variables['latitude'][:]

        if verbose==True:
            print '\n\nMISSINGVALUE:\t\t\t\t\t{0}'.format(MISSINGVALUE)
            print '\n\nROOTFOLDER:\t\t\t\t\t\t{0}'.format(ROOTFOLDER)
            print '\n\nnetcdffolder:\t\t\t\t\t{0}'.format(netcdffolder)
            print '\n\nwgs84proj.srs:\t\t\t\t\t{0}'.format(wgs84proj.srs)
            print '\n\nresolution:\t\t\t\t\t\t{0}'.format(resolution)
            print '\n\ncoordinatenetCDFFile:\t\t\tS{0}'.format(coordinatenetCDFFile)
            print '\n\nlongitude:\t\t\t\t\t\t{0}'.format(longitude)
            print 'latitude:\t\t\t\t\t\t{0}'.format(latitude)

        #  Close coordinates netCDF file
        fh.close()




        #  Set NetCDF format
        netcdfformat = 'NETCDF4'
        #  Set compression option for NetCDF4 files
        zlib = True
        #  Check NetCDF format and compression option are compatible
        if netcdfformat == 'NETCDF3_CLASSIC' and zlib:
            print '\n' * 5 + \
                  '*' * 5 + \
                  '  Cannot use compression with NETCDF3_CLASSIC NetDCF format files!  ' + \
                  '*' * 5 + \
                  '\n' * 5
            sys.exit()

        #  Define source folder
        sourcefolder = ROOTFOLDER
        if verbose==True:
            print '\n\nsourcefolder:\t\t\t\t\t{0}'.format(sourcefolder)
            #
            #  Processing loop
            print '\n\nLooping...'
        #
        #  Define input netCDF file
        inputnetCDF = os.path.join(sourcefolder, inputFileName)
        #
        #   Open input netCDF file
        fh = netCDF4.Dataset(inputnetCDF, mode='r')

        #
        #  Create out NetCDF file
        outputnetcdffile = os.path.join(outputFolder, inputFileName)
        #outputnetcdffile = inputFileName[:-3] + '_2D.nc'
        if verbose==True:
            print '\t\t#\n\t\toutputnetcdffile:\t\t{0}\n\t\t#'.format(outputnetcdffile)

        if os.path.exists(outputnetcdffile):
            os.remove(outputnetcdffile)
        outnc = netCDF4.Dataset(outputnetcdffile, 'w', format=netcdfformat)

        #
        #  Create out NetDCF file attributes
        setattr(outnc, 'title', 'WATCH OUTPUT Data')
        setattr(outnc, 'institution', 'Centre for Ecology & Hydrology (CEH) Wallingford')
        setattr(outnc, 'source', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'reference', 'reference')
        setattr(outnc, 'description', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'grid_mapping', 'crs')
        setattr(outnc, 'history', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'summary', 'Derived from WATCH 1D Output Data')
        setattr(outnc, 'keywords', 'WATCH, Output Data, WFD')
        setattr(outnc, 'date_created', date.today().strftime('%Y-%m-%d'))
        setattr(outnc, 'date_modified', date.today().strftime('%Y-%m-%d'))
        setattr(outnc, 'date_issued', date.today().strftime('%Y-%m-%d'))
        setattr(outnc, 'creator_name', 'MAJIC')
        setattr(outnc, 'creator_url', 'https://majic.ceh.ac.uk/')
        setattr(outnc, 'creator_email', 'majic@ceh.ac.uk')
        setattr(outnc, 'geospatial_lon_min', multipoint.GetEnvelope()[0] - (resolution * 0.5))
        setattr(outnc, 'geospatial_lat_min', multipoint.GetEnvelope()[2] - (resolution * 0.5))
        setattr(outnc, 'geospatial_lon_max', multipoint.GetEnvelope()[1] + (resolution * 0.5))
        setattr(outnc, 'geospatial_lat_max', multipoint.GetEnvelope()[3] + (resolution * 0.5))

        setattr(outnc, 'licence', 'https://majic.ceh.ac.uk/docs/majic_terms_and_conditions.pdf')
        setattr(outnc, 'publisher_name', 'Centre for Ecology & Hydrology')
        setattr(outnc, 'publisher_url', 'http://www.ceh.ac.uk')
        setattr(outnc, 'publisher_email', 'enquiries@ceh.ac.uk')
        setattr(outnc, 'Conventions', 'CF-1.6')
        setattr(outnc, 'comment', 'Created using Python script converting WATCH WFD 1-Dimensinal to gridded netCDF fiels')
        #
        #  Define varibales to hold minimum and maximum parameter values (for output
        #  netCDF file valid_min and valid_max attributes
        parameterminvalue = MISSINGVALUE * MISSINGVALUE
        parametermaxvalue = MISSINGVALUE
        #
        #  Define list for time steps
        timelist = []
        #
        #  Interval output flag
        outputinterval = False

        #
        # Create netCDF dimensions (the same as in the original file,
        # except x and y)
        for dim in fh.dimensions.values():

            names = str(dim).split("'")
            name = names[3]
            #if (name != 'x') and (name != 'y'):
            sizes = str(dim).split(' ')
            size = sizes[len(sizes)-1]
            if verbose == True:
                print 'Creating dimension ' + name + ' of size '+ size
            if (name == DIM_TIME_ORIGINAL):
                name = DIM_TIME_FINAL
            if name == 'x':
                xsize = size
            elif name == 'y':
                ysize = size
            if (name != 'x') and (name != 'y'):
                outnc.createDimension(name, int(size))


        #
        #  Create out netCDF file latitude dimension
        outncdimy = outnc.createDimension('Latitude', int(ysize))
        #
        #  Create out netCDF file longitude dimension
        outncdimx = outnc.createDimension('Longitude', int(xsize))


        #
        #  Create out netCDF file time bounds variable
        outncvartime = outnc.createVariable('time_bounds', 'f8', (DIM_TIME_FINAL,'nt'), zlib=zlib)
        outncvartime[:] = fh.variables['time_bounds']
        for att in fh.variables['time_bounds'].ncattrs():
            setattr(outncvartime, att, getattr(fh.variables['time_bounds'],att))

        #  Create out netCDF file time variable
        outncvartime = outnc.createVariable('Time', 'f8', (DIM_TIME_FINAL), zlib=zlib)
        outncvartime[:] = fh.variables[DIM_TIME_ORIGINAL]
        for att in fh.variables[DIM_TIME_ORIGINAL].ncattrs():
            setattr(outncvartime, att, getattr(fh.variables[DIM_TIME_ORIGINAL],att))
        intervals = len(outncvartime)
        if verbose==True:
            print '\t\t#\n\t\tintervals:\t\t\t\t{0}'.format(intervals)

        #
        # Transform netcdf time units into datetime units
        if intervals > 0:
            t1 = outncvartime[0]
            t2 = outncvartime[intervals-1]
        else:
            t1 = 0
            t2 = 0

        netcdfUnits = getattr(fh.variables[DIM_TIME_ORIGINAL],'units')

        startdatetime = netcdf2datetime(t1,netcdfUnits)
        enddatetime = netcdf2datetime(t2,netcdfUnits)
        setattr(outnc, 'time_coverage_start', str(startdatetime))
        setattr(outnc, 'time_coverage_end', str(enddatetime))

        #
        #  Create out netCDF file latitude variable

        outncvary = outnc.createVariable('Latitude', 'f8', ('Latitude'), zlib=zlib)
        outncvary[:] = fh.variables['latitude'][:,0]
        setattr(outncvary, 'long_name', 'Latitude')
        setattr(outncvary, 'units', 'degrees_north')
        #
        #  Create out netCDF file longitude variable

        outncvarx = outnc.createVariable('Longitude', 'f8', ('Longitude'), zlib=zlib)
        outncvarx[:] = fh.variables['longitude'][0,:]
        setattr(outncvarx, 'long_name', 'Longitude')
        setattr(outncvarx, 'units', 'degrees_east')

        # List of variables that have already been defined
        NoList = [DIM_TIME_ORIGINAL,'time_bounds','Time','longitude','Longitude','latitude','Latitude']

        # Loop through the remaining variables
        for var in fh.variables:
            if var not in NoList:
                if verbose==True:
                    print '\nVariable: ' + var
                #
                # Define new variable shape
                varShape = np.shape(fh.variables[var])
                print varShape


                # Define new variable dimensions

                line = str(fh.variables[var]).split('\n')[1]
                parenthesis = line.split('(')[1][:-1]
                elements = parenthesis.split(',')
                newDim = []
                for k in range(len(elements)-2):
                    if elements[k].strip() != DIM_TIME_ORIGINAL:
                        newDim.append(elements[k].strip())
                    else:
                        newDim.append(DIM_TIME_FINAL)
                newDim.append('Latitude')
                newDim.append('Longitude')

                if verbose==True:
                    print '  Dimensions: ' + str(newDim)

                outncvar = outnc.createVariable(var, 'f8', newDim, zlib=zlib, fill_value=MISSINGVALUE)
                outncvar[:] = fh.variables[var]
                for att in fh.variables[var].ncattrs():
                    if att != '_FillValue':
                        if verbose==True:
                            print '    ' + att
                        setattr(outncvar, att, getattr(fh.variables[var],att))



        if outputinterval:
            print '\t\t#'

        #
        #  Close input netCDF file and delete fh object
        fh.close()
        del fh
        #

        #
        #  Delete outnc dimensions and variables
        #del outncdimtime
        del outncdimy, outncdimx
        del outncvartime, outncvary, outncvarx, outncvar
        #
        #  Close the out netCDF file and delete outnc object
        outnc.close()
        del outnc
        #

        #
        #  Delete the time list
        del timelist
        #
        if verbose==True:
            print '\t#\nLooped.'

        #  Delete multipoint object
        del multipoint



if __name__ == '__main__':

    # ==============================================================
    # INPUT PARAMETERS
    # ==============================================================
    inputFolder = '/prj/lwis/maliko/JULES_JASMIN/'
    outputFolder = '/prj/lwis/maliko/JULES_JASMIN/output'
    ##inputFileName = 'arcc_global.daily_gb.1979.nc'
    ##inputFileName = 'arcc_global.monthly.1979_2D.nc'
    inputFileName = 'majic_land.nc'
    ##inputFileName = 'jules-output_land_and_sea.nc'
    ##inputFileName = 'jules-output-horizontal-transect.nc'
    # ==============================================================

    timeitstart = timeit.default_timer()
    timestart = time.clock()

    print '\n\n', datetime.datetime.now()

    convert1Din2D(inputFolder,outputFolder,inputFileName,verbose=True)

    print '\n\n', datetime.datetime.now()

    timeitstop = timeit.default_timer()
    print '\n\ntimeit:\t{0:.1f} seconds.'.format(timeitstop - timeitstart)

    timestop = time.clock()
    print '\n\ntime:\t{0:.1f} seconds.'.format(timestop - timestart)


    # ======================================================================================================================

print '\n'

