#header

import logging

from pylons import request
from pylons.controllers.util import abort
from pylons.decorators import jsonify
from simplejson import JSONDecodeError

from job_runner.lib.base import BaseController
from job_runner.utils import constants

log = logging.getLogger(__name__)


def _validate_namelist(namelist):
    """
    Validate that the namelist has a name and that the parameters have names
    """
    if not 'name' in namelist or namelist['name'].strip() == '':
            abort(400, "Invalid name for one of the name lists")

    if not 'parameters' in namelist:
            abort(400, "namelist has no parameters in")

    for key in namelist['parameters']:
        if key.strip() == '':
            abort(400, "A parameter name can not be blank")


def _validate_namelist_file(namelist_file):
    """
    Validate that the namelist file has a filename and contains some namelists
    """
    if not 'filename' in namelist_file or namelist_file['filename'].strip() == '':
            abort(400, "Invalid filename for one of the namelist files")

    if not 'namelists' in namelist_file or len(namelist_file['namelists']) == 0:
            abort(400, "namelist file has no namelists in")

    for namelist in namelist_file['namelists']:
        _validate_namelist(namelist)

class JobsController(BaseController):
    """
    Controller for jobs
    """

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

        if not 'code_version' in json or json['code_version'] not in constants.VALID_CODE_VERSIONS:
            abort(400, "Invalid code version")

        if not 'model_run_id' in json or json['model_run_id'].strip() == '':
            abort(400, "Invalid model run id")

        if not 'namelist_files' in json or len(json['namelist_files']) == 0:
            abort(400, "Invalid namelist files")

        namelist = []
        for namelist_file in json['namelist_files']:
            namelist.append(_validate_namelist_file(namelist_file))

        return '100'
