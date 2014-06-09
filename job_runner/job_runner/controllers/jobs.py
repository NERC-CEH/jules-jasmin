import logging

from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from simplejson import JSONDecodeError

from job_runner.lib.base import BaseController, render
from job_runner.utils import constants

log = logging.getLogger(__name__)

class JobsController(BaseController):

    @jsonify
    def new(self):

        try:
            json = request.json_body
        except JSONDecodeError:
            return abort(400, "Only valid JSON Posts allowed")

        if not 'code_version' in json or json['code_version'] not in constants.VALID_CODE_VERSIONS:
            return abort(400, "Invalid code version")

        if not 'model_run_id' in json or json['model_run_id'].strip() == '':
            return abort(400, "Invalid model run id")

        if not 'namelist_files' in json or len(json['namelist_files']) == 0:
            return abort(400, "Invalid namelist files")

        return '100'
