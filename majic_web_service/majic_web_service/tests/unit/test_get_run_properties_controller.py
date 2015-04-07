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
from hamcrest import *
from mock import *
import pylons
from webob.exc import HTTPInternalServerError
import json

from majic_web_service.controllers.run_property import RunPropertyController
from majic_web_service.services.run_property_service import RunPropertyService, ServiceException
from majic_web_service.tests import TestController


class TestGetRunPropertiesController(TestController):

    def setUp(self):
        pylons = Mock()
        pylons.response = Mock()
        pylons.response.headers = {}
        self.runs_properties_service = Mock(RunPropertyService)
        self.runs_properties = RunPropertyController(self.runs_properties_service)
        self.runs_properties._py_object = pylons

    def test_GIVEN_database_is_not_up_WHEN_request_run_properties_THEN_return_fail(self):
        error_message = "Database is not available"
        self.runs_properties_service.list = Mock(side_effect=ServiceException(error_message))

        assert_that(calling(self.runs_properties.list), raises(HTTPInternalServerError, error_message))

    def test_GIVEN_database_is_empty_WHEN_request_run_properties_THEN_return_empty_list(self):
        self.runs_properties_service.list = Mock(return_value=[])

        result = self.runs_properties.list()

        decoded = json.JSONDecoder().decode(result)
        assert_that(decoded, is_({"model_runs": []}))
