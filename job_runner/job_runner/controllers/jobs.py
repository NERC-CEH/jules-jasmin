"""
#header
"""

import logging

from pylons.controllers.util import abort
from pylons.decorators import jsonify

from job_runner.lib.base import BaseController
from job_runner.utils.constants import *
from job_runner.services.job_service import JobService, ServiceException
from job_runner.model.job_status import JobStatus

log = logging.getLogger(__name__)


def _validate_namelist(namelist):
    """
    Validate that the namelist has a name and that the parameters have names
    :param namelist: the name list
    """
    if not JSON_MODEL_NAMELIST_NAME in namelist or namelist[JSON_MODEL_NAMELIST_NAME].strip() == '':
            abort(400, "Invalid name for one of the name lists")

    if not JSON_MODEL_PARAMETERS in namelist:
            abort(400, "namelist has no parameters in")

    for key in namelist[JSON_MODEL_PARAMETERS]:
        if key.strip() == '':
            abort(400, "A parameter name can not be blank")


def _validate_namelist_file(namelist_file):
    """
    Validate that the namelist file has a filename and contains some namelists
    :param namelist_file: the name list file
    """
    if not JSON_MODEL_NAMELIST_FILE_FILENAME in namelist_file \
            or namelist_file[JSON_MODEL_NAMELIST_FILE_FILENAME].strip() == '':
            abort(400, "Invalid filename for one of the namelist files")

    if not JSON_MODEL_NAMELISTS in namelist_file or len(namelist_file[JSON_MODEL_NAMELISTS]) == 0:
            abort(400, "namelist file has no namelists in")

    for namelist in namelist_file[JSON_MODEL_NAMELISTS]:
        _validate_namelist(namelist)


class JobsController(BaseController):
    """
    Controller for jobs
    """

    def __init__(self, job_service=JobService()):
        """
        :param job_service: the job service
        """
        self._job_service = job_service

    @jsonify
    def new(self):
        """
        Create a new job submission.
        """

        json = self._get_json_abort_on_error()

        log.debug("New Model with parameters %s" % json)

        self._check_field_exists_in_json("code version", json, JSON_MODEL_CODE_VERSION)
        if json[JSON_MODEL_CODE_VERSION] not in VALID_CODE_VERSIONS:
            abort(400, "Invalid code version")

        self._check_field_exists_in_json("model run id", json, JSON_MODEL_RUN_ID, is_int=True)
        self._check_field_exists_in_json("user id", json, JSON_USER_ID, is_int=True)
        self._check_field_exists_in_json("user name", json, JSON_USER_NAME)
        self._check_field_exists_in_json("user email address", json, JSON_USER_EMAIL)

        self._check_field_exists_in_json("namelist files", json, JSON_MODEL_NAMELIST_FILES)
        if len(json[JSON_MODEL_NAMELIST_FILES]) == 0:
            abort(400, "Invalid namelist files")

        self._check_field_exists_in_json("land cover", json, JSON_LAND_COVER)

        namelist = []
        for namelist_file in json[JSON_MODEL_NAMELIST_FILES]:
            namelist.append(_validate_namelist_file(namelist_file))

        try:
            return self._job_service.submit(json)
        except ServiceException, ex:
            abort(400, ex.message)

    @jsonify
    def status(self):
        """
        Return the statuses of the jobs requested
        """

        json = self._get_json_abort_on_error()

        log.debug("Status with parameters %s" % json)

        queued_jobs_status = self._job_service.queued_jobs_status()
        job_statuses = []
        for job_id in json:
            try:
                job_status = JobStatus(int(job_id))
                job_status.check(self._job_service, queued_jobs_status)
                job_statuses.append(job_status)
            except ValueError:
                abort(400, "Job ids must all be integers")

        return job_statuses

    @jsonify
    def delete(self):
        """
        Delete a model run directory
        """

        json = self._get_json_abort_on_error()

        log.debug("Delete with parameters %s" % json)

        if JSON_MODEL_RUN_ID not in json:
            abort(400, "Model run id must be included")
        try:
            model_run_id = int(json[JSON_MODEL_RUN_ID])
            self._job_service.delete(model_run_id)
        except ValueError:
            abort(400, "Model run id must be an integer")
        except ServiceException, ex:
            abort(400, ex.message)
        except Exception:
            log.exception("Unknown error when trying to delete model run directory")
            abort(400, "Unknown error when trying to delete model run directory")

    def _check_field_exists_in_json(self, field_name_description, json, json_field_name, is_int=False):
        """
        Check that an entry in the json dictionary exists and is not none. If it is an int check it is an int
        :param field_name_description: the field description for the error message
        :param json: the json to check
        :param json_field_name: the field name to look for
        :param is_int: True if validate it is an integer
        :return: nothing throw abort if validation fails
        """
        if not json_field_name in json or json[json_field_name] is None:
            abort(400, "Invalid %s" % field_name_description)

        if is_int and not isinstance(json[json_field_name], (int, long)):
            abort(400, "Invalid %s, not a number" % field_name_description)
