#header

"""General constants for the project"""
# Database table constants
DB_STRING_SIZE = 255  # Default size (chars) to use when creating strings for simple names
DB_LONG_STRING_SIZE = 1000 # Default size (chars) to use when descriptions
DB_PARAMETER_VALUE_STRING_SIZE = 1000 # Default size (chars) to use for a Jules name list value
DB_URL_STRING_SIZE = 1000  # Default size (chars) to use when creating urls
DB_PATH_SIZE = 4000  # Default size (chars) to use for a file path


MODEL_RUN_STATUS_CREATING = 'Creating' # Status of a model run when a user is creating a model run
MODEL_RUN_STATUS_SUBMIT_FAILED = 'Submission Failed' # Status of a model run when a user submit a model but it can not be submitted

PARAMETER_TYPE_INTEGER = 'integer' # parameter is an integer (case is from documentation)
