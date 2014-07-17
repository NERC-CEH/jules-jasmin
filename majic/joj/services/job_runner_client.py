"""
# Header
"""
import logging
import json
import requests
from joj.utils import constants
from joj.services.general import ServiceException

log = logging.getLogger(__name__)


class JobRunnerClient(object):
    """
    Client to contact the job runner service
    """

    def __init__(self, config):
        self._config = config

    def submit(self, model, parameters):
        """
        Submit the model to the job_runner service
        :param model: the run model including parameters
        :return: status the model run is in and a message
        """
        data = self.convert_model_to_dictionary(model, parameters)
        try:
            url = self._config['job_runner_url'] + 'jobs/new'
            response = requests.post(url=url, data=json.dumps(data))
            # auth=('user', 'password'))
        except Exception, ex:
            log.error("Failed to submit job %s" % ex.message)
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, "Could not contact job submission server."

        if response.status_code == 200:
            return constants.MODEL_RUN_STATUS_SUBMITTED, "Model run submitted."
        else:
            log.error("Failed to submit job %s" % response.text)
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, "Could not submit model. Error %s" % response.text

    def get_run_model_statuses(self, model_ids):
        """
        Get the model statuses for ids passed in
        :param model_ids: list of model run ids
        :return:list of model run dictionaries with ids, status and error message
        """
        try:
            url = self._config['job_runner_url'] + 'jobs/status'
            response = requests.post(url=url, data=json.dumps(model_ids))
            # auth=('user', 'password'))

        except Exception, ex:
            raise ServiceException("Failed to get job statuses %s" % ex.message)

        if response.status_code == 200:
            return response.json()
        else:
            raise ServiceException("Job status call returned with non ok status code. Status code {} content {}"
                                   .format(str(response.status_code), response.text))

    def convert_model_to_dictionary(self, run_model, parameters):
        """
        Convert the run model from the database object to a dictionary that can be sent to the job runner service
        :param run_model: the run model
        :return: dictionary for the run model
        """
        namelist_files = []

        for parameter in parameters:
            namelist_file = self._find_or_create_namelist_file(namelist_files,
                                                               parameter.namelist.namelist_file.filename)
            if len(parameter.parameter_values) == 0:
                self._find_or_create_namelist(
                    namelist_file[constants.JSON_MODEL_NAMELISTS],
                    parameter.namelist.name,
                    parameter.namelist.index_in_file,
                    None)
            else:
                for parameter_value in parameter.parameter_values:
                    namelist = self._find_or_create_namelist(
                        namelist_file[constants.JSON_MODEL_NAMELISTS],
                        parameter.namelist.name,
                        parameter.namelist.index_in_file,
                        parameter_value.group_id)
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
        namelist_file = {constants.JSON_MODEL_NAMELIST_FILE_FILENAME: namelist_filename,
                         constants.JSON_MODEL_NAMELISTS: []}
        namelist_files.append(namelist_file)
        return namelist_file

    def _find_or_create_namelist(self, namelists, namelist_name, namelist_index, group_id):
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
        #check that the name list hasn't been created with not group id
        if group_id is not None:
            for namelist in namelists:
                if namelist[constants.JSON_MODEL_NAMELIST_NAME] == namelist_name \
                   and namelist[constants.JSON_MODEL_NAMELIST_GROUP_ID] is None:
                    namelists.remove(namelist)
                    break

        namelist = {constants.JSON_MODEL_NAMELIST_NAME: namelist_name,
                    constants.JSON_MODEL_NAMELIST_INDEX: namelist_index,
                    constants.JSON_MODEL_NAMELIST_GROUP_ID: group_id,
                    constants.JSON_MODEL_PARAMETERS: {}}
        namelists.append(namelist)
        return namelist
