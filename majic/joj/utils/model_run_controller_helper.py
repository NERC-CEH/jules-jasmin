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
from pylons import url
from joj.lib.base import redirect
from joj.lib import helpers
from joj.utils import constants, utils


class ModelRunControllerHelper(object):
    """
    Helper for general functions in the model run controller
    """

    def __init__(self, model_run_service):
        """
        Create a model run controller helper
        :param model_run_service: the model run service
        :return:nothing
        """
        self._model_run_service = model_run_service

    def check_user_quota(self, current_user):
        """
        Check that the user can create a new model run
        :param current_user: the current user
        :return: the model run being created
        """
        total = 0
        for user_id, status_name, storage_in_mb in self._model_run_service.get_storage_used(current_user):
            if status_name != constants.MODEL_RUN_STATUS_PUBLISHED:
                total += storage_in_mb

        total_in_gb = utils.convert_mb_to_gb_and_round(total)

        storage_percent_used = round(total_in_gb / current_user.storage_quota_in_gb * 100.0, 0)

        if storage_percent_used >= constants.QUOTA_ABSOLUTE_LIMIT_PERCENT:
            helpers.error_flash(constants.ERROR_MESSAGE_QUOTA_EXCEEDED)
            redirect(url(controller="model_run", action="index"))
