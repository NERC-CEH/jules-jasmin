from _bisect import bisect_right
from bisect import bisect_left
import logging
from threading import Thread
import os
import time
import pyper
from pydap.client import open_url
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Point

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class EcomapsAnalysis(object):
    """Runs the ecomaps R code"""

    _working_dir = None
    _user_name = None
    _user_email = None

    def __init__(self, working_dir, user_name, email):
        """Constructor:
            Params:
                working_dir: The directory we're running the code from
                user_name: Name of the user running the analysis
                email: Email address of the user running the analysis
        """
        self._working_dir = working_dir
        self._user_name = user_name
        self._user_email = email

    def _open_sample_opendap(self, url):

        #  Create points OPeNDAP object
        points = open_url(url)

        #  Create dictionary containing data columns from OPeNDAP
        column_list = []
        column_dictionary = {}
        for column in points.keys():

            if points[column].shape:

                column_list.append(column)

                # Data may have been created on a machine with a different byte order to the one on which you are running
                # Python.  To deal with this issue should convert to the native system byte order BEFORE passing it to a
                # Series/DataFrame/Panel constructor.
                # see:  http://pandas.pydata.org/pandas-docs/dev/gotchas.html#byte-ordering-issues
                column_dictionary[column] = points[column][:].byteswap().newbyteorder()

        #  Create GeoPandas GeoDataFrame from column dictionary
        ##  See 'GeoPandas - Geospatial Data in Python Made Easy' by Kelsey Jordahl
        ##  at:  http://vimeo.com/79535664.
        ##  Basic GeoPandas documentation at:  http://geopandas.org/index.html
        gdf = GeoDataFrame(column_dictionary)

        #  Re-order column order of GeoDataFrame using column list generated when points OPeNDAP accessed
        gdf = GeoDataFrame(gdf[column_list])

        #  Create geometry column in GeoDataFrame
        s = GeoSeries([Point(x, y) for x, y in zip(gdf['easting'], gdf['northing'])])
        gdf['geometry'] = s
        #  Set CRS for GeoDataFrame
        gdf.crs = {'init': 'epsg:27700', 'no_defs': True}

        del points
        return gdf

    def _get_coordinate_lists(self, url):

        # Create aggregation OPeNDAP object
        aggregation = open_url(url)

        # Set north and east dimensions
        north = aggregation['y']
        east = aggregation['x']

        # Convert north and east dimensions to lists
        north_list = list(north[:])

        east_list = list(east[:])

        # Delete north and east dimension objects
        del north, east
        # Delete aggregation object
        del aggregation
        return north_list, east_list

    def _get_landcover_array(self, url, column_name):

        # Create aggregation OPeNDAP object
        aggregation = open_url(url)

        #  Get data as numpy array
        data = aggregation[column_name]

        #  Delete aggregation object
        del aggregation
        return data

