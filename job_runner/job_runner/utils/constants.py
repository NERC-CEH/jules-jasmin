"""
#header
"""

# The code versions and the script used to submit those code versions
VALID_CODE_VERSIONS = {'Jules v3.4.1': 'submit_jules_3_4_1.sh'}

JULES_RUN_COMPLETED_MESSAGE = 'Run completed successfully'

# Constants for the names of the dictionary values in the json submitted
JSON_MODEL_RUN_ID = 'model_run_id'
JSON_MODEL_CODE_VERSION = 'code_version'
JSON_MODEL_NAMELISTS = 'namelists'
JSON_MODEL_NAMELIST_FILES = 'namelist_files'
JSON_MODEL_PARAMETERS = 'parameters'
JSON_MODEL_NAMELIST_NAME = 'name'
JSON_MODEL_NAMELIST_FILE_FILENAME = 'filename'

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