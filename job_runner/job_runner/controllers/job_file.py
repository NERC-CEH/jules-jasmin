"""
header
"""
from pylons.controllers.util import abort
from job_runner.lib.base import BaseController
from job_runner.utils import constants
from job_runner.services.job_service import JobService


class JobFileController(BaseController):
    """
    Provides the web app access to write files to the JULES model run directory
    """

    def __init__(self, job_service=JobService()):
        self._job_service = job_service

    def new(self):
        """
        Create a new file with specified file name in the directory for a specified model run ID
        :return:
        """
        try:
            json = self.get_json_abort_on_error()
            filename = json[constants.JSON_MODEL_FILENAME]
            model_run_id = json[constants.JSON_MODEL_RUN_ID]
            self._job_service.create_file(model_run_id, filename)
        except KeyError:
            abort(400, "Missing key: required '%s' and '%s'" % (constants.JSON_MODEL_FILENAME,
                                                                constants.JSON_MODEL_RUN_ID))

    def append(self):
        """
        Add lines of text to an existing file with given filename and model run ID
        :return:
        """
        try:
            json = self.get_json_abort_on_error()
            filename = json[constants.JSON_MODEL_FILENAME]
            model_run_id = json[constants.JSON_MODEL_RUN_ID]
            line = json[constants.JSON_MODEL_FILE_LINE]
            self._job_service.append_to_file(model_run_id, filename, line)
        except KeyError:
            abort(400, "Missing key: required '%s', '%s' and '%s'" % (constants.JSON_MODEL_FILENAME,
                                                                      constants.JSON_MODEL_RUN_ID,
                                                                      constants.JSON_MODEL_FILE_LINE))

    def delete(self):
        """
        Delete a file with specified file name and model run ID
        :return:
        """
        try:
            json = self.get_json_abort_on_error()
            filename = json[constants.JSON_MODEL_FILENAME]
            model_run_id = json[constants.JSON_MODEL_RUN_ID]
            self._job_service.delete_file(model_run_id, filename)
        except KeyError:
            abort(400, "Missing key: required '%s' and '%s'" % (constants.JSON_MODEL_FILENAME,
                                                                constants.JSON_MODEL_RUN_ID))
