"""
# header
"""
import logging
import datetime

from joj.model import session_scope, DrivingDataset, DrivingDatasetParameterValue, DrivingDatasetLocation
from joj.model.meta import Session
from joj.utils import constants
from joj.services.model_run_service import ModelRunService

log = logging.getLogger(__name__)


CHESS_DRIVING_DATA = \
    [
        #Jules var,  var netcdf, template,  interp, title,                                           min, max
        ['sw_down',  'rsds',     'rsds',    'nf',   'Surface Downwelling Shortwave Radiation',       0, 2000],
        ['lw_down',  'rlds',     'rlds',    'nf',   'Surface Downwelling Longwave Radiation',        0, 2000],
        ['precip',   'precip',   'precip_scaled', 'nf', 'CEH Gridded Estimates of Areal Rainfall',   0, 0.02],
        ['t',        'tas',      'tas',     'nf',   'Near-Surface Air Temperature',                  150, 400],
        ['wind',     'sfcWind',  'sfcWind', 'nf',   'Near-Surface Wind Speed',                       0, 30],
        ['q',        'huss',     'huss',    'nf',   'Near surface specific humidity',                0, 0.1],
        ['dt_range', 'dtr',      'dtr',     'nf',   'Daily temperature range',                       150, 400],
        ['pstar',    'psurf',    'psurf',   'nf',   'Surface air pressure',                          30000, 120000]
    ]

CHESS_SOIL_PROPS_FILE = "data/CHESS/ancils/chess_soilparams_hwsd_vg_copy.nc"
CHESS_LAND_FRAC_FILE = "data/CHESS/ancils/chess_landcover_2000_copy.nc"
CHESS_LATLON_FILE = "data/CHESS/ancils/chess_lat_lon.nc"
CHESS_FRAC_FILE = "data/CHESS/ancils/chess_landfrac_copy.nc"


def _create_chess_data_basic(conf):
    chess_driving_dataset = DrivingDataset()
    chess_driving_dataset.name = "UK CHESS Forcing Data"
    chess_driving_dataset.description = \
        "The Climate, Hydrochemistry and Economics of Surface-water Systems (CHESS)" \
        " project has explored effects of climate change on the water quality of European" \
        " rivers, with the purpose of informing future catchment management."
    chess_driving_dataset.geographic_region = 'UK'
    chess_driving_dataset.temporal_resolution = '24 Hours'
    chess_driving_dataset.spatial_resolution = '1 km'
    chess_driving_dataset.boundary_lat_north = 10
    chess_driving_dataset.boundary_lat_south = -10
    chess_driving_dataset.boundary_lon_west = -170
    chess_driving_dataset.boundary_lon_east = 170
    chess_driving_dataset.time_start = datetime.datetime(1961, 1, 1, 12, 0, 0)
    if conf['full_data_range'].lower() == "true":
        chess_driving_dataset.time_end = datetime.datetime(1999, 1, 1, 17, 0, 0)
    else:
        chess_driving_dataset.time_end = datetime.datetime(1961, 1, 31, 17, 0, 0)
    chess_driving_dataset.view_order_index = 200
    chess_driving_dataset.usage_order_index = 1
    chess_driving_dataset.is_restricted_to_admins = True

    return chess_driving_dataset


def _create_regions(driving_dataset):
    #cat1 = LandCoverRegionCategory()
    #cat1.name = "Test Regions"
    #cat1.driving_dataset = driving_dataset
    #region1 = LandCoverRegion()
    #region1.name = "Equator Horizontal Strip (20 deg)"
    #region1.category = cat1
    #region1.mask_file = "data/CHESS/masks/equator-20-degree-horizontal-strip.nc"
    pass


