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
        ['dt_range', 'dtr',      'dtr',     'nf',   'Daily temperature range',                       150, 400],
        ['sw_down',  'rsds',     'rsds',    'nf',   'Surface Downwelling Shortwave Radiation',       0, 2000],
        ['lw_down',  'rlds',     'rlds',    'nf',   'Surface Downwelling Longwave Radiation',        0, 2000],
        ['precip',   'precip',   'precip_scaled', 'nf', 'CEH Gridded Estimates of Areal Rainfall',   0, 0.02],
        ['t',        'tas',      'tas',     'nf',   'Near-Surface Air Temperature',                  150, 400],
        ['wind',     'sfcWind',  'sfcWind', 'nf',   'Near-Surface Wind Speed',                       0, 30],
        ['q',        'huss',     'huss',    'nf',   'Near surface specific humidity',                0, 0.1],
        ['pstar',    'psurf',    'psurf',   'nf',   'Surface air pressure',                          30000, 120000]
    ]

CHESS_SOIL_PROPS_FILE = "data/CHESS/ancils/chess_soilparams_hwsd_vg_copy.nc"
CHESS_LAND_FRAC_FILE = "data/CHESS/ancils/chess_landfrac_copy.nc"
CHESS_LATLON_FILE = "data/CHESS/ancils/chess_lat_lon.nc"
CHESS_FRAC_FILE = "data/CHESS/ancils/chess_landcover_2000_copy.nc"


