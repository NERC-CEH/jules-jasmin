"""
# header
"""

import datetime
import logging

from joj.model import session_scope, DrivingDataset, DrivingDatasetParameterValue, DrivingDatasetLocation, \
    LandCoverRegionCategory, LandCoverRegion
from joj.model.meta import Session
from joj.utils import constants
from joj.services.model_run_service import ModelRunService

log = logging.getLogger(__name__)

WATCH_DRIVING_DATA = \
    [
        ['PSurf_WFD/PSurf_WFD', 'pstar', 'Surface pressure', 30000, 120000],
        ['Tair_WFD/Tair_WFD', 't', 'Near surface air temperature at 2m', 150, 400],
        ['Qair_WFD/Qair_WFD', 'q', 'Near surface specific humidity at 2m', 0, 0.1],
        ['Wind_WFD/Wind_WFD', 'wind', 'Near surface wind speed at 10m', 0, 30],
        ["LWdown_WFD/LWdown_WFD", 'lw_down', "Surface incident longwave radiation", 0, 2000],
        ['SWdown_WFD/SWdown_WFD', 'sw_down', 'Surface incident shortwave radiation', 0, 2000],
        ['Rainf_WFD_GPCC/Rainf_WFD_GPCC', 'tot_rain', 'Rainfall rate', 0, 0.02],
        ['Snowf_WFD_GPCC/Snowf_WFD_GPCC', 'tot_snow', 'Snowfall rate', 0, 0.004]
    ]

WATCH_SOIL_PROPS_FILE = "data/WATCH_2D/ancils/soil_igbp_bc_watch_0p5deg_capUM6.6_2D.nc"
WATCH_FRAC_FILE = "data/WATCH_2D/ancils/frac_igbp_watch_0p5deg_capUM6.6_2D.nc"
WATCH_LAND_FRAC_FILE = "data/WATCH_2D/ancils/WFD-land-lat-long-z_2D.nc"
WATCH_LATLON_FILE = "data/WATCH_2D/ancils/WFD-land-lat-long-z_2D.nc"


def _create_watch_driving_data_basic(conf):
    watch_driving_dataset = DrivingDataset()
    watch_driving_dataset.name = "WATCH Forcing Data 20th Century"
    watch_driving_dataset.description = \
        "A sub-diurnal meteorological forcing dataset: based on ERA-40 for the sub-monthly variability, " \
        "tuned to CRU monthly observations. " \
        "See Weedon et al, 2011, Journal of Hydrometeorology, doi: 10.1175/2011JHM1369.1"
    watch_driving_dataset.geographic_region = 'Global'
    watch_driving_dataset.temporal_resolution = '3 Hours'
    watch_driving_dataset.spatial_resolution = '0.5 Degrees'
    watch_driving_dataset.boundary_lat_north = 84
    watch_driving_dataset.boundary_lat_south = -56
    watch_driving_dataset.boundary_lon_west = -180
    watch_driving_dataset.boundary_lon_east = 180
    watch_driving_dataset.time_start = datetime.datetime(1901, 1, 1, 0, 0, 0)
    if conf['full_data_range'].lower() == "true":
        watch_driving_dataset.time_end = datetime.datetime(2001, 12, 31, 21, 0, 0)
    else:
        watch_driving_dataset.time_end = datetime.datetime(1901, 1, 31, 21, 0, 0)
    watch_driving_dataset.view_order_index = 100
    watch_driving_dataset.usage_order_index = 2
    watch_driving_dataset.is_restricted_to_admins = False
    return watch_driving_dataset


def _create_watch_regions(watch_driving_dataset, regions_csv_file):
    categories = []
    f = open(regions_csv_file, "r")
    for line in f:
        stripped_line = line.strip()
        if not stripped_line.startswith('#') and len(stripped_line) > 0:
            values = line.split(',')
            if len(values) != 3:
                log.error("Regions csv file has incorrect number of elements on line reading %s" % stripped_line)
                exit(-1)
            category_name = values[0].strip()
            cat = None
            for category in categories:
                if category.name == category_name:
                    cat = category

            if cat is None:
                log.info("  adding category {}".format(category_name))
                cat = LandCoverRegionCategory(name=category_name)
                cat.driving_dataset = watch_driving_dataset
                categories.append(cat)

            region = LandCoverRegion()
            region.name = values[1].strip()
            region.mask_file = "data/WATCH_2D/masks/{}".format(values[2].strip())
            region.category = cat
            log.info("  adding region {} to {} with file {}".format(region.name, category_name, region.mask_file))
    f.close()


