"""
#header
"""

# The code versions and the script used to submit those code versions
VALID_CODE_VERSIONS = {'Jules v3.4.1': 'submit_jules_3_4_1.sh'}

# The code versions and the script used to submit those code versions on a single processor
VALID_SINGLE_PROCESSOR_CODE_VERSIONS = {'Jules v3.4.1': 'submit_jules_single_proc_3_4_1.sh'}

# Set the name of the output directory (if changed copy to joj)
OUTPUT_DIR = 'output'
# The list of filenames which the job_file controller API is allowed to create / write to remotely.
WHITELISTED_FILE_NAMES = ["fractional.dat", "user_uploaded_driving_data.dat"]


JULES_RUN_COMPLETED_MESSAGE = 'Run completed successfully'
JULES_FATAL_ERROR_PREFIX = "[FATAL ERROR]"
JULES_POST_PROCESS_ERROR_PREFIX = "[POST PROCESS ERROR]"
JULES_START_TIME_PREFIX = 'Start Time:'
JULES_END_TIME_PREFIX = 'End Time:'
JULES_STORAGE_PREFIX = 'Storage MB:'

# Constants for the names of the dictionary values in the json submitted
JSON_MODEL_RUN_ID = 'model_run_id'
JSON_MODEL_CODE_VERSION = 'code_version'
JSON_MODEL_NAMELISTS = 'namelists'
JSON_MODEL_NAMELIST_FILES = 'namelist_files'
JSON_MODEL_NAMELIST_INDEX = 'index'
JSON_MODEL_PARAMETERS = 'parameters'
JSON_MODEL_NAMELIST_NAME = 'name'
JSON_MODEL_NAMELIST_FILE_FILENAME = 'filename'
JSON_USER_NAME = 'user_name'
JSON_USER_ID = 'user_id'
JSON_USER_EMAIL = 'user_email'
# These are used for transferring files from the web app to the job runner (e.g. user uploaded driving datasets)
JSON_MODEL_FILENAME = 'filename'
JSON_MODEL_FILE_LINE = 'line'

# Model run statuses
MODEL_RUN_STATUS_SUBMITTED = 'Submitted'
MODEL_RUN_STATUS_PENDING = 'Pending'
MODEL_RUN_STATUS_RUNNING = 'Running'
MODEL_RUN_STATUS_COMPLETED = 'Completed'
MODEL_RUN_STATUS_FAILED = 'Failed'
MODEL_RUN_STATUS_SUBMIT_FAILED = 'Submission Failed'  # user submitted a model but it can not be submitted
MODEL_RUN_STATUS_UNKNOWN = 'Unknown'  # Job is in the bjobs list but the status is not understood

# Error messages to pass back for statuses (can be displayed in UI)
ERROR_MESSAGE_NO_FOLDER = 'Model run folder can not be found'
ERROR_MESSAGE_NO_JOB_ID = 'Model run folder contains no job id, model run was not submitted'
ERROR_MESSAGE_NO_LOG_FILE = 'No output from the model run'
ERROR_MESSAGE_OUTPUT_IS_EMPTY = 'Output from the model run is empty'
ERROR_MESSAGE_UNKNOWN_JULES_ERROR = 'Jules did not complete successfully'

#filename for the file containg the bsub id
FILENAME_BSUB_ID = 'bsub_id'
FILENAME_OUTPUT_LOG = 'out.log'
FILENAME_JOBS_RUN_LOG = 'jobs_run.log'

DATA_FORMAT_WITH_TZ = '%Y-%m-%d %H:%m:%S %z'

JULES_NML_MODEL_GRID = "JULES_MODEL_GRID"
JULES_PARAM_POINTS_FILE = [JULES_NML_MODEL_GRID, "points_file"]
JULES_PARAM_LATLON_REGION = [JULES_NML_MODEL_GRID, "latlon_region"]