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

from majic_web_service.services.run_property_service import RunPropertyService
from majic_web_service.tests import TestController
from majic_web_service.utils.constants import *


class TestGetRunPropertiesController(TestController):

    def setUp(self):
        self.clean_database()
        self.property_service = RunPropertyService()

    def test_GIVEN_database_is_empty_WHEN_request_run_properties_THEN_return_empty_list(self):

        result = self.property_service.list()

        assert_that(result, is_([]))

    def test_GIVEN_database_has_one_row_WHEN_request_run_properties_THEN_return_list_with_item_in(self):
        username = "username"
        last_status_change = datetime(2015, 5, 3, 2, 1)
        status = MODEL_RUN_STATUS_COMPLETED
        model_id = self.add_model_run(username, last_status_change, status)

        result = self.property_service.list()

        assert_that(result, has_length(1), "model run count")
        result_dict = result[0].__json__()
        self.assert_model_run_json_is(result_dict, model_id, last_status_change, username, False)

    def test_GIVEN_database_has_two_rows_one_published_WHEN_request_run_properties_THEN_return_list_with_both_items_in_ordered_by_change_date(self):
        usernames = ["username", "username2"]
        last_status_changes = [datetime(2015, 5, 3, 2, 1), datetime(2014, 6, 4, 3, 2)]
        statuses = [MODEL_RUN_STATUS_COMPLETED, MODEL_RUN_STATUS_PUBLISHED]
        expected_is_published = [False, True]
        model_ids = []
        for username, last_status_change, status in zip(usernames, last_status_changes, statuses):
            model_id = self.add_model_run(username, last_status_change, status)
            model_ids.append(model_id)

        result = self.property_service.list()

        assert_that(result, has_length(2), "model run count")
        self.assert_model_run_json_is(result[0].__json__(), model_ids[1], last_status_changes[1], usernames[1], expected_is_published[1])
        self.assert_model_run_json_is(result[1].__json__(), model_ids[0], last_status_changes[0], usernames[0], expected_is_published[0])

