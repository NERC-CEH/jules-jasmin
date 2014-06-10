# Header
import logging
import json
import requests
from pylons import config
from requests.packages.urllib3.exceptions import ConnectionError
from joj.utils import constants
from joj.services.general import DatabaseService

log = logging.getLogger(__name__)

class JobRunnerClient(DatabaseService):
    def submit(self, model):
        """
        Submit the model to the job_runner service
        :param model: the run model including parameters
        :return: status the model run is in and a message
        """
        data = self.convert_model_to_dictionary(model)
        try:
            url = config['job_runner_url'] + 'jobs/new'
            response = requests.post(url=url, data=json.dumps(data))
                        # auth=('user', 'password'))
        except Exception, ex:
            log.error("Failed to submit job %s" % ex.message)
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, "Could not contact job submission server. Error %s" % ex.message

        if response.status_code == 200:
            return constants.MODEL_RUN_STATUS_PENDING, "Model run submitted."
        else:
            log.error("Failed to submit job %s" % response.text)
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, "Could not submit model. Error %s" % response.text

    def convert_model_to_dictionary(self, run_model):
        """
        Convert the run model from the database object to a dictionary that can be sent to the job runner service
        :param run_model: the run model
        :return: dictionary for the run model
        """
        namelist_files=[]

        for parameter in run_model.code_version.parameters:
            namelist_file = self._find_or_create(namelist_files, parameter.namelist.namelist_file.filename, constants.JSON_MODEL_NAMELIST_FILE_FILENAME)
            if constants.JSON_MODEL_NAMELISTS not in namelist_file:
                namelist_file[constants.JSON_MODEL_NAMELISTS] = []
            namelist = self._find_or_create(namelist_file[constants.JSON_MODEL_NAMELISTS], parameter.namelist.name, constants.JSON_MODEL_NAMELIST_NAME)
            if constants.JSON_MODEL_PARAMETERS not in namelist:
                namelist[constants.JSON_MODEL_PARAMETERS] = {}
            namelist[constants.JSON_MODEL_PARAMETERS][parameter.name] = parameter.parameter_values[0].value

        return \
            {
                constants.JSON_MODEL_RUN_ID: run_model.id,
                constants.JSON_MODEL_CODE_VERSION: run_model.code_version.name,
                constants.JSON_MODEL_NAMELIST_FILES: namelist_files
            }

    def _find_or_create(self, values, value_to_find, property):
        for value in values:
            if value[property] == value_to_find:
                return value
        value = {property: value_to_find}
        values.append(value)
        return value
