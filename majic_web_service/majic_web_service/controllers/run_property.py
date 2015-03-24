"""
#    Majic
#    Copyright (C) 2015  CEH
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
from majic_web_service.lib.base import BaseController
from majic_web_service.services.run_property_service import RunPropertyService, ServiceException
from pylons.controllers.util import abort
from pylons.decorators import jsonify
from majic_web_service.utils.constants import JSON_MODEL_RUNS


class RunPropertyController(BaseController):
    """
    Controller for properties associated with a model run
    """

    def __init__(self, run_property_service=RunPropertyService()):
        """
        Constructor
        :param run_property_service: service to access run properties
        :return: nothing
        """
        super(RunPropertyController, self).__init__()
        self._run_property_service = run_property_service

    @jsonify
    def list(self):
        """
        List all the model runs with their properties
        :return: all model runs and their properties
        """

        try:
            return {JSON_MODEL_RUNS: self._run_property_service.list()}
        except ServiceException as ex:
            abort(500, ex.message)
