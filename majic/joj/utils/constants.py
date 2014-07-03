"""
header
General constants for the project
"""

# Database table constants
DB_STRING_SIZE = 255  # Default size (chars) to use when creating strings for simple names
DB_LONG_STRING_SIZE = 1000  # Default size (chars) to use when creating descriptions
DB_PARAMETER_VALUE_STRING_SIZE = 1000  # Default size (chars) to use for a Jules name list value
DB_URL_STRING_SIZE = 1000  # Default size (chars) to use when creating urls
DB_PATH_SIZE = 4000  # Default size (chars) to use for a file path

#Username for the core user, The core user will have scientific configurations and model runs
CORE_USERNAME = 'core'

# The default science configuration to use
DEFAULT_SCIENCE_CONFIGURATION = 1

# Model Run status descriptions
MODEL_RUN_STATUS_CREATED = 'Created'
MODEL_RUN_STATUS_SUBMITTED = 'Submitted'
MODEL_RUN_STATUS_PENDING = 'Pending'
MODEL_RUN_STATUS_RUNNING = 'Running'
MODEL_RUN_STATUS_COMPLETED = 'Completed'
MODEL_RUN_STATUS_PUBLISHED = 'Published'
MODEL_RUN_STATUS_FAILED = 'Failed'
MODEL_RUN_STATUS_SUBMIT_FAILED = 'Submission Failed'  # user submited a model but it can not be submitted

# Parameter types
PARAMETER_TYPE_INTEGER = 'integer'  # parameter is an integer (case is from documentation)

# Constants for the names of the dictionary values in the json submitted
JSON_MODEL_RUN_ID = 'model_run_id'
JSON_MODEL_CODE_VERSION = 'code_version'
JSON_MODEL_NAMELISTS = 'namelists'
JSON_MODEL_NAMELIST_FILES = 'namelist_files'
JSON_MODEL_PARAMETERS = 'parameters'
JSON_MODEL_NAMELIST_NAME = 'name'
JSON_MODEL_NAMELIST_GROUP_ID = 'group_id'
JSON_MODEL_NAMELIST_FILE_FILENAME = 'filename'

# Constants for reading netCDF files
NETCDF_LATITUDE = 'Latitude'
NETCDF_LONGITUDE = 'Longitude'
NETCDF_TIME = 'Time'

# Constants for Jules Parameters (so we can easily update if they change name etc)

# Some variables depend on the value of nsmax being > 0 - keep a record of those names here:
DEPENDS_ON_NSMAX = ['snow_ice_gb', 'snow_liq_gb', 'snow_ice_tile', 'snow_liq_tile',
                    'rgrainl', 'snow_ds', 'snow_ice', 'snow_liq', 'tsnow']

JULES_NML_MODEL_GRID = "JULES_MODEL_GRID"
JULES_PARAM_USE_SUBGRID = [JULES_NML_MODEL_GRID, "use_subgrid"]
JULES_PARAM_LATLON_REGION = [JULES_NML_MODEL_GRID, "latlon_region"]
JULES_PARAM_LAT_BOUNDS = [JULES_NML_MODEL_GRID, "lat_bounds"]
JULES_PARAM_LON_BOUNDS = [JULES_NML_MODEL_GRID, "lon_bounds"]

JULES_NML_TIME = "JULES_TIME"
JULES_PARAM_RUN_START = [JULES_NML_TIME, "main_run_start"]
JULES_PARAM_RUN_END = [JULES_NML_TIME, "main_run_end"]

JULES_NML_OUTPUT_PROFILE = "JULES_OUTPUT_PROFILE"
JULES_PARAM_PROFILE_NAME = [JULES_NML_OUTPUT_PROFILE, "profile_name"]
JULES_PARAM_OUTPUT_MAIN_RUN = [JULES_NML_OUTPUT_PROFILE, "output_main_run"]
JULES_PARAM_OUTPUT_PERIOD = [JULES_NML_OUTPUT_PROFILE, "output_period"]
JULES_PARAM_NVARS = [JULES_NML_OUTPUT_PROFILE, "nvars"]
JULES_PARAM_VAR = [JULES_NML_OUTPUT_PROFILE, "var"]
JULES_PARAM_OUTPUT_TYPE = [JULES_NML_OUTPUT_PROFILE, "output_type"]

JULES_NML_OUTPUT = "JULES_OUTPUT"
JULES_PARAM_OUTPUT_NPROFILES = [JULES_NML_OUTPUT, "nprofiles"]

JULES_NML_MODEL_LEVELS = "JULES_MODEL_LEVELS"
JULES_PARAM_NSMAX = [JULES_NML_MODEL_LEVELS, "nsmax"]