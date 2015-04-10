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
import re
from pylons import config

from joj.tests import *
from joj.utils import constants
from joj.model import session_scope, Session, User


class TestAdminUsersEdit(TestController):

    def setUp(self):
        super(TestAdminUsersEdit, self).setUp()
        self.clean_database()

    def login_setup_params(self, storage=10, workbench_username=""):
        self.user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        self.params = {'first_name': self.user.first_name,
                       'last_name': self.user.last_name,
                       'email': self.user.email,
                       'storage_quota': storage,
                       'user_id': self.user.id,
                       'workbench_username': workbench_username}
        if self.user.is_admin():
            self.params['is_admin'] = 'checked'

    def test_GIVEN_not_logged_in_WHEN_edit_THEN_redirects(self):
        response = self.app.get(
            url=url(controller='user', action='edit', id='2'),
            expect_errors=True
        )
        assert_that(response.status_code, is_(302), "Response is redirect")

    def test_GIVEN_non_admin_WHEN_edit_THEN_returns_error(self):
        self.login()
        response = self.app.get(
            url=url(controller='user', action='edit', id='2'),
            expect_errors=True
        )
        assert_that(response.normal_body, contains_string("Not found"))

    def test_GIVEN_admin_and_non_existant_user_WHEN_edit_THEN_returns_error(self):
        self.login()
        response = self.app.get(
            url=url(controller='user', action='edit', id='900000'),
            expect_errors=True
        )
        assert_that(response.normal_body, contains_string("Not found"))

    def test_GIVEN_admin_WHEN_edit_THEN_edit_page(self):
        self.user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        response = self.app.get(
            url=url(controller='user', action='edit', id=self.user.id),
            expect_errors=False
        )
        assert_that(response.normal_body, contains_string("Edit user"))
        assert_that(response.normal_body, contains_string(config['storage_quota_admin_GB']))

    def test_GIVEN_post_storage_quota_WHEN_update_THEN_storage_quota_updated(self):
        expected_storage = 6789
        self.login_setup_params(str(expected_storage))

        response = self.app.post(
            url=url(controller='user', action='edit', id=self.user.id),
            params=self.params,
            expect_errors=False
        )

        with session_scope(Session) as session:
            user = session.query(User).filter(User.id == self.user.id).one()

        assert_that(response.status_code, is_(302), "redirect after successful post")
        assert_that(user.storage_quota_in_gb, is_(expected_storage), "storage")

    def test_GIVEN_post_storage_quota_is_not_a_number_WHEN_update_THEN_storage_quota_updated(self):
        self.login_setup_params('NAN')

        response = self.app.post(
            url=url(controller='user', action='edit', id=self.user.id),
            params=self.params,
            expect_errors=False
        )

        assert_that(response.status_code, is_(200), "no redirect")
        assert_that(response.normal_body, contains_string("integer value"))

    def test_GIVEN_post_storage_quota_is_negative_WHEN_update_THEN_storage_quota_updated(self):
        self.login_setup_params("-19")

        response = self.app.post(
            url=url(controller='user', action='edit', id=self.user.id),
            params=self.params,
            expect_errors=False
        )

        assert_that(response.status_code, is_(200), "no redirect")
        assert_that(response.normal_body, contains_string("greater"))

    def test_GIVEN_editing_user_with_no_workbench_userid_WHEN_edit_THEN_edit_page_contains_empty_workbench_username(self):
        self.user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        response = self.app.get(
            url=url(controller='user', action='edit', id=self.user.id),
            expect_errors=False
        )

        self.assert_input_has_correct_label_and_value("workbench_username", "Workbench username", response, None)

    def test_GIVEN_editing_user_with_a_workbench_userid_WHEN_edit_THEN_edit_page_contains_workbench_username(self):
        workbench_username = "workbench"
        self.user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN, workbench_username=workbench_username)

        response = self.app.get(
            url=url(controller='user', action='edit', id=self.user.id),
            expect_errors=False
        )

        self.assert_input_has_correct_label_and_value("workbench_username", "Workbench username", response, workbench_username)

    def test_GIVEN_post_workbench_username_WHEN_update_THEN_workbench_username_updated(self):
        expected_name = "workbench"
        self.login_setup_params(workbench_username=expected_name)

        response = self.app.post(
            url=url(controller='user', action='edit', id=self.user.id),
            params=self.params,
            expect_errors=False
        )

        with session_scope(Session) as session:
            user = session.query(User).filter(User.id == self.user.id).one()

        assert_that(response.status_code, is_(302), "redirect after successful post")
        assert_that(user.workbench_username, is_(expected_name), "workbench username")