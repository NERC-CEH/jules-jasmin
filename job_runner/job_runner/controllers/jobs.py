#header

import logging

from pylons import request
from pylons.controllers.util import abort
from pylons.decorators import jsonify
from simplejson import JSONDecodeError

from job_runner.lib.base import BaseController
from job_runner.utils.constants import *
from services.job_service import JobService, ServiceError

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

        json = {}
        try:
            json = request.json_body
        except JSONDecodeError:
            abort(400, "Only valid JSON Posts allowed")

        if not JSON_MODEL_CODE_VERSION in json or json[JSON_MODEL_CODE_VERSION] not in VALID_CODE_VERSIONS:
            abort(400, "Invalid code version")

        if not JSON_MODEL_RUN_ID in json or json[JSON_MODEL_RUN_ID].strip() == '':
            abort(400, "Invalid model run id")

        if not json[JSON_MODEL_RUN_ID].strip().isdigit():
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
