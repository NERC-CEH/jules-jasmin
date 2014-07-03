"""
#header
"""

import logging

from pylons import request
from pylons.controllers.util import abort
from pylons.decorators import jsonify
from simplejson import JSONDecodeError

from job_runner.lib.base import BaseController
from job_runner.utils.constants import *
from job_runner.services.job_service import JobService, ServiceError
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

    def get_json_abort_on_error(self):
        """
        raise a exception if this is not a post with a json body
        otherwise return the body

        """
        try:
            return request.json_body
        except JSONDecodeError:
            abort(400, "Only valid JSON Posts allowed")

    @jsonify
    def new(self):
        """
        Create a new job submission.
        """

        json = self.get_json_abort_on_error()

        if not JSON_MODEL_CODE_VERSION in json or json[JSON_MODEL_CODE_VERSION] not in VALID_CODE_VERSIONS:
            abort(400, "Invalid code version")

        if not JSON_MODEL_RUN_ID in json or json[JSON_MODEL_RUN_ID] is None:
            abort(400, "Invalid model run id")

        if not isinstance(json[JSON_MODEL_RUN_ID], (int, long)):
            abort(400, "Invalid model run id")

        if not JSON_MODEL_NAMELIST_FILES in json or len(json[JSON_MODEL_NAMELIST_FILES]) == 0:
            abort(400, "Invalid namelist files")

        namelist = []
        for namelist_file in json[JSON_MODEL_NAMELIST_FILES]:
            namelist.append(_validate_namelist_file(namelist_file))

        try:
            return self._job_service.submit(json)
        except ServiceError, ex:
            abort(400, ex.message)

    @jsonify
    def status(self):
        """
        Return the statuses of the jobs requested
        """

        json = self.get_json_abort_on_error()

        queued_jobs_status = self._job_service.queued_jobs_status()
        job_statuses = []
        for jobid in json:
            try:
                jobstatus = JobStatus(int(jobid))
                jobstatus.check(self._job_service, queued_jobs_status)
                job_statuses.append(jobstatus)
            except ValueError:
                abort(400, "Job ids must all be integers")

        return job_statuses
