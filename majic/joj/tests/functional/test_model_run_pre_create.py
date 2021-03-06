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
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from joj.services.model_run_service import ModelRunService
from joj.utils import constants
from joj.model import session_scope, Session, User
from joj.services.user import UserService


class TestModelRunControllerPreCreate(TestController):

    def setUp(self):
        super(TestModelRunControllerPreCreate, self).setUp()
        self.clean_database()

    def test_GIVEN_nothing_WHEN_navigate_to_create_or_redirect_THEN_create_run_page_shown(self):

        self.login()

        response = self.app.get(
            url(controller='model_run', action='pre_create'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_user_over_quota_WHEN_navigate_to_precreate_THEN_index_shown(self):

        user = self.login()
        self.create_run_model(storage_in_mb=user.storage_quota_in_gb * 1024 + 1, name="big_run", user=user)

        response = self.app.get(
            url(controller='model_run', action='pre_create'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")

    def test_GIVEN_model_created_and_user_not_seen_page_WHEN_navigate_to_create_or_redirect_THEN_create_run_page_shown(self):

        user = self.login()
        self.create_run_model(storage_in_mb=0, name="big_run", user=user, status=constants.MODEL_RUN_STATUS_CREATED)

        response = self.app.get(
            url(controller='model_run', action='pre_create'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_model_created_and_user_action_set_WHEN_navigate_to_create_or_redirect_THEN_user_action_page_shown(self):

        user = self.login()
        user_service = UserService()
        user_service.set_current_model_run_creation_action(user, "driving_data")
        self.create_run_model(storage_in_mb=0, name="big_run", user=user, status=constants.MODEL_RUN_STATUS_CREATED)

        response = self.app.get(
            url(controller='model_run', action='pre_create'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='driving_data')), "url")

    def test_GIVEN_no_model_created_and_user_action_set_WHEN_navigate_to_create_or_redirect_THEN_create_page_shown(self):

        user = self.login()
        user_service = UserService()
        user_service.set_current_model_run_creation_action(user, "driving_data")

        response = self.app.get(
            url(controller='model_run', action='pre_create'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")
