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
from pylons.controllers.util import abort
from job_runner.lib.base import BaseController
from job_runner.utils import constants
from job_runner.services.job_service import JobService
from pylons.decorators import jsonify
from job_runner.services.service_exception import ServiceException

log = logging.getLogger(__name__)


class JobFileController(BaseController):
    """
    Provides the web app access to write files to the JULES model run directory
    """

    def __init__(self, job_service=JobService()):
        self._job_service = job_service

    def _check_whitelist_filename(self, filename):
        """
        Checks to see if a requested filename belongs to an approved list of filenames and aborts if not.
        This ensures files cannot accidentally get overwritten (or something more malicious).
        :param filename: Filename requested
        :return:
        """
        if filename not in constants.WHITELISTED_FILE_NAMES:
            abort(400, "Filename %s is not an authorised file to write to" % filename)

    @jsonify
    def new(self):
        """
        Create a new file with specified file name in the directory for a specified model run ID
        :return:
        """
        try:
            json = self._get_json_abort_on_error()
            filename = json[constants.JSON_MODEL_FILENAME]
            model_run_id = json[constants.JSON_MODEL_RUN_ID]
            self._check_whitelist_filename(filename)
            self._job_service.create_file(model_run_id, filename)
        except KeyError:
            abort(400, "Missing key: required '%s' and '%s'" % (constants.JSON_MODEL_FILENAME,
                                                                constants.JSON_MODEL_RUN_ID))

    @jsonify
    def append(self):
        """
        Add lines of text to an existing file with given filename and model run ID
        :return:
        """
        try:
            json = self._get_json_abort_on_error()
            filename = json[constants.JSON_MODEL_FILENAME]
            model_run_id = json[constants.JSON_MODEL_RUN_ID]
            line = json[constants.JSON_MODEL_FILE_LINE]
            self._check_whitelist_filename(filename)
            self._job_service.append_to_file(model_run_id, filename, line)
        except KeyError:
            abort(400, "Missing key: required '%s', '%s' and '%s'" % (constants.JSON_MODEL_FILENAME,
                                                                      constants.JSON_MODEL_RUN_ID,
                                                                      constants.JSON_MODEL_FILE_LINE))

    @jsonify
    def delete(self):
        """
        Delete a file with specified file name and model run ID
        :return:
        """
        try:
            json = self._get_json_abort_on_error()
            filename = json[constants.JSON_MODEL_FILENAME]
            model_run_id = json[constants.JSON_MODEL_RUN_ID]
            self._check_whitelist_filename(filename)
            self._job_service.delete_file(model_run_id, filename)
        except KeyError:
            abort(400, "Missing key: required '%s' and '%s'" % (constants.JSON_MODEL_FILENAME,
                                                                constants.JSON_MODEL_RUN_ID))

    @jsonify
    def duplicate(self):
        """
        Duplicate a file with specified file name and model run ID to a model run id folder
        :return:
        """
        json = self._get_json_abort_on_error()

        self._check_field_exists_in_json('model run id', json, constants.JSON_MODEL_RUN_ID, is_int=True)
        self._check_field_exists_in_json(
            'model run id to duplicate from',
            json,
            constants.JSON_MODEL_RUN_ID_TO_DUPLICATE_FROM,
            is_int=True)
        self._check_field_exists_in_json('filename', json, constants.JSON_MODEL_FILENAME)
        filename = json[constants.JSON_MODEL_FILENAME]
        self._check_whitelist_filename(filename)

        model_run_id = json[constants.JSON_MODEL_RUN_ID]
        model_run_id_to_duplicate = json[constants.JSON_MODEL_RUN_ID_TO_DUPLICATE_FROM]

        try:
            self._job_service.duplicate_file(model_run_id_to_duplicate, filename, model_run_id)
        except ServiceException, ex:
            abort(400, "Can not duplicate file %s" % ex.message)
        except Exception:
            log.exception("Problem while duplicating file")
            abort(400, "Can not duplicate file, unknown error")