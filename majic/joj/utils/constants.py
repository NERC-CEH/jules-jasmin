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
JSON_MODEL_NAMELIST_FILE_FILENAME = 'filename'