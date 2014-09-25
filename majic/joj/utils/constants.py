"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
General constants for the project
"""

# Database table constants
DB_STRING_SIZE = 255  # Default size (chars) to use when creating strings for simple names
DB_LONG_STRING_SIZE = 1000  # Default size (chars) to use when creating descriptions
DB_PARAMETER_VALUE_STRING_SIZE = 1000  # Default size (chars) to use for a Jules name list value
DB_URL_STRING_SIZE = 1000  # Default size (chars) to use when creating urls
DB_PATH_SIZE = 4000  # Default size (chars) to use for a file path

#Username for the core user, The core user will have scientific configurations and model runs
CORE_USERNAME = 'system'

USER_ACCESS_LEVEL_ADMIN = "Admin"
USER_ACCESS_LEVEL_CEH = "CEH"
USER_ACCESS_LEVEL_EXTERNAL = "External"

QUOTA_WARNING_LIMIT_PERCENT = 80
QUOTA_ABSOLUTE_LIMIT_PERCENT = 100

#Size to cache when read file for a generator
GENERATORS_SIZE_TO_READ = 100000
GENERATORS_LINES_TO_READ = 100

# Time in hours that a UUID for a forgotten password is valid for
FORGOTTEN_PASSWORD_UUID_VALID_TIME = 24
PASSWORD_MINIMUM_LENGTH = 10

# The default science configuration to use
DEFAULT_SCIENCE_CONFIGURATION = 2

# Model Run status descriptions *** If you update these update the same ones in job runner****
MODEL_RUN_STATUS_CREATED = 'Created'
MODEL_RUN_STATUS_SUBMITTED = 'Submitted'
MODEL_RUN_STATUS_PENDING = 'Pending'
MODEL_RUN_STATUS_RUNNING = 'Running'
MODEL_RUN_STATUS_COMPLETED = 'Completed'
MODEL_RUN_STATUS_PUBLISHED = 'Published'
MODEL_RUN_STATUS_FAILED = 'Failed'
MODEL_RUN_STATUS_SUBMIT_FAILED = 'Submission Failed'  # user submitted a model but it can not be submitted
MODEL_RUN_STATUS_UNKNOWN = 'Unknown'  # Job is in the bjobs list but the status is not understood

# Error messages
ERROR_MESSAGE_NO_STATUS_RETURNED = 'No status has been returned from the job runner'
ERROR_MESSAGE_QUOTA_EXCEEDED = "You have exceeded your quota and can no longer create a new model run; " \
                               "any changes you made have been saved. " \
                               "Please delete or publish one of your model runs" \
                               " to reduce the amount of storage you are using."

# Parameter types
PARAMETER_TYPE_INTEGER = 'integer'  # parameter is an integer (case is from documentation)

# Constants for the names of the dictionary values in the json submitted
JSON_MODEL_RUN_ID = 'model_run_id'
JSON_MODEL_RUN_ID_TO_DUPLICATE_FROM = 'model_run_to_duplicate_from'
JSON_MODEL_CODE_VERSION = 'code_version'
JSON_MODEL_NAMELISTS = 'namelists'
JSON_MODEL_NAMELIST_FILES = 'namelist_files'
JSON_MODEL_PARAMETERS = 'parameters'
JSON_MODEL_NAMELIST_NAME = 'name'
JSON_MODEL_NAMELIST_INDEX = 'index'
JSON_MODEL_NAMELIST_GROUP_ID = 'group_id'
JSON_MODEL_NAMELIST_FILE_FILENAME = 'filename'
# These are used for transferring files from the web app to the job runner (e.g. user uploaded driving datasets)
JSON_MODEL_FILENAME = 'filename'
JSON_MODEL_FILE_LINE = 'line'
JOB_RUNNER_CLIENT_FILE_CHUNK_BYTES = 100*1024

JSON_USER_NAME = 'user_name'
JSON_USER_ID = 'user_id'
JSON_USER_EMAIL = 'user_email'

JSON_STATUS_STORAGE = 'storage_in_mb'
JSON_STATUS_START_TIME = 'start_time'
JSON_STATUS_END_TIME = 'end_time'

JSON_LAND_COVER = 'land_cover'
JSON_LAND_COVER_ACTIONS = 'land_cover_actions'
JSON_LAND_COVER_MASK_FILE = 'land_cover_mask_file'
JSON_LAND_COVER_BASE_FILE = 'land_cover_base_file'
JSON_LAND_COVER_BASE_KEY = 'land_cover_base_key'
JSON_LAND_COVER_VALUE = 'land_cover_value'
JSON_LAND_COVER_ORDER = 'land_cover_order'
JSON_LAND_COVER_POINT_EDIT = "land_cover_point_edit"
JSON_LAND_COVER_FRACTIONAL_VALS = "land_cover_fractional_vals"
JSON_LAND_COVER_LAT = "land_cover_lat"
JSON_LAND_COVER_LON = "land_cover_lon"
JSON_LAND_COVER_ICE_INDEX = "land_cover_ice_index"

# Constants for reading netCDF files
NETCDF_LATITUDE = ['Latitude', 'lat']
NETCDF_LONGITUDE = ['Longitude', 'lon']
NETCDF_TIME = ['Time']
NETCDF_TIME_BOUNDS = ['time_bounds', 'timestp', 'timestep']
NETCDF_CRS = ['crs']
NETCDF_CRS_X = ['x']
NETCDF_CRS_Y = ['y']

# Max number of points to get for graph:
GRAPH_NPOINTS = 1000
# Date time string format used by the graph / visualisation.
GRAPH_TIME_FORMAT = "%Y-%m-%dT%X.%fZ"

#The name of the driving dataset which represents the 'upload your own driving dataset' option
USER_UPLOAD_DRIVING_DATASET_NAME = "Use My Own Single Cell Driving Data"
USER_UPLOAD_FILE_NAME = "user_uploaded_driving_data.dat"  # The name of the file we store user driving data in
USER_UPLOAD_DATE_FORMAT = "%Y-%m-%d %H:%M"
USER_UPLOAD_ALLOWED_VARS = ['pstar', 'q', 't', 'rad_net', 'sw_down', 'lw_down', 'lw_net', 'sw_net', 'diff_rad',
                            'precip', 'tot_rain', 'tot_snow', 'ls_rain', 'con_rain', 'ls_snow', 'con_snow',
                            'wind', 'u', 'v']
USER_UPLOAD_ALLOWED_INTERPS = ['b', 'c', 'f', 'i', 'nb', 'nc', 'nf']
USER_DOWNLOAD_DATA_FILE_EXTENSION = ".dat"
USER_DOWNLOAD_CACHE_SIZE = 10000  # Number of timesteps to cache when downloading driving data

# These two dictionaries allow us to identify which interpolation flags need extra driving data steps at the start
# or end of a run.
INTERPS_EXTRA_STEPS_RUN_START = {'b': 0, 'c': 1, 'f': 1, 'i': 0, 'nb': 0, 'nc': 0, 'nf': 0}
INTERPS_EXTRA_STEPS_RUN_END = {'b': 2, 'c': 2, 'f': 1, 'i': 1, 'nb': 1, 'nc': 1, 'nf': 1}

FRACTIONAL_FILENAME = 'fractional.dat'
FRACTIONAL_ICE_NAME = 'Ice'
USER_EDITED_FRACTIONAL_FILENAME = 'user_edited_land_cover_fractional_file.nc'

# Some JULES output variables depend on the value of nsmax being > 0 - keep a record of those names here:
DEPENDS_ON_NSMAX = ['snow_ice_gb', 'snow_liq_gb', 'snow_ice_tile', 'snow_liq_tile',
                    'rgrainl', 'snow_ds', 'snow_ice', 'snow_liq', 'tsnow']

# Set the timestep length in seconds
TIMESTEP_LEN = 30 * 60  # half an hour

# Sets the spin up duration in years (can not be 0)
SPINUP_MAX_TIME_RANGE_YEARS = 5

# Set the name of the run and consequently the name of the output files
RUN_ID = "majic"

# Set the name of the output directory (if changed copy to job_runner)
OUTPUT_DIR = 'output'

# prefix of driving var variables
PREFIX_FOR_DRIVING_VARS = 'drive_var_'

# input name of land cover fraction file name parameter
LAND_COVER_FRAC_FILE_INPUT_NAME = 'frac_file'

# Periods for jules output
JULES_YEARLY_PERIOD = -2
JULES_MONTHLY_PERIOD = -1
JULES_DAILY_PERIOD = 24 * 60 * 60
JULES_HOURLY_PERIOD = 60 * 60

#Month abbreviations for templates
JULES_MONTH_ABBREVIATIONS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

# Constants for Jules Parameters (so we can easily update if they change name etc)
# 3 tuple, name list name, parameter name, if present True/false is this a list
JULES_NML_MODEL_GRID = "JULES_MODEL_GRID"
JULES_PARAM_USE_SUBGRID = [JULES_NML_MODEL_GRID, "use_subgrid"]
JULES_PARAM_LATLON_REGION = [JULES_NML_MODEL_GRID, "latlon_region"]
JULES_PARAM_LAT_BOUNDS = [JULES_NML_MODEL_GRID, "lat_bounds"]
JULES_PARAM_LON_BOUNDS = [JULES_NML_MODEL_GRID, "lon_bounds"]
JULES_PARAM_NPOINTS = [JULES_NML_MODEL_GRID, "npoints"]
JULES_PARAM_POINTS_FILE = [JULES_NML_MODEL_GRID, "points_file"]

JULES_NML_TIME = "JULES_TIME"
JULES_PARAM_TIMESTEP_LEN = [JULES_NML_TIME, "timestep_len"]
JULES_PARAM_RUN_START = [JULES_NML_TIME, "main_run_start"]
JULES_PARAM_RUN_END = [JULES_NML_TIME, "main_run_end"]

JULES_NML_SPINUP = "JULES_SPINUP"
JULES_PARAM_SPINUP_START = [JULES_NML_SPINUP, "spinup_start"]
JULES_PARAM_SPINUP_END = [JULES_NML_SPINUP, "spinup_end"]
JULES_PARAM_SPINUP_CYCLES = [JULES_NML_SPINUP, "max_spinup_cycles"]
JULES_PARAM_SPINUP_TERMINATE_ON_FAIL = [JULES_NML_SPINUP, "terminate_on_spinup_fail"]
JULES_PARAM_SPINUP_NVARS = [JULES_NML_SPINUP, "nvars"]
JULES_PARAM_SPINUP_VAR = [JULES_NML_SPINUP, "var"]
JULES_PARAM_SPINUP_USE_PERCENT = [JULES_NML_SPINUP, "use_percent"]
JULES_PARAM_SPINUP_TOLERANCE = [JULES_NML_SPINUP, "tolerance"]

JULES_NML_OUTPUT_PROFILE = "JULES_OUTPUT_PROFILE"
JULES_PARAM_OUTPUT_PROFILE_NAME = [JULES_NML_OUTPUT_PROFILE, "profile_name"]
JULES_PARAM_OUTPUT_MAIN_RUN = [JULES_NML_OUTPUT_PROFILE, "output_main_run"]
JULES_PARAM_OUTPUT_PERIOD = [JULES_NML_OUTPUT_PROFILE, "output_period"]
JULES_PARAM_OUTPUT_FILE_PERIOD = [JULES_NML_OUTPUT_PROFILE, "file_period"]
JULES_PARAM_OUTPUT_NVARS = [JULES_NML_OUTPUT_PROFILE, "nvars"]
JULES_PARAM_OUTPUT_VAR = [JULES_NML_OUTPUT_PROFILE, "var"]
JULES_PARAM_OUTPUT_TYPE = [JULES_NML_OUTPUT_PROFILE, "output_type"]
JULES_PARAM_OUTPUT_START = [JULES_NML_OUTPUT_PROFILE, "output_start"]

JULES_NML_OUTPUT = "JULES_OUTPUT"
JULES_PARAM_OUTPUT_NPROFILES = [JULES_NML_OUTPUT, "nprofiles"]
JULES_PARAM_OUTPUT_RUN_ID = [JULES_NML_OUTPUT, "run_id"]
JULES_PARAM_OUTPUT_OUTPUT_DIR = [JULES_NML_OUTPUT, "output_dir"]

JULES_NML_INPUT = "JULES_INPUT_GRID"
JULES_PARAM_INPUT_GRID_IS_1D = [JULES_NML_INPUT, "grid_is_1d"]
JULES_PARAM_INPUT_GRID_DIM_NAME = [JULES_NML_INPUT, "grid_dim_name"]
JULES_PARAM_INPUT_NPOINTS = [JULES_NML_INPUT, "npoints"]
JULES_PARAM_INPUT_TIME_DIM_NAME = [JULES_NML_INPUT, "time_dim_name"]
JULES_PARAM_INPUT_TYPE_DIM_NAME = [JULES_NML_INPUT, "type_dim_name"]
JULES_PARAM_INPUT_SOIL_DIM_NAME = [JULES_NML_INPUT, "soil_dim_name"]
JULES_PARAM_INPUT_PFT_DIM_NAME = [JULES_NML_INPUT, "pft_dim_name"]
JULES_PARAM_INPUT_GRID_NX = [JULES_NML_INPUT, "nx"]
JULES_PARAM_INPUT_GRID_NY = [JULES_NML_INPUT, "ny"]
JULES_PARAM_INPUT_GRID_X_DIM_NAME = [JULES_NML_INPUT, "x_dim_name"]
JULES_PARAM_INPUT_GRID_Y_DIM_NAME = [JULES_NML_INPUT, "y_dim_name"]

JULES_NML_LATLON = "JULES_LATLON"
JULES_PARAM_LATLON_FILE = [JULES_NML_LATLON, "file"]
JULES_PARAM_LATLON_LAT_NAME = [JULES_NML_LATLON, "lat_name"]
JULES_PARAM_LATLON_LON_NAME = [JULES_NML_LATLON, "lon_name"]
JULES_PARAM_LATLON_LATITUDE = [JULES_NML_LATLON, "latitude"]
JULES_PARAM_LATLON_LONGITUDE = [JULES_NML_LATLON, "longitude"]

JULES_NML_LAND_FRAC = "JULES_LAND_FRAC"
JULES_PARAM_LAND_FRAC_FILE = [JULES_NML_LAND_FRAC, "file"]
JULES_PARAM_LAND_FRAC_LAND_FRAC_NAME = [JULES_NML_LAND_FRAC, "land_frac_name"]

JULES_NML_SURF_HGT = "JULES_SURF_HGT"
JULES_PARAM_SURF_HGT_ZERO_HEIGHT = [JULES_NML_SURF_HGT, "zero_height"]

JULES_NML_MODEL_LEVELS = "JULES_MODEL_LEVELS"
JULES_PARAM_NSMAX = [JULES_NML_MODEL_LEVELS, "nsmax"]
JULES_PARAM_MODEL_LEVELS_ICE_INDEX = [JULES_NML_MODEL_LEVELS, "ice"]
JULES_PARAM_MODEL_LEVELS_ICE_INDEX_DEFAULT_VALUE = 9
JULES_PARAM_MODEL_LEVELS_NNVG = [JULES_NML_MODEL_LEVELS, "nnvg"]

JULES_NML_DRIVE = "JULES_DRIVE"
JULES_PARAM_DRIVE_DATA_START = [JULES_NML_DRIVE, "data_start"]
JULES_PARAM_DRIVE_DATA_END = [JULES_NML_DRIVE, "data_end"]
JULES_PARAM_DRIVE_DATA_PERIOD = [JULES_NML_DRIVE, "data_period"]
JULES_PARAM_DRIVE_FILE = [JULES_NML_DRIVE, "file"]
JULES_PARAM_DRIVE_NVARS = [JULES_NML_DRIVE, "nvars"]
JULES_PARAM_DRIVE_VAR = [JULES_NML_DRIVE, "var", True]
JULES_PARAM_DRIVE_VAR_NAME = [JULES_NML_DRIVE, "var_name", True]
JULES_PARAM_DRIVE_TPL_NAME = [JULES_NML_DRIVE, "tpl_name", True]
JULES_PARAM_DRIVE_INTERP = [JULES_NML_DRIVE, "interp", True]
JULES_PARAM_DRIVE_Z1_UV_IN = [JULES_NML_DRIVE, "z1_uv_in"]
JULES_PARAM_DRIVE_Z1_TQ_IN = [JULES_NML_DRIVE, "z1_tq_in"]

JULES_PARAM_DRIVE_L_DAILY_DISAGG = [JULES_NML_DRIVE, "l_daily_disagg"]
JULES_PARAM_DRIVE_L_DISAGG_RH = [JULES_NML_DRIVE, "l_disagg_rh"]
JULES_PARAM_DRIVE_PRECIP_DISAGG_METHOD = [JULES_NML_DRIVE, "precip_disagg_method"]
JULES_PARAM_DRIVE_DIFF_FRAC_CONST = [JULES_NML_DRIVE, "diff_frac_const"]
JULES_PARAM_DRIVE_T_FOR_SNOW = [JULES_NML_DRIVE, "t_for_snow"]
JULES_PARAM_DRIVE_T_FOR_CON_RAIN = [JULES_NML_DRIVE, "t_for_con_rain"]
JULES_PARAM_DRIVE_DUR_CONV_RAIN = [JULES_NML_DRIVE, "dur_conv_rain"]
JULES_PARAM_DRIVE_DUR_LS_RAIN = [JULES_NML_DRIVE, "dur_ls_rain"]
JULES_PARAM_DRIVE_DUR_LS_SNOW = [JULES_NML_DRIVE, "dur_ls_snow"]

#ancils namelist file
JULES_NML_FRAC = "JULES_FRAC"
JULES_PARAM_FRAC_FILE = [JULES_NML_FRAC, "file"]
JULES_PARAM_FRAC_NAME = [JULES_NML_FRAC, "frac_name"]

JULES_NML_SOIL_PRARAM = "JULES_SOIL_PARAM"
JULES_PARAM_SOIL_PARAM_ZSMC = [JULES_NML_SOIL_PRARAM, "zsmc"]
JULES_PARAM_SOIL_PARAM_ZST = [JULES_NML_SOIL_PRARAM, "zst"]
JULES_PARAM_SOIL_PARAM_CONFRAC = [JULES_NML_SOIL_PRARAM, "confrac"]
JULES_PARAM_SOIL_PARAM_DZSOIL_IO = [JULES_NML_SOIL_PRARAM, "dzsoil_io"]

JULES_NML_SOIL_PROPS = "JULES_SOIL_PROPS"
JULES_PARAM_SOIL_PROPS_CONST_Z = [JULES_NML_SOIL_PROPS, "const_z"]
JULES_PARAM_SOIL_PROPS_FILE = [JULES_NML_SOIL_PROPS, "file"]
JULES_PARAM_SOIL_PROPS_NVARS = [JULES_NML_SOIL_PROPS, "nvars"]
JULES_PARAM_SOIL_PROPS_VAR = [JULES_NML_SOIL_PROPS, "var", True]
JULES_PARAM_SOIL_PROPS_VAR_NAME = [JULES_NML_SOIL_PROPS, "var_name", True]
JULES_PARAM_SOIL_PROPS_USE_FILE = [JULES_NML_SOIL_PROPS, "use_file", True]
JULES_PARAM_SOIL_PROPS_CONST_VAL = [JULES_NML_SOIL_PROPS, "const_val", True]

JULES_NML_PDM = "JULES_PDM"
JULES_PARAM_PDM_DZ_PDM = [JULES_NML_PDM, "dz_pdm"]
JULES_PARAM_PDM_B_PDM = [JULES_NML_PDM, "b_pdm"]

JULES_NML_AGRIC = "JULES_AGRIC"
JULES_PARAM_AGRIC_ZERO_AGRIC = [JULES_NML_AGRIC, "zero_agric"]

#initial namelist file
JULES_NML_INITIAL = "JULES_INITIAL"
JULES_PARAM_INITIAL_NVARS = [JULES_NML_INITIAL, "nvars"]
JULES_PARAM_INITIAL_VAR = [JULES_NML_INITIAL, "var"]
JULES_PARAM_INITIAL_USE_FILE = [JULES_NML_INITIAL, "use_file"]
JULES_PARAM_INITIAL_CONST_VAL = [JULES_NML_INITIAL, "const_val"]

JULES_NML_SWITCHES = "JULES_SWITCHES"
JULES_PARAM_SWITCHES_L_POINT_DATA = [JULES_NML_SWITCHES, "l_point_data"]
JULES_PARAM_SWITCHES_L_VG_SOIL = [JULES_NML_SWITCHES, "l_vg_soil"]

JULES_NML_PFTPARM = "JULES_PFTPARM"
#the parameters are not been made into constants but are used in the chess driving data setup

JULES_NML_POST_PROCESSING = "POST_PROCESSING"
JULES_PARAM_POST_PROCESSING_ID = [JULES_NML_POST_PROCESSING, "id"]

DATASET_TYPE_COVERAGE = 'Coverage'
DATASET_TYPE_SINGLE_CELL = 'Single Cell'
DATASET_TYPE_TRANSECT = 'Transect'
DATASET_TYPE_LAND_COVER_FRAC = 'Land Cover Fraction'
DATASET_TYPE_SOIL_PROP = 'Soil Properties File'
MODIFIED_FOR_VISUALISATION_EXTENSION = '_MODIFIED_FOR_VISUALISATION'
