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

    def assert_model_run_json_is(self, model_run_json_dict, model_id, last_status_change, username, is_published):
        """
        assert that the model_run_json_dict has the expected answers
        :param model_run_json_dict: dictionary to check
        :param model_id: model id
        :param last_status_change: last status change
        :param username: the username who owns the model run
        :param is_published: whether model run is published
        :return: nothing
        :raises AssertionError: if the two don't match
        """
        assert_that(model_run_json_dict[JSON_MODEL_RUN_ID], is_(model_id), "model run id")
        assert_that(model_run_json_dict[JSON_USER_NAME], is_(username), "username")
        assert_that(model_run_json_dict[JSON_IS_PUBLISHED], is_(is_published), "the model is not published")
        assert_that(model_run_json_dict[JSON_LAST_STATUS_CHANGE], is_(last_status_change), "last changed")

    def test_GIVEN_database_has_one_row_WHEN_request_run_properties_THEN_return_list_with_item_in(self):
        username = "username"
        last_status_change = datetime(2015, 5, 3, 2, 1)
        status = MODEL_RUN_STATUS_COMPLETED
        model_id = self.add_model_run(username, last_status_change, status)

        result = self.property_service.list()

        assert_that(result, has_length(1), "There should be one item in the model run")
        result_dict = result[0].__json__()
        self.assert_model_run_json_is(result_dict, model_id, last_status_change, username, False)
