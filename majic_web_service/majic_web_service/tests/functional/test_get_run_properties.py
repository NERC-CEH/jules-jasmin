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
from majic_web_service.utils.constants import JSON_MODEL_RUNS, MODEL_RUN_STATUS_COMPLETED, MODEL_RUN_STATUS_PUBLISHED, \
    MODEL_RUN_STATUS_PUBLIC
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
            False,
            False)

    def test_GIVEN_database_has_different_workbench_username_from_username_WHEN_request_run_properties_THEN_workbench_username_returned(self):
        workbench_username = "workbench"
        majic_username = "majic"
        last_status_change = datetime(2015, 5, 3, 2, 1)
        status = MODEL_RUN_STATUS_COMPLETED
        model_id = self.add_model_run(workbench_username, last_status_change, status, majic_username=majic_username)

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
            workbench_username,
            False,
            False)

    def test_GIVEN_workbench_username_is_none_WHEN_request_run_properties_THEN_workbench_username_none_returned(self):
        username = "username"
        workbench_username = None
        last_status_change = datetime(2015, 5, 3, 2, 1)
        status = MODEL_RUN_STATUS_COMPLETED
        model_id = self.add_model_run(workbench_username, last_status_change, status, majic_username=username)

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
            workbench_username,
            False,
            False)

    def test_GIVEN_database_has_more_than_one_row_WHEN_request_run_properties_THEN_return_list_with_all_items_in(self):
        usernames = ["username", "username2", "username3"]
        last_status_changes = [datetime(2015, 5, 3, 2, 1), datetime(2014, 6, 4, 3, 2), datetime(2013, 6, 4, 3, 20)]
        statuses = [MODEL_RUN_STATUS_COMPLETED, MODEL_RUN_STATUS_PUBLISHED, MODEL_RUN_STATUS_PUBLIC]
        expected_is_published = [False, True, True]
        expected_is_public = [False, False, True]
        model_ids = []

        for username, last_status_change, status in zip(usernames, last_status_changes, statuses):
            model_id = self.add_model_run(username, last_status_change, status)
            model_ids.append(model_id)

        response = self.app.get(
            url(controller='run_property', action='list'),
            expect_errors=False
        )

        assert_that(response.status_code, is_(200))
        response = response.json_body
        assert_that(response[JSON_MODEL_RUNS], has_length(3), "model run count")
        self.assert_model_run_json_is(
            response[JSON_MODEL_RUNS][0],
            model_ids[2],
            last_status_changes[2],
            usernames[2],
            expected_is_published[2],
            expected_is_public[2])
        self.assert_model_run_json_is(
            response[JSON_MODEL_RUNS][1],
            model_ids[1],
            last_status_changes[1],
            usernames[1],
            expected_is_published[1],
            expected_is_public[1])
        self.assert_model_run_json_is(
            response[JSON_MODEL_RUNS][2],
            model_ids[0],
            last_status_changes[0],
            usernames[0],
            expected_is_published[0],
            expected_is_public[0])
