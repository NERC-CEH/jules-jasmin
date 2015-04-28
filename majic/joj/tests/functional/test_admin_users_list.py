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
from joj.tests import *
from joj.utils import constants, utils


class TestAdminUsersList(TestController):

    def setUp(self):
        super(TestAdminUsersList, self).setUp()
        self.clean_database()

    def test_GIVEN_not_logged_in_WHEN_list_THEN_redirects(self):
        response = self.app.get(
            url=url(controller='user', action=''),
            expect_errors=True
        )
        assert_that(response.status_code, is_(302), "Response is redirect")

    def test_GIVEN_non_admin_WHEN_list_THEN_returns_error(self):
        self.login()
        response = self.app.get(
            url=url(controller='user', action=''),
            expect_errors=True
        )
        assert_that(response.normal_body, contains_string("Not found"))

    def test_GIVEN_admin_WHEN_list_THEN_returns_list(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        response = self.app.get(
            url=url(controller='user', action=''),
            expect_errors=True
        )
        assert_that(response.normal_body, contains_string("Users List"))

    def test_GIVEN_admin_WHEN_list_THEN_returns_users_with_current_storage_usage(self):
        user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        storage = 90000
        name = "test"
        self.create_run_model(storage, name, user)

        response = self.app.get(
            url=url(controller='user', action=''),
            expect_errors=True
        )
        assert_that(response.normal_body, contains_string(str(round(storage/1024.0, 1))))

    def test_GIVEN_multiple_runs_some_published_some_public_WHEN_list_THEN_returns_current_storages_corectly_added_up(self):
            user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

            failed_storage1 = 90000
            self.create_run_model(failed_storage1, "test", user, constants.MODEL_RUN_STATUS_FAILED)
            failed_storage2 = 30000
            self.create_run_model(failed_storage2, "tes2", user, constants.MODEL_RUN_STATUS_UNKNOWN)

            pub_storage1 = 80000
            self.create_run_model(pub_storage1, "test3", user, constants.MODEL_RUN_STATUS_PUBLISHED)
            pub_storage2 = 100000
            self.create_run_model(pub_storage2, "test4", user, constants.MODEL_RUN_STATUS_PUBLISHED)
            pub_storage3 = 110000
            self.create_run_model(pub_storage3, "test5", user, constants.MODEL_RUN_STATUS_PUBLIC)

            response = self.app.get(
                url=url(controller='user', action=''),
                expect_errors=True
            )
            assert_that(response.normal_body, contains_string(str(utils.convert_mb_to_gb_and_round(failed_storage1 + failed_storage2))))
            assert_that(response.normal_body, contains_string(str(utils.convert_mb_to_gb_and_round(pub_storage1 + pub_storage2 + pub_storage3))))
            assert_that(response.normal_body, contains_string(str(utils.convert_mb_to_gb_and_round((pub_storage1 + pub_storage2 + pub_storage3 + failed_storage1 + failed_storage2)))))

    def test_GIVEN_null_storage_WHEN_list_THEN_returns_current_storages_corectly_added_up(self):
            user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

            self.create_run_model(None, "test1", user, constants.MODEL_RUN_STATUS_PUBLISHED)

            response = self.app.get(
                url=url(controller='user', action=''),
                expect_errors=True
            )
            assert_that(response.normal_body, contains_string(str(utils.convert_mb_to_gb_and_round(0))))