def _create_chess_parameters_and_locations(cover_dst, land_cover_frac_dst, soild_prop_dst, driving_dataset, conf):
    file_template = 'data/CHESS/driving/chess_{}_copy.ncml'

    vars = ""
    templates = ""
    interps = ""
    var_names = ""
    for jules_var, var, template, interp, title, min, max in CHESS_DRIVING_DATA:
        location = DrivingDatasetLocation()
        location.base_url = file_template.format(template)
        location.dataset_type = cover_dst
        location.driving_dataset = driving_dataset
        vars += "'{}' ".format(jules_var)
        templates += "'{}' ".format(template)
        interps += "'{}' ".format(interp)
        var_names += "'{}' ".format(var)
    nvars = len(CHESS_DRIVING_DATA)

    DrivingDatasetLocation(
        dataset_type=soild_prop_dst,
        base_url=CHESS_SOIL_PROPS_FILE,
        driving_dataset=driving_dataset)

    DrivingDatasetLocation(
        dataset_type=land_cover_frac_dst,
        base_url=CHESS_LAND_FRAC_FILE,
        driving_dataset=driving_dataset)

    jules_parameters = [
        [constants.JULES_PARAM_FRAC_FILE, ("'%s'" % CHESS_FRAC_FILE)],
        [constants.JULES_PARAM_FRAC_NAME, "'frac'"],

        [constants.JULES_PARAM_SOIL_PROPS_NVARS, "9"],
        [constants.JULES_PARAM_SOIL_PROPS_USE_FILE, ".true. .true. .true. .true. .true. .true. .true. .true. .false."],
        [constants.JULES_PARAM_SOIL_PROPS_FILE, ("'%s'" % CHESS_SOIL_PROPS_FILE)],
        [constants.JULES_PARAM_SOIL_PROPS_VAR,
         "'b'       'sathh'  'satcon'  'sm_sat'  'sm_crit'  'sm_wilt'  'hcap'      'hcon'   'albsoil'"],
        [constants.JULES_PARAM_SOIL_PROPS_VAR_NAME,
         "'oneovernminusone' 'oneoveralpha' 'satcon'  'vsat'  'vcrit'  'vwilt'     'hcap'    'hcon'  'albsoil'"],

        [constants.JULES_PARAM_SOIL_PROPS_CONST_VAL, ".true."],

        [constants.JULES_PARAM_INITIAL_NVARS, "8"],
        [constants.JULES_PARAM_INITIAL_VAR,
         "'sthuf' 'canopy' 'snow_tile' 'rgrain' 'tstar_tile' 't_soil' 'cs' 'gs'"],
        [constants.JULES_PARAM_INITIAL_USE_FILE,
         ".false.  .false.  .false.  .false.  .false.  .false.  .false.  .false."],
        [constants.JULES_PARAM_INITIAL_CONST_VAL,
         "0.9     0.0      0.0         50.0     275.0        278.0    10.0 0.0"],

        [constants.JULES_PARAM_DRIVE_DATA_START, "'1961-01-01 00:00:00'"],
        [constants.JULES_PARAM_DRIVE_DATA_PERIOD, "86400"],
        [constants.JULES_PARAM_DRIVE_FILE, "'data/CHESS/driving/chess_%vv_%y4%m2_copy.nc'"],
        [constants.JULES_PARAM_DRIVE_NVARS, nvars],
        [constants.JULES_PARAM_DRIVE_VAR, vars],
        [constants.JULES_PARAM_DRIVE_VAR_NAME, var_names],
        [constants.JULES_PARAM_DRIVE_TPL_NAME, templates],
        [constants.JULES_PARAM_DRIVE_INTERP, interps],
        [constants.JULES_PARAM_DRIVE_Z1_TQ_IN, "1.2"],
        [constants.JULES_PARAM_DRIVE_Z1_UV_IN, "10.0"],

        [constants.JULES_PARAM_INPUT_GRID_IS_1D, ".false."],
        [constants.JULES_PARAM_INPUT_GRID_NX, "656"],
        [constants.JULES_PARAM_INPUT_GRID_NY, "1057"],
        [constants.JULES_PARAM_INPUT_GRID_X_DIM_NAME, "'x'"],
        [constants.JULES_PARAM_INPUT_GRID_Y_DIM_NAME, "'y'"],
        [constants.JULES_PARAM_INPUT_TIME_DIM_NAME, "'Time'"],
        [constants.JULES_PARAM_INPUT_TYPE_DIM_NAME, "'z'"],
        [constants.JULES_PARAM_INPUT_SOIL_DIM_NAME, "'z'"],
        [constants.JULES_PARAM_INPUT_PFT_DIM_NAME, "'pft'"],

        [constants.JULES_PARAM_LATLON_FILE, ("'%s'" % CHESS_LATLON_FILE)],
        [constants.JULES_PARAM_LATLON_LAT_NAME, "'lat'"],
        [constants.JULES_PARAM_LATLON_LON_NAME, "'lon'"],

        [constants.JULES_PARAM_LAND_FRAC_FILE, ("'%s'" % CHESS_LAND_FRAC_FILE)],
        [constants.JULES_PARAM_LAND_FRAC_LAND_FRAC_NAME, "'landfrac'"],

        [constants.JULES_PARAM_SURF_HGT_ZERO_HEIGHT, ".true."],


    ]

    if conf['full_data_range'].lower() == "true":
        jules_parameters.append([constants.JULES_PARAM_DRIVE_DATA_END, "'2001-12-31 21:00:00'"])
    else:
        jules_parameters.append([constants.JULES_PARAM_DRIVE_DATA_END, "'1901-01-31 21:00:00'"])

    model_run_service = ModelRunService()
    for constant, value in jules_parameters:
        log.info("  adding parameter {}::{}".format(constant[0], constant[1]))
        DrivingDatasetParameterValue(model_run_service, driving_dataset, constant, value)


def create_chess_driving_data(conf, cover_dst, land_cover_frac_dst, soil_prop_dst):
    """
    Create the chess driving dataset
    :param conf: configuration
    :param cover_dst: cover data set type
    :param land_cover_frac_dst: land cover fraction data set type
    :param soil_prop_dst:  soil property data set type
    :return: name of dataset
    """

    log.info("Creating Chess Driving Dataset:")

    with session_scope(Session) as session:
        chess_driving_dataset = _create_chess_data_basic(conf)
        _create_regions(chess_driving_dataset)
        _create_chess_parameters_and_locations(
            cover_dst,
            land_cover_frac_dst,
            soil_prop_dst,
            chess_driving_dataset,
            conf)
        session.add(chess_driving_dataset)

    return chess_driving_dataset.name
