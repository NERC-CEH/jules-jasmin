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
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from joj.services.model_run_service import ModelRunService
from joj.utils import constants


class TestModelRunCatalogue(TestController):

    def setUp(self):
        super(TestModelRunCatalogue, self).setUp()
        self.clean_database()

    def test_GIVEN_nothing_WHEN_navigate_to_run_catalogue_THEN_user_storage_allocation_is_shown(self):

        user = self.login()
        model1_storage = 10101
        model2_storage = 6400
        total = 16.1  # 16501/1024l
        percent_used = 16  # 16.1 / 100 (storage for user) rounded
        self.create_run_model(model1_storage, "test", user)
        self.create_run_model(model2_storage, "test2", user)

        response = self.app.get(
            url(controller='model_run', action=''))

        assert_that(response.normal_body, contains_string("Model Runs"))
        assert_that(response.normal_body, contains_string(str(user.storage_quota_in_gb)))
        assert_that(response.normal_body, contains_string(str(total)))
        assert_that(response.normal_body, contains_string(str(percent_used)))
        assert_that(response.normal_body, contains_string("bar-success"))

    def test_GIVEN_when_some_runs_published_and_public_WHEN_navigate_to_run_catalogue_THEN_user_storage_allocation_does_not_include_published_or_public(self):

        user = self.login()
        model1_storage = 10101
        model2_storage = 4300
        model3_storage = 2100

        total = 9.9  # 10101/1024
        percent_used = 10  # 9.9 / 100 (storage for user) rounded
        self.create_run_model(model1_storage, "test", user)
        self.create_run_model(model2_storage, "test2", user, constants.MODEL_RUN_STATUS_PUBLISHED)
        self.create_run_model(model3_storage, "test3", user, constants.MODEL_RUN_STATUS_PUBLIC)

        response = self.app.get(
            url(controller='model_run', action=''))

        assert_that(response.normal_body, contains_string("Model Runs"))
        assert_that(response.normal_body, contains_string(str(user.storage_quota_in_gb)))
        assert_that(response.normal_body, contains_string(str(total)))
        assert_that(response.normal_body, contains_string(str(percent_used)))
        assert_that(response.normal_body, contains_string("bar-success"))

    def test_GIVEN_90_percent_of_space_user_WHEN_navigate_to_run_catalogue_THEN_user_storage_allocation_is_orange(self):

        user = self.login()
        model1_storage = 90000
        name = "test"
        self.create_run_model(model1_storage, name, user)


        response = self.app.get(
            url(controller='model_run', action=''))

        assert_that(response.normal_body, contains_string("bar-warning"))

    def test_GIVEN_110_percent_of_space_user_WHEN_navigate_to_run_catalogue_THEN_user_storage_allocation_is_orange(self):

        user = self.login()
        model1_storage = 110000
        self.create_run_model(model1_storage, "test", user)


        response = self.app.get(
            url(controller='model_run', action=''))

        assert_that(response.normal_body, contains_string("bar-danger"))
