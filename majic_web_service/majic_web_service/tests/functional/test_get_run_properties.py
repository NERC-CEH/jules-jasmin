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
from datetime import datetime
from hamcrest import *
from mock import *
from pylons import url, config
from webob.exc import HTTPInternalServerError
import json

from majic_web_service.controllers.run_property import RunPropertyController
from majic_web_service.services.run_property_service import RunPropertyService, ServiceException
from majic_web_service.tests import TestController
from majic_web_service.utils.constants import JSON_MODEL_RUNS, MODEL_RUN_STATUS_COMPLETED
from majic_web_service.utils.general import convert_time_to_standard_string


class TestGetRunProperties(TestController):

    def setUp(self):
        self.clean_database()

    def test_GIVEN_no_runs_WHEN_get_run_properties_THEN_return_empty_list(self):
        response = self.app.get(
            url(controller='run_property', action='list'),
            expect_errors=False
        )

        assert_that(response.status_code, is_(200))
        response = response.json_body
        assert_that(response[JSON_MODEL_RUNS], empty(), "the model runs")

    def test_GIVEN_database_has_one_row_WHEN_request_run_properties_THEN_return_list_with_item_in(self):
        username = "username"
        last_status_change = datetime(2015, 5, 3, 2, 1)
        status = MODEL_RUN_STATUS_COMPLETED
        model_id = self.add_model_run(username, last_status_change, status)

        response = self.app.get(
            url(controller='run_property', action='list'),
            expect_errors=False
        )

        assert_that(response.status_code, is_(200))
        response = response.json_body
        assert_that(response[JSON_MODEL_RUNS], has_length(1), "model run count")
        self.assert_model_run_json_is(
            response[JSON_MODEL_RUNS][0],
            model_id,
            last_status_change,
            username,
            False)