def _create_chess_data_basic(conf):
    chess_driving_dataset = DrivingDataset()
    chess_driving_dataset.name = "UK CHESS Forcing Data"
    chess_driving_dataset.description = \
        "A daily meteorological forcing dataset: based on MORECS at 40km and downscaled to 1km using sub-grid scale " \
        "topography. See Robinson et al, 2014. manuscript in prep."
    chess_driving_dataset.geographic_region = 'UK'
    chess_driving_dataset.temporal_resolution = '24 Hours'
    chess_driving_dataset.spatial_resolution = '1 km'
    chess_driving_dataset.boundary_lat_north = 59
    chess_driving_dataset.boundary_lat_south = 50
    chess_driving_dataset.boundary_lon_west = -7.5
    chess_driving_dataset.boundary_lon_east = 1.5
    chess_driving_dataset.time_start = datetime.datetime(1961, 1, 1, 0, 0, 0)
    if conf['full_data_range'].lower() == "true":
        chess_driving_dataset.time_end = datetime.datetime(1999, 1, 1, 0, 0, 0)
    else:
        chess_driving_dataset.time_end = datetime.datetime(1961, 1, 31, 0, 0, 0)
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
        location.var_name = jules_var
        vars += "'{}' ".format(jules_var)
        templates += "'{}' ".format(template)
        interps += "'{}' ".format(interp)
        var_names += "'{}' ".format(var)
    nvars = len(CHESS_DRIVING_DATA)

    jules_parameters = [
        [constants.JULES_PARAM_MODEL_LEVELS_ICE_INDEX, "-1"],
        [constants.JULES_PARAM_MODEL_LEVELS_NNVG, "3"],

        [constants.JULES_PARAM_FRAC_FILE, ("'%s'" % CHESS_FRAC_FILE)],
        [constants.JULES_PARAM_FRAC_NAME, "'frac'"],

        [constants.JULES_PARAM_SOIL_PROPS_NVARS, "9"],
        [constants.JULES_PARAM_SOIL_PROPS_USE_FILE, ".true. .true. .true. .true. .true. .true. .true. .true. .false."],
        [constants.JULES_PARAM_SOIL_PROPS_FILE, ("'%s'" % CHESS_SOIL_PROPS_FILE)],
        [constants.JULES_PARAM_SOIL_PROPS_VAR,
         "'b'       'sathh'  'satcon'  'sm_sat'  'sm_crit'  'sm_wilt'  'hcap'      'hcon'   'albsoil'"],
        [constants.JULES_PARAM_SOIL_PROPS_VAR_NAME,
         "'oneovernminusone' 'oneoveralpha' 'satcon'  'vsat'  'vcrit'  'vwilt'     'hcap'    'hcon'  'albsoil'"],

        [constants.JULES_PARAM_SOIL_PROPS_CONST_VAL, "0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.15"],

        [constants.JULES_PARAM_INITIAL_NVARS, "10"],
        [constants.JULES_PARAM_INITIAL_VAR,
         "'sthuf' 'canopy' 'snow_tile' 'rgrain' 'tstar_tile' 't_soil' 'cs' 'gs'  'lai' 'canht'"],
        [constants.JULES_PARAM_INITIAL_USE_FILE,
         ".false.  .false.  .false.  .false.  .false.  .false.  .false.  .false. .false.  .false."],
        [constants.JULES_PARAM_INITIAL_CONST_VAL,
         "0.9     0.0      0.0         50.0     275.0        278.0    10.0   0.0   1.0   2.0"],


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

        [constants.JULES_PARAM_DRIVE_L_DAILY_DISAGG, ".true."],
        [constants.JULES_PARAM_DRIVE_L_DISAGG_RH, ".true."],
        [constants.JULES_PARAM_DRIVE_PRECIP_DISAGG_METHOD, "3"],
        [constants.JULES_PARAM_DRIVE_DIFF_FRAC_CONST, "0.4"],
        [constants.JULES_PARAM_DRIVE_T_FOR_SNOW, "275.15"],
        [constants.JULES_PARAM_DRIVE_T_FOR_CON_RAIN, "288.15"],
        [constants.JULES_PARAM_DRIVE_DUR_CONV_RAIN, "7200.0"],
        [constants.JULES_PARAM_DRIVE_DUR_LS_RAIN, "18000.0"],
        [constants.JULES_PARAM_DRIVE_DUR_LS_SNOW, "18000.0"],

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

        [constants.JULES_PARAM_POST_PROCESSING_ID, "0"],

        [constants.JULES_PARAM_SWITCHES_L_VG_SOIL, ".true."]
    ]

    extra_pft_parameters = [
        ["pftname_io          ", "   'BT'      'NT'     'grass' 'shrub'     'crop'"],
        ["canht_ft_io         ", " 19.01     16.38      0.79      1.00      0.79"],
        ["lai_io              ", "   5.0       4.0       2.0       1.0       2.0"],

        ["c3_io               ", "     1         1         1         1         1"],
        ["orient_io           ", "     0         0         0         0         0"],
        ["a_wl_io             ", "  0.65      0.65     0.005      0.10     0.005"],
        ["a_ws_io             ", " 10.00     10.00      1.00     10.00      1.00"],
        ["albsnc_max_io       ", "  0.15      0.15      0.60      0.40      0.60"],
        ["albsnc_min_io       ", "  0.30      0.30      0.80      0.80      0.80"],
        ["albsnf_max_io       ", "  0.10      0.10      0.20      0.20      0.20"],
        ["dz0v_dh_io          ", "  0.05      0.05      0.10      0.10      0.10"],
        ["catch0_io           ", "  0.50      0.50      0.50      0.50      0.50"],
        ["dcatch_dlai_io      ", "  0.05      0.05      0.05      0.05      0.05"],
        ["infil_f_io          ", "  4.00      4.00      2.00      2.00      2.00"],
        ["kext_io             ", "  0.50      0.50      0.50      0.50      0.50"],
        ["rootd_ft_io         ", "  3.00      1.00      0.50      0.50      0.50"],
        ["z0hm_pft_io         ", "  0.10      0.10      0.10      0.10      0.10"],
        ["alpha_io            ", "  0.08      0.08      0.08      0.08      0.08"],
        ["alnir_io            ", "  0.45      0.35      0.58      0.58      0.58"],
        ["alpar_io            ", "  0.10      0.07      0.10      0.10      0.10"],
        ["b_wl_io             ", " 1.667     1.667     1.667     1.667     1.667"],
        ["dgl_dm_io           ", "   0.0       0.0       0.0       0.0       0.0"],
        ["dgl_dt_io           ", "   9.0       9.0       0.0       9.0       0.0"],
        ["dqcrit_io           ", " 0.090     0.060     0.100     0.100     0.100"],
        ["eta_sl_io           ", "  0.01      0.01      0.01      0.01      0.01"],
        ["fd_io               ", " 0.015     0.015     0.015     0.015     0.015"],
        ["fsmc_of_io          ", "  0.00      0.00      0.00      0.00      0.00"],
        ["f0_io               ", " 0.875     0.875     0.900     0.900     0.900"],
        ["g_leaf_0_io         ", "  0.25      0.25      0.25      0.25      0.25"],
        ["glmin_io            ", "1.0E-6    1.0E-6    1.0E-6    1.0E-6    1.0E-6"],
        ["kpar_io             ", "  0.50      0.50      0.50      0.50      0.50"],
        ["neff_io             ", "0.8e-3    0.8e-3    0.8e-3    0.8e-3    0.8e-3"],
        ["nl0_io              ", " 0.040     0.030     0.060     0.030     0.060"],
        ["nr_nl_io            ", "  1.00      1.00      1.00      1.00      1.00"],
        ["ns_nl_io            ", "  0.10      0.10      1.00      0.10      1.00"],
        ["omega_io            ", "  0.15      0.15      0.15      0.15      0.15"],
        ["omnir_io            ", "  0.70      0.45      0.83      0.83      0.83"],
        ["r_grow_io           ", "  0.25      0.25      0.25      0.25      0.25"],
        ["sigl_io             ", "0.0375    0.1000    0.0250    0.0500    0.0250"],
        ["tleaf_of_io         ", "273.15    243.15    258.15    243.15    258.15"],
        ["tlow_io             ", "   0.0      -5.0       0.0       0.0       0.0"],
        ["tupp_io             ", "  36.0      31.0      36.0      36.0      36.0"],
        ["emis_pft_io         ", "  0.97      0.97      0.97      0.97      0.97"],

        ["fl_o3_ct_io         ", "   1.6       1.6       5.0       1.6       5.0"],
        ["dfp_dcuo_io         ", "  0.04      0.02      0.25      0.03      0.25"],

        ["ief_io              ", "  35.0      12.0      16.0      20.0      16.0"],
        ["tef_io              ", "  0.40      2.40      0.80      0.80      0.80"],
        ["mef_io              ", "  0.60      0.90      0.60      0.57      0.60"],
        ["aef_io              ", "  0.18      0.21      0.12      0.20      0.12"],

        ["z0hm_classic_pft_io ", "   0.1       0.1       0.1       0.1       0.1"],

        ["albsnf_maxu_io      ", " 0.215     0.132     0.288     0.173     0.288"],
        ["albsnf_maxl_io      ", " 0.095     0.059     0.128     0.077     0.128"],
        ["alniru_io           ", "  0.68      0.53      0.87      0.87      0.87"],
        ["alnirl_io           ", "  0.30      0.23      0.39      0.39      0.39"],
        ["alparu_io           ", "  0.15      0.11      0.15      0.15      0.15"],
        ["alparl_io           ", "  0.06      0.04      0.06      0.06      0.06"],
        ["omegau_io           ", "  0.23      0.23      0.23      0.23      0.23"],
        ["omegal_io           ", "  0.10      0.10      0.10      0.10      0.10"],
        ["omniru_io           ", "  0.90      0.65      0.98      0.98      0.98"],
        ["omnirl_io           ", "  0.50      0.30      0.53      0.53      0.53"]]
    for name, value in extra_pft_parameters:
        parameter_constant = [constants.JULES_NML_PFTPARM, name.strip()]
        jules_parameters.append([parameter_constant, value])

    if conf['full_data_range'].lower() == "true":
        jules_parameters.append([constants.JULES_PARAM_DRIVE_DATA_END, "'2013-01-01 00:00:00'"])
    else:
        jules_parameters.append([constants.JULES_PARAM_DRIVE_DATA_END, "'1961-01-31 00:00:00'"])

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
