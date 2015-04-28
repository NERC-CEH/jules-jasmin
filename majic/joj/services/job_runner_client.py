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
"""
import logging
import json
from dateutil.relativedelta import relativedelta
import requests
import sys
from joj.utils import constants
from joj.services.general import ServiceException
from joj.utils import utils
from joj.services.land_cover_service import LandCoverService
from joj.model import ParameterValue

log = logging.getLogger(__name__)


class JobRunnerClient(object):
    """
    Client to contact the job runner service
    """

    def __init__(self, config, land_cover_service=LandCoverService()):
        self._config = config
        self._land_cover_service = land_cover_service
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
            log.exception("Failed to submit job: %s" % ex.message)
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, "Could not contact job submission server."

        if response.status_code == requests.codes.ok:
            return constants.MODEL_RUN_STATUS_SUBMITTED, "Model run submitted."
        elif response.status_code == requests.codes.bad_request:
            log.exception("Failed to submit job %s" % response.text)
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, "Could not submit model. Error: %s" % \
                   utils.extract_error_message_from_response(response.text)
        else:
            log.exception("Failed to submit job %s" % response.text)
            return constants.MODEL_RUN_STATUS_SUBMIT_FAILED, \
                "Could not submit model because there is an error in the job runner."

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
            raise ServiceException("Failed to get job statuses: %s" % ex.message)

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
        parameters = self.alter_driving_data_start(parameters)
        parameters = self.alter_yearly_monthly_output_profiles(parameters)
        # We need to identify if using fractional file, edited land cover or default .nc file
        # If multicell AND land cover actions saved --> use edited fractional.nc file
        # If multicell AND no land cover actions saved --> leave the .nc file as is
        # If single cell AND user uploaded --> use a fractional.dat file.
        # If single cell AND not user uploaded --> use an edited fractional.nc file
        multicell = utils.get_first_parameter_value_from_parameter_list(
            parameters, constants.JULES_PARAM_LATLON_REGION) or False
        user_uploaded = utils.get_first_parameter_value_from_parameter_list(
            parameters, constants.JULES_PARAM_DRIVE_FILE) == constants.USER_UPLOAD_FILE_NAME

        json_land_cover = {}

        if multicell:
            if land_cover_actions:
                json_land_cover = self._create_json_land_cover_with_land_cover_actions(land_cover_actions, parameters)
        else:
            if user_uploaded:
                json_land_cover = self._create_fractional_file_and_set_parameters(parameters, run_model)
            else:
                json_land_cover = self._create_json_land_cover_with_single_point_edits(parameters, run_model)

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
                constants.JSON_MODEL_NAMELIST_FILES: namelist_files,
                constants.JSON_USER_ID: run_model.user.id,
                constants.JSON_USER_NAME: run_model.user.username,
                constants.JSON_USER_EMAIL: run_model.user.email,
                constants.JSON_LAND_COVER: json_land_cover
            }

    def _create_json_land_cover_with_land_cover_actions(self, land_cover_actions, parameters):
        """
        Create JSON land cover object with land cover actions
        :param land_cover_actions: List of land cover actions to be applied
        :param parameters: List of parameters for model run
        :return: JSON land cover object.
        """
        # Identify the base land cover file, and rename the parameter to be the new file we'll create
        # Identify the name of the base land cover variable
        json_land_cover = self._create_json_land_cover(parameters)

        # Add the ice index
        ice_index_from_parameters = utils.get_first_parameter_value_from_parameter_list(
            parameters,
            constants.JULES_PARAM_MODEL_LEVELS_ICE_INDEX)
        if ice_index_from_parameters is None:
            ice_index_from_parameters = constants.JULES_PARAM_MODEL_LEVELS_ICE_INDEX_DEFAULT_VALUE
        json_land_cover[constants.JSON_LAND_COVER_ICE_INDEX] = ice_index_from_parameters

        # Add the land cover actions
        json_actions = []
        for action in land_cover_actions:
            json_action = {constants.JSON_LAND_COVER_MASK_FILE: action.region.mask_file,
                           constants.JSON_LAND_COVER_VALUE: action.value_id,
                           constants.JSON_LAND_COVER_ORDER: action.order}
            json_actions.append(json_action)
        json_land_cover[constants.JSON_LAND_COVER_ACTIONS] = json_actions
        json_land_cover[constants.JSON_LAND_COVER_POINT_EDIT] = {}
        return json_land_cover

    def _create_fractional_file_and_set_parameters(self, parameters, run_model):
        """
        Create a land cover fractional ASCII file on the job runner and set the appropriate parameter
        in the parameter list
        :param parameters: List of parameters for model run
        :param run_model: Model run
        :return: JSON land cover object (empty)
        """
        # Save the fractional file
        self.start_new_file(run_model.id, constants.FRACTIONAL_FILENAME)
        self.append_to_file(run_model.id, constants.FRACTIONAL_FILENAME, run_model.land_cover_frac)
        self.close_file(run_model.id, constants.FRACTIONAL_FILENAME)
        utils.set_parameter_value_in_parameter_list(
            parameters, constants.JULES_PARAM_FRAC_FILE, constants.FRACTIONAL_FILENAME)
        return {}

    def _create_json_land_cover_with_single_point_edits(self, parameters, run_model):
        """
        Create a JSON land cover object for single point land cover edits
        :param parameters: List of parameters
        :param run_model: Model run
        :return: JSON land cover object
        """
        json_land_cover = self._create_json_land_cover(parameters)

        lat, lon = utils.get_first_parameter_value_from_parameter_list(
            parameters, constants.JULES_PARAM_POINTS_FILE, is_list=True)
        vals = [float(val) for val in run_model.land_cover_frac.split()]
        land_cover_point_edit = {constants.JSON_LAND_COVER_LAT: lat,
                                 constants.JSON_LAND_COVER_LON: lon,
                                 constants.JSON_LAND_COVER_FRACTIONAL_VALS: vals}
        json_land_cover[constants.JSON_LAND_COVER_POINT_EDIT] = land_cover_point_edit
        return json_land_cover

    def _create_json_land_cover(self, parameters):
        """
        Create a JSON land cover object with the land cover base filename, variable key and empty
        actions and single point edits
        :param parameters: Parameters for model run
        :return: JSON land cover object
        """
        json_land_cover = {}

        fractional_base_filename = utils.get_first_parameter_value_from_parameter_list(
            parameters, constants.JULES_PARAM_FRAC_FILE)
        utils.set_parameter_value_in_parameter_list(
            parameters, constants.JULES_PARAM_FRAC_FILE, constants.USER_EDITED_FRACTIONAL_FILENAME)
        fractional_base_variable_key = utils.get_first_parameter_value_from_parameter_list(
            parameters, constants.JULES_PARAM_FRAC_NAME)

        # Create the land cover JSON object
        json_land_cover[constants.JSON_LAND_COVER_BASE_FILE] = fractional_base_filename
        json_land_cover[constants.JSON_LAND_COVER_BASE_KEY] = fractional_base_variable_key
        json_land_cover[constants.JSON_LAND_COVER_ACTIONS] = []
        json_land_cover[constants.JSON_LAND_COVER_POINT_EDIT] = {}
        return json_land_cover

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
        if 'run_in_test_mode' in self._config and self._config['run_in_test_mode'].lower() == 'true':
            return
        self._file_lines_store = ''
        data = {constants.JSON_MODEL_RUN_ID: model_run_id,
                constants.JSON_MODEL_FILENAME: filename}
        try:
            url = self._config['job_runner_url'] + 'job_file/new'
            response = self._post_securely(url, data)

        except Exception:
            log.exception("Job Runner client failed to open file")
            raise ServiceException("Error storing file on job runner.")

        self._interpret_status_code(
            response,
            "Job Runner client failed to open file",
            "Error storing file on job runner:",
            "Error storing file on job runner.")

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
        if 'run_in_test_mode' in self._config and self._config['run_in_test_mode'].lower() == 'true':
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
            except Exception:
                log.exception("Job Runner client failed to append to a file")
                raise ServiceException("Error storing file on job runner.")

            self._interpret_status_code(
                response,
                "Job Runner client failed to append to a file",
                "Error storing file on job runner:",
                "Error storing file on job runner.")

    def delete_file(self, model_run_id, filename):
        """
        Delete a file in the model_run directory
        :param model_run_id: Model run ID
        :param filename: Filename to delete
        :return:
        """
        if 'run_in_test_mode' in self._config and self._config['run_in_test_mode'].lower() == 'true':
            return
        data = {constants.JSON_MODEL_RUN_ID: model_run_id,
                constants.JSON_MODEL_FILENAME: filename}
        try:
            url = self._config['job_runner_url'] + 'job_file/delete'
            response = self._post_securely(url, data=data)

        except Exception:
            log.exception("Job Runner client failed to delete file")
            raise ServiceException("Error storing file on job runner.")

        self._interpret_status_code(
            response,
            "Job Runner client failed to delete file",
            "Error storing file on job runner:",
            "Error storing file on job runner.")

    def close_file(self, model_run_id, filename):
        """
        Close a file that has been appended to. This writes to the file any remaining text that was
        not sent to the job runner in the last text chunk.
        :param model_run_id: Model run ID
        :param filename: Filename to close
        :return:
        """
        if 'run_in_test_mode' in self._config and self._config['run_in_test_mode'].lower() == 'true':
            return
        data = {constants.JSON_MODEL_RUN_ID: model_run_id,
                constants.JSON_MODEL_FILENAME: filename,
                constants.JSON_MODEL_FILE_LINE: self._file_lines_store}
        try:
            url = self._config['job_runner_url'] + 'job_file/append'
            response = self._post_securely(url, data=data)
            self._file_lines_store = ''
        except Exception:
            log.exception("Job Runner client failed to close file")
            raise ServiceException("Error storing file on job runner.")

        self._interpret_status_code(
            response,
            "Job Runner client failed to close file",
            "Error storing file on job runner:",
            "Error storing file on job runner.")

    def duplicate_uploaded_driving_data(self, model_run_to_duplicate_id, new_model_run_id):
        """
        Duplicate the uploaded driving data between model runs
        :param model_run_to_duplicate_id: id of model run to duplicate
        :param new_model_run_id: id of the model run to duplicate to
        :return: nothing
        """
        data = {constants.JSON_MODEL_RUN_ID: new_model_run_id,
                constants.JSON_MODEL_FILENAME: constants.USER_UPLOAD_FILE_NAME,
                constants.JSON_MODEL_RUN_ID_TO_DUPLICATE_FROM: model_run_to_duplicate_id}
        try:
            url = self._config['job_runner_url'] + 'job_file/duplicate'
            response = self._post_securely(url, data=data)
        except Exception:
            log.exception("Job runner client failed to duplicate a file")
            raise ServiceException("Job runner client failed to duplicate a file")

        self._interpret_status_code(
            response,
            "Failed to duplicate file",
            "Job runner failed to duplicate the file. Error:",
            "Job runner failed to duplicate the file.")

    def _interpret_status_code(self,
                               response,
                               log_error_text,
                               service_exception_with_text_prefix,
                               service_exception_with_no_text):
        """
        Interpret the status code and if error raise a service exception
        :param response: response
        :param log_error_text: error text for log file
        :param service_exception_with_text_prefix: exception to which the returned error is appended
        :param service_exception_with_no_text: text for when there is no error
        :return: nothing
        """
        if response.status_code == requests.codes.ok:
            return

        log.error("{}. Response text: {}".format(log_error_text, response.text))
        if response.status_code == requests.codes.bad_request:
            raise ServiceException("{} {}".format(service_exception_with_text_prefix, response.text))

        raise ServiceException(service_exception_with_no_text)

    def alter_driving_data_start(self, parameters):
        """
        Moves the driving data start to be closer to the main run start
        Due to a bug in JULES if the driving data start is too far before the main run start,
        an integer overflows and causes an error. We therefore need to move the driving data
        start close to the model run
        :param parameters: List of parameters
        :return:
        """
        driving_start = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                            constants.JULES_PARAM_DRIVE_DATA_START)
        spinup_start = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                           constants.JULES_PARAM_SPINUP_START)
        time_gap = relativedelta(years=10)
        new_driving_start = max(spinup_start - time_gap, driving_start)
        utils.set_parameter_value_in_parameter_list(
            parameters, constants.JULES_PARAM_DRIVE_DATA_START, new_driving_start)
        return parameters

    def alter_yearly_monthly_output_profiles(self, parameters):
        """
        Adjusts the output profiles to avoid JULES errors like:
        "Jules error:file_ts_open: When using data_period=-1, data must start at 00:00:00 on 1st of month"
        caused by asking for output profiles that aren't valid for the selected run starts and ends
        :param parameters: List of parameters
        :return:
        """
        run_start = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                        constants.JULES_PARAM_RUN_START)
        run_end = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                      constants.JULES_PARAM_RUN_END)

        output_starts_to_add = []

        for parameter in parameters:
            if parameter.namelist.name == constants.JULES_PARAM_OUTPUT_PERIOD[0]:
                if parameter.name == constants.JULES_PARAM_OUTPUT_PERIOD[1]:
                    for pv_output_period in parameter.parameter_values:
                        period = pv_output_period.get_value_as_python()
                        group_id = pv_output_period.group_id
                        if period == constants.JULES_YEARLY_PERIOD:
                            if not utils.is_first_of_year(run_start):
                                next_year = utils.next_first_of_year(run_start)
                                if next_year <= run_end:
                                    output_start = ParameterValue()
                                    output_start.set_value_from_python(next_year)
                                    output_start.group_id = group_id
                                    output_starts_to_add.append(output_start)
                        elif period == constants.JULES_MONTHLY_PERIOD:
                            if not utils.is_first_of_month(run_start):
                                next_month = utils.next_first_of_month(run_start)
                                if next_month <= run_end:
                                    output_start = ParameterValue()
                                    output_start.set_value_from_python(next_month)
                                    output_start.group_id = group_id
                                    output_starts_to_add.append(output_start)

        # Add parameter values (output_start)
        for parameter in parameters:
            if parameter.namelist.name == constants.JULES_PARAM_OUTPUT_START[0]:
                if parameter.name == constants.JULES_PARAM_OUTPUT_START[1]:
                    parameter.parameter_values += output_starts_to_add

        return parameters