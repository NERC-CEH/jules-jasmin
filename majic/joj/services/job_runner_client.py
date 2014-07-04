"""
# Header
"""
import logging
import json
import requests
from pylons import config
from joj.utils import constants
from joj.services.general import DatabaseService

log = logging.getLogger(__name__)


class JobRunnerClient(DatabaseService):
    """
    Client to contact the job runner service
    """

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
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, "Could not contact job submission server."

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
        namelist_files = []

        for parameter in run_model.code_version.parameters:
            namelist_file = self._find_or_create_namelist_file(namelist_files,
                                                               parameter.namelist.namelist_file.filename)
            if constants.JSON_MODEL_NAMELISTS not in namelist_file:
                namelist_file[constants.JSON_MODEL_NAMELISTS] = []
            for parameter_value in parameter.parameter_values:
                namelist = self._find_or_create_namelist(namelist_file[constants.JSON_MODEL_NAMELISTS],
                                                         parameter.namelist.name, parameter_value.group_id)
                if constants.JSON_MODEL_PARAMETERS not in namelist:
                    namelist[constants.JSON_MODEL_PARAMETERS] = {}
                namelist[constants.JSON_MODEL_PARAMETERS][parameter.name] = parameter_value.value

        return \
            {
                constants.JSON_MODEL_RUN_ID: run_model.id,
                constants.JSON_MODEL_CODE_VERSION: run_model.code_version.name,
                constants.JSON_MODEL_NAMELIST_FILES: namelist_files
            }

    def _find_or_create_namelist_file(self, namelist_files, namelist_filename):
        """
        Given a list of JSON model namelist files, finds or creates a namelist file entry
        corresponding to a specified filename.
        :param namelist_files: A list of JSON model namelist files,
        :param namelist_filename: The filename of the namelist file to find or create
        :return: A new or existing namelist_file dictionary
        """
        for namelist_file in namelist_files:
            if namelist_file[constants.JSON_MODEL_NAMELIST_FILE_FILENAME] == namelist_filename:
                return namelist_file
        namelist_file = {constants.JSON_MODEL_NAMELIST_FILE_FILENAME: namelist_filename}
        namelist_files.append(namelist_file)
        return namelist_file

    def _find_or_create_namelist(self, namelists, namelist_name, group_id):
        """
        Given a list of JSON model namelists, finds or creates a namelist entry
        corresponding to a specified name.
        :param namelists: A list of JSON model namelists
        :param namelist_name: The name of the namelist to find or create
        :param group_id: If the same namelist occurs more than once in the file, the group_id indicates which occurrence
        we are using.
        :return: A new or existing namelist dictionary
        """
        for namelist in namelists:
            if namelist[constants.JSON_MODEL_NAMELIST_NAME] == namelist_name \
                    and namelist[constants.JSON_MODEL_NAMELIST_GROUP_ID] == group_id:
                return namelist
        namelist = {constants.JSON_MODEL_NAMELIST_NAME: namelist_name,
                    constants.JSON_MODEL_NAMELIST_GROUP_ID: group_id}
        namelists.append(namelist)
        return namelist