def _create_watch_parameters_and_locations(cover_dst, land_cover_frac_dst, soild_prop_dst, watch_driving_dataset, conf):

    file_template = 'data/WATCH_2D/driving/{}.ncml'
    for path, var, name, min, max in WATCH_DRIVING_DATA:
        location = DrivingDatasetLocation()
        location.base_url = file_template.format(path)
        location.dataset_type = cover_dst
        location.driving_dataset = watch_driving_dataset
        location.var_name = var

    watch_jules_parameters = [
        [constants.JULES_PARAM_DRIVE_DATA_START, "'1901-01-01 00:00:00'"],
        [constants.JULES_PARAM_DRIVE_DATA_PERIOD, "10800"],
        [constants.JULES_PARAM_DRIVE_FILE, "'data/WATCH_2D/driving/%vv/%vv_%y4%m2.nc'"],
        [constants.JULES_PARAM_DRIVE_NVARS, "8"],
        [constants.JULES_PARAM_DRIVE_VAR,
         "'pstar'      't'         'q'         'wind'      'lw_down'     'sw_down'     "
         "'tot_rain'        'tot_snow'"],
        [constants.JULES_PARAM_DRIVE_VAR_NAME, "'PSurf'      'Tair'      'Qair'      'Wind'      'LWdown'      "
                                               "'SWdown'      'Rainf'           'Snowf'"],
        [constants.JULES_PARAM_DRIVE_TPL_NAME, "'PSurf_WFD'      'Tair_WFD'      "
                                               "'Qair_WFD'      'Wind_WFD'      'LWdown_WFD'      'SWdown_WFD'     "
                                               "'Rainf_WFD_GPCC'           'Snowf_WFD_GPCC'"],
        [constants.JULES_PARAM_DRIVE_INTERP,
         "'i'          'i'         'i'         'i'         'nf'          'nf'          'nf'              'nf'"],
        [constants.JULES_PARAM_DRIVE_Z1_TQ_IN, "2.0"],
        [constants.JULES_PARAM_DRIVE_Z1_UV_IN, "10.0"],

        [constants.JULES_PARAM_INPUT_GRID_IS_1D, ".false."],
        [constants.JULES_PARAM_INPUT_GRID_NX, "720"],
        [constants.JULES_PARAM_INPUT_GRID_NY, "280"],
        [constants.JULES_PARAM_INPUT_GRID_X_DIM_NAME, "'Longitude'"],
        [constants.JULES_PARAM_INPUT_GRID_Y_DIM_NAME, "'Latitude'"],
        [constants.JULES_PARAM_INPUT_TIME_DIM_NAME, "'Time'"],
        [constants.JULES_PARAM_INPUT_TYPE_DIM_NAME, "'pseudo'"],

        [constants.JULES_PARAM_LATLON_FILE, ("'%s'" % WATCH_LATLON_FILE)],
        [constants.JULES_PARAM_LATLON_LAT_NAME, "'Grid_lat'"],
        [constants.JULES_PARAM_LATLON_LON_NAME, "'Grid_lon'"],
        [constants.JULES_PARAM_LAND_FRAC_FILE, ("'%s'" % WATCH_LAND_FRAC_FILE)],
        [constants.JULES_PARAM_LAND_FRAC_LAND_FRAC_NAME, "'land'"],
        [constants.JULES_PARAM_SURF_HGT_ZERO_HEIGHT, ".true."],

        [constants.JULES_PARAM_FRAC_FILE, ("'%s'" % WATCH_FRAC_FILE)],
        [constants.JULES_PARAM_FRAC_NAME, "'frac'"],

        [constants.JULES_PARAM_SOIL_PROPS_CONST_Z, ".true."],
        [constants.JULES_PARAM_SOIL_PROPS_FILE, ("'%s'" % WATCH_SOIL_PROPS_FILE)],
        [constants.JULES_PARAM_SOIL_PROPS_NVARS, "9"],
        [constants.JULES_PARAM_SOIL_PROPS_VAR,
         "'b'       'sathh'  'satcon'  'sm_sat'  'sm_crit'  'sm_wilt'  'hcap'      'hcon'   'albsoil'"],
        [constants.JULES_PARAM_SOIL_PROPS_VAR_NAME,
         "'bexp'    'sathh'  'satcon'  'vsat'    'vcrit'    'vwilt'    'hcap'      'hcon'   'albsoil'"],

        [constants.JULES_PARAM_INITIAL_NVARS, "10"],
        [constants.JULES_PARAM_INITIAL_VAR,
         "'sthuf' 'canopy' 'snow_tile' 'rgrain' 'tstar_tile' 't_soil' 'cs' 'gs'  'lai' 'canht'"],
        [constants.JULES_PARAM_INITIAL_USE_FILE,
         ".false.  .false.  .false.  .false.  .false.  .false.  .false.  .false. .false.  .false."],
        [constants.JULES_PARAM_INITIAL_CONST_VAL,
         "0.9     0.0      0.0         50.0     275.0        278.0    10.0   0.0   1.0   2.0"],

        [constants.JULES_PARAM_POST_PROCESSING_ID, "1"]
    ]

    if conf['full_data_range'].lower() == "true":
        watch_jules_parameters.append([constants.JULES_PARAM_DRIVE_DATA_END, "'2001-12-31 21:00:00'"])
    else:
        watch_jules_parameters.append([constants.JULES_PARAM_DRIVE_DATA_END, "'1901-01-31 21:00:00'"])

    model_run_service = ModelRunService()
    for constant, value in watch_jules_parameters:
        log.info("  adding parameter {}::{}".format(constant[0], constant[1]))
        DrivingDatasetParameterValue(model_run_service, watch_driving_dataset, constant, value)


def create_watch_driving_data(conf, cover_dst, land_cover_frac_dst, soil_prop_dst, regions_csv_file):
    """
    Create the watch driving data
    :param conf: configuration
    :param cover_dst: cover data set type
    :param land_cover_frac_dst: land cover fraction data set type
    :param soil_prop_dst:  soil property data set type
    :return: name of dataset
    """
    log.info("Creating Watch Driving Dataset:")
    with session_scope(Session) as session:
        watch_driving_dataset = _create_watch_driving_data_basic(conf)
        _create_watch_regions(watch_driving_dataset, regions_csv_file)
        _create_watch_parameters_and_locations(
            cover_dst,
            land_cover_frac_dst,
            soil_prop_dst,
            watch_driving_dataset,
            conf)
        session.add(watch_driving_dataset)

    return watch_driving_dataset.name