# ======================================================================================================================
##  mapToPixel function, and associated functions, plus approach bastardised from:
##  http://gis-lab.info/qa/extract-values-rasters-eng.html.  For EcoMaps both the
##  sample vector points and Land Cover Map raster are in British National Grid
##  (EPSG 27700) projection so don't need to worry about re-projecting between
##  different projection systems.

    def _mapToPixel(self, mX, mY, geoTransform):
        """Convert map coordinates to pixel coordinates.

        ##  Function and approach bastardised from http://gis-lab.info/qa/extract-values-rasters-eng.html

        @param mX              Input map X coordinate (double)
        @param mY              Input map Y coordinate (double)
        @param geoTransform    Input geotransform (six doubles)
        @return pX, pY         Output coordinates (two doubles)
        """

        if geoTransform[2] + geoTransform[4] == 0:
            pX = (mX - geoTransform[0] ) / geoTransform[1]
            pY = (mY - geoTransform[3] ) / geoTransform[5]
        else:
            pX, pY = self._applyGeoTransform(mX, mY, self._invertGeoTransform(geoTransform))

        return int(pX + 0.0), int(pY + 0.0)

    def _applyGeoTransform(self, inX, inY, geoTransform):
        """Apply a geotransform to coordinates.

        @param inX             Input coordinate (double)
        @param inY             Input coordinate (double)
        @param geoTransform    Input geotransform (six doubles)
        @return outX, outY     Output coordinates (two doubles)
        """
        outX = geoTransform[0] + inX * geoTransform[1] + inY * geoTransform[2]
        outY = geoTransform[3] + inX * geoTransform[4] + inY * geoTransform[5]
        return outX, outY

    def _invertGeoTransform(self, geoTransform):
        """Invert standard 3x2 set of geotransform coefficients.

        @param geoTransform        Input GeoTransform (six doubles - unaltered)
        @return outGeoTransform    Output GeoTransform ( six doubles - updated )
                                   on success, None if the equation is uninvertable
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

    def _find_closest(self, list, value):

        # Sort list
        list = sorted(list)
        pos = bisect_left(list, value)

        if pos==0:
            return list[0]
        if pos == len(list):
            return list[-1]
        before = list[pos - 1]
        after = list[pos]
        if after - value < value - before:
           return after
        else:
           return before


    def _geodataframe_intersect(self, north_list, east_list, dataframe,
                                array, geotransform, column_name, time_index, progress_fn):

        for count, row in dataframe.iterrows():
            northing = row['northing']
            easting = row['easting']

            xpixel, ypixel = self._mapToPixel(easting, northing, geotransform)

            # Is this temporal data? If so, we need to take a 2D slice at a point in time
            if time_index is not None:
                dataframe.loc[count, column_name] = float(array[column_name][time_index, ypixel, xpixel])
            else:
                dataframe.loc[count, column_name] = float(array[column_name][ypixel, xpixel])

        return dataframe


    def _data_frame_to_csv(self, dataframe, csv):
        # Output data frame as csv file
        print '\n\noutcsv:\t{0}'.format(csv)
        if os.path.exists(csv):
            os.remove(csv)
        dataframe.to_csv(csv, index=True, sep=',', na_rep='NA', header=True, mode='w', index_label='Count')

    def _run_r_script(self, script):
        messages = True
        if messages:
            print '\n\nR script:\t\t{0}'.format(script)
            print '\tFile last modified:\t{0}'.format(time.asctime(time.localtime(os.stat(script).st_mtime)))
        command = 'source(\'' + script + '\')'
        if messages:
            print 'command:\t{0}'.format(command)
        output = pyper.runR(command)
        if messages:
            print 'output:\t\t', output.replace('\n', '\n\t\t\t')

    def run(self, point_url, coverage_dict, progress_fn):
        """Runs the analysis
            Params;
                point_url: Location of the point netCDF file
                coverage_dict: Multiple coverage datasets, each containing a list of columns
                progress_fn: Function reference used for progress messages
        """

        # pydap is a noisy library, quieten it
        logging.getLogger("pydap").setLevel(logging.WARNING)

        progress_fn("Opening point data")
        points_gdf = self._open_sample_opendap(point_url)

        progress_fn("Opening coverage data")

        array_intersect = None

        for coverage_ds in coverage_dict.keys():

            northing_list, easting_list = self._get_coordinate_lists(coverage_ds.netcdf_url)

            if len(easting_list) > 10000:
                 pixelxsize, pixelysize = 25, -25
            else:
                #  Set array 'geotransform' properties, similar to world file (eg .tfw)
                pixelxsize, pixelysize = 1000, -1000

            arrayxorigin, arrayyorigin = 0.0, 1300000.0
            arrayxrotation, arrayyrotation = 0.0, 0.0

            #  Set array 'geotransform' list
            gt = (arrayxorigin, pixelxsize, arrayxrotation, arrayyorigin, arrayyrotation, pixelysize)

            # We may have multiple columns that we want to add
            # to the data frame, so perform an intersect for each
            for column_name, time_index in coverage_dict[coverage_ds]:

                array = self._get_landcover_array(coverage_ds.netcdf_url, column_name)

                #  Add new column to data frame to store data from coverage ds
                points_gdf[column_name] = -9999.99

                progress_fn("Setting up the analysis: %s" % column_name)

                array_intersect = self._geodataframe_intersect(northing_list, easting_list, points_gdf, array, gt, column_name, time_index,progress_fn)

        csv_folder = self._working_dir.csv_folder
        csv_file_name = 'InputRDataFile.csv'
        csv_full_path = os.path.normpath(
            os.path.join(csv_folder, csv_file_name)
        )

        progress_fn("Creating input files")
        self._data_frame_to_csv(array_intersect, csv_full_path)

        r_code_folder = self._working_dir.r_script_folder
        r_script = 'LCM_thredds_model.r'
        r_script_full_path = os.path.normpath(
            os.path.join(r_code_folder, r_script)
        )

        progress_fn("Initialising R engine")

        r = pyper.R()

        time_slices = {}
        coverage_setup = {}

        # Check each column that has been passed in, and
        # make a record of any time slice that has been tagged onto the column
        for ds, columns in coverage_dict.iteritems():
            column_list = []
            for col, time_slice in columns:
                if time_slice is not None:
                    time_slices[col] = time_slice + 1

                column_list.append(col)
            coverage_setup[ds.low_res_url] = column_list

        progress_file_path = os.path.join(self._working_dir.root_folder, 'progress.txt')

        r["coverage_setup"] = coverage_setup
        r["time_slices"] = time_slices
        r["progress_rep_file"] = progress_file_path
        r["user_name"] = self._user_name
        r["email_address"] = self._user_email
        r["csv_file"] = csv_full_path
        r["map_image_file"] = os.path.join(self._working_dir.image_folder, 'map_output.png')
        r["fit_image_file"] = os.path.join(self._working_dir.image_folder, 'fit_output.png')
        r["temp_netcdf_file"] = os.path.join(self._working_dir.netcdf_folder, 'temp.nc')
        r["output_netcdf_file"] = os.path.join(self._working_dir.netcdf_folder, 'output.nc')

        progress_fn("Starting R code")

        run_thread = Thread(target=r.run, kwargs={
            'CMDS': "source('%s')" % r_script_full_path
        })

        run_thread.start()
        while run_thread.is_alive():

            time.sleep(10)
            try:
                with open(progress_file_path, 'r') as progress_file:
                    progress_fn(progress_file.read().strip())
            except IOError:
                log.warn("Couldn't open progress file for writing")

        # Now to return the results - we're interested in where the netcdf results file
        # and the png image have been written to

        return r["output_netcdf_file"], r["map_image_file"], r["fit_image_file"]