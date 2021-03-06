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
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun
from joj.model import Session, session_scope, LandCoverRegion, LandCoverRegionCategory, LandCoverAction
from joj.utils import constants
from joj.services.parameter_service import ParameterService


class TestModelRunDuplicateController(TestController):
    def setUp(self):
        super(TestModelRunDuplicateController, self).setUp()
        self.clean_database()

    def test_GIVEN_model_run_WHEN_duplicate_THEN_redirect_to_duplicated_model_run_submit_page(self):

        user = self.login()
        model = self.create_run_model(10, "test", user)

        response = self.app.post(
            url(controller='model_run', action='duplicate', id=model.id))

        assert_that(response.status_code, is_(302), "Response is redirect, page was %s" % response.body)
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='submit')), "url")

    def test_GIVEN_model_run_id_is_not_found_WHEN_duplicate_THEN_redirect_to_model_runs_page(self):

        user = self.login()

        response = self.app.post(
            url(controller='model_run', action='duplicate', id=-100),
            params={"came_from": "index"})

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")

    def test_GIVEN_model_run_id_is_not_a_number_WHEN_duplicate_THEN_redirect_to_model_runs_page(self):

        user = self.login()
        id = 'a'

        response = self.app.post(
            url(controller='model_run', action='duplicate', id=id),
            params={"came_from": "summary"})

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='summary', id=id)), "url")
