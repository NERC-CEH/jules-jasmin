"""
# Header
"""
import logging
import json
import requests
import sys
from joj.utils import constants
from joj.services.general import ServiceException

log = logging.getLogger(__name__)


class JobRunnerClient(object):
    """
    Client to contact the job runner service
    """

    def __init__(self, config):
        self._config = config
        self._file_lines_store = ''  # Store line text until it reaches the chunk size

    def submit(self, model, parameters, land_cover_actions):
        """
        Submit the model to the job_runner service
        :param model: the run model including parameters
        :param parameters: List of parameters to submit
        :param land_cover_actions: List of land cover actions to apply
        :return: status the model run is in and a message
        """
        data = self.convert_model_to_dictionary(model, parameters, land_cover_actions)
        try:
            url = self._config['job_runner_url'] + 'jobs/new'
            response = self._post_securely(url, data)
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
            response = self._post_securely(url, model_ids)

        except Exception, ex:
            raise ServiceException("Failed to get job statuses %s" % ex.message)

        if response.status_code == 200:
            return response.json()
        else:
            raise ServiceException("Job status call returned with non ok status code. Status code {} content {}"
                                   .format(str(response.status_code), response.text))

    def delete(self, model_run):
        """
        Delete the run model directory
        :param model_run: the model run to delete
        :return: nothing throws a service exception if there is a problem
        """
        try:
            url = self._config['job_runner_url'] + 'jobs/delete'
            response = self._post_securely(url, {constants.JSON_MODEL_RUN_ID: model_run.id})

        except Exception:
            log.exception("Job runner service error on delete")
            raise ServiceException("The job runner service is not responding")

        if response.status_code == 200:
            return
        else:
            raise ServiceException(response.text)

    def convert_model_to_dictionary(self, run_model, parameters, land_cover_actions):
        """
        Convert the run model from the database object to a dictionary that can be sent to the job runner service
        :param run_model: the run model
        :param parameters: Model run parameters
        :param land_cover_actions:
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

        json_actions = []
        for action in land_cover_actions:
            json_action = {constants.JSON_LAND_COVER_MASK_FILE: action.region.mask_file,
                           constants.JSON_LAND_COVER_VALUE: action.value_id,
                           constants.JSON_LAND_COVER_ORDER: action.order}
            json_actions.append(json_action)

        return \
            {
                constants.JSON_MODEL_RUN_ID: run_model.id,
                constants.JSON_MODEL_CODE_VERSION: run_model.code_version.name,
                constants.JSON_MODEL_NAMELIST_FILES: namelist_files,
                constants.JSON_USER_ID: run_model.user.id,
                constants.JSON_USER_NAME: run_model.user.username,
                constants.JSON_USER_EMAIL: run_model.user.email,
                constants.JSON_LAND_COVER_ACTIONS: json_actions
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

    def _post_securely(self, url, data):
        """
        Use the ssl certificates to post some data
        :param url: the url to post to
        :param data: the data to post
        :return: the response
        """
        verify = True
        if self._config and 'job_runner_certificate' in self._config:
            verify = self._config['job_runner_certificate']
        cert = None
        if self._config and 'majic_certificate_path' in self._config:
            cert = (self._config['majic_certificate_path'], self._config['majic_certificate_key_path'])

        return requests.post(url=url, data=json.dumps(data), verify=verify, cert=cert)

    def start_new_file(self, model_run_id, filename):
        """
        Create a new file in the model run directory
        :param model_run_id: Model run ID
        :param filename: Filename to create
        :return:
        """
        if self._config['job_runner_mode'] == 'test':
            return
        self._file_lines_store = ''
        data = {constants.JSON_MODEL_RUN_ID: model_run_id,
                constants.JSON_MODEL_FILENAME: filename}
        try:
            url = self._config['job_runner_url'] + 'job_file/new'
            response = self._post_securely(url, data)
            if not response.status_code == 200:
                raise ServiceException(response.text)
        except Exception, ex:
            log.error("Job Runner client failed to open file: %s" % ex.message)
            raise ServiceException("Error storing file on job runner: %s" % ex.message)

    def append_to_file(self, model_run_id, filename, line):
        """
        Append a line of text to an existing file in the model run directory. This will save
        text until the size of the stored text is greater than the chunk size defined in the constants
        class and will then send it all to the job runner.
        :param model_run_id: Model run ID
        :param filename: Filename to append to
        :param line: Text to append
        :return:
        """
        if self._config['job_runner_mode'] == 'test':
            return
        self._file_lines_store += line
        if sys.getsizeof(self._file_lines_store, 0) > constants.JOB_RUNNER_CLIENT_FILE_CHUNK_BYTES:

            data = {constants.JSON_MODEL_RUN_ID: model_run_id,
                    constants.JSON_MODEL_FILENAME: filename,
                    constants.JSON_MODEL_FILE_LINE: self._file_lines_store}
            try:
                url = self._config['job_runner_url'] + 'job_file/append'
                response = self._post_securely(url, data=data)
                self._file_lines_store = ''
                if not response.status_code == 200:
                    raise ServiceException(response.text)
            except Exception, ex:
                log.error("Job Runner client failed to append to a file: %s" % ex.message)
                raise ServiceException("Error storing file on job runner: %s" % ex.message)

    def delete_file(self, model_run_id, filename):
        """
        Delete a file in the model_run directory
        :param model_run_id: Model run ID
        :param filename: Filename to delete
        :return:
        """
        if self._config['job_runner_mode'] == 'test':
            return
        data = {constants.JSON_MODEL_RUN_ID: model_run_id,
                constants.JSON_MODEL_FILENAME: filename}
        try:
            url = self._config['job_runner_url'] + 'job_file/delete'
            response = self._post_securely(url, data=data)
            if not response.status_code == 200:
                raise ServiceException(response.text)
        except Exception, ex:
            log.error("Job Runner client failed to delete file: %s" % ex.message)
            raise ServiceException("Error storing file on job runner: %s" % ex.message)

    def close_file(self, model_run_id, filename):
        """
        Close a file that has been appended to. This writes to the file any remaining text that was
        not sent to the job runner in the last text chunk.
        :param model_run_id: Model run ID
        :param filename: Filename to close
        :return:
        """
        if self._config['job_runner_mode'] == 'test':
            return
        data = {constants.JSON_MODEL_RUN_ID: model_run_id,
                constants.JSON_MODEL_FILENAME: filename,
                constants.JSON_MODEL_FILE_LINE: self._file_lines_store}
        try:
            url = self._config['job_runner_url'] + 'job_file/append'
            response = self._post_securely(url, data=data)
            self._file_lines_store = ''
            if not response.status_code == 200:
                raise ServiceException(response.text)
        except Exception, ex:
            log.error("Job Runner client failed to close file: %s" % ex.message)
            raise ServiceException("Error storing file on job runner: %s" % ex.message)