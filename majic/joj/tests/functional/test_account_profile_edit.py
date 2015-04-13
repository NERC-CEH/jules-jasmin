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
from joj.utils import constants
from joj.model import session_scope, Session, User


class TestAccountProfileEdit(TestController):

    def setUp(self):
        super(TestAccountProfileEdit, self).setUp()
        self.clean_database()

    def login_setup_params(self, workbench_username="", original_workbench_username=""):
        self.user = self.login(access_level=constants.USER_ACCESS_LEVEL_CEH, workbench_username=original_workbench_username)
        self.params = {'first_name': "new first name",
                       'last_name': "new last name",
                       'email': "new_email_address@name.new",
                       'workbench_username': workbench_username}

    def test_GIVEN_not_logged_in_WHEN_edit_profile_THEN_redirects(self):
        response = self.app.get(
            url=url(controller='account', action='profile'),
            expect_errors=True
        )
        assert_that(response.status_code, is_(302), "Response is redirect")

    def test_GIVEN_logged_in_WHEN_edit_profile_THEN_edit_page_contains_user_details(self):
        self.user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        response = self.app.get(
            url=url(controller='account', action='profile', id=self.user.id),
            expect_errors=False
        )
        assert_that(response.normal_body, contains_string("Your Profile"))
        self.assert_input_has_correct_label_and_value("first_name", "First name", response, self.user.first_name)
        self.assert_input_has_correct_label_and_value("last_name", "Last name", response, self.user.last_name)
        self.assert_input_has_correct_label_and_value("email", "Email", response, self.user.email)
        self.assert_input_has_correct_label_and_value("workbench_username", "Workbench username", response, self.user.workbench_username)

    def test_GIVEN_logged_in_WHEN_post_edit_profile_THEN_user_details_changed(self):
        self.login_setup_params(workbench_username="workbench_username")

        response = self.app.post(
            url=url(controller='account', action='profile', id=self.user.id),
            params=self.params,
            expect_errors=False
        )

        assert_that(response.status_code, is_(302), "Response is redirect")

        with session_scope() as session:
            user = session.query(User).filter(User.username == self.user.username).one()

        assert_that(user.first_name, is_(self.params['first_name']), "first_name")
        assert_that(user.last_name, is_(self.params['last_name']), "last_name")
        assert_that(user.email, is_(self.params['email']), "email")
        assert_that(user.workbench_username, is_(self.params['workbench_username']), "Workbench username")

    def test_GIVEN_setting_workbench_username_to_empty_WHEN_post_edit_profile_THEN_workbench_username_is_empty(self):
        self.login_setup_params(workbench_username="", original_workbench_username="something")

        response = self.app.post(
            url=url(controller='account', action='profile', id=self.user.id),
            params=self.params,
            expect_errors=False
        )

        assert_that(response.status_code, is_(302), "Response is redirect")

        with session_scope() as session:
            user = session.query(User).filter(User.username == self.user.username).one()

        assert_that(user.workbench_username, none(), "Workbench username")

    def test_GIVEN_errornus_values_WHEN_post_edit_profile_THEN_error(self):
        self.user = self.login(access_level=constants.USER_ACCESS_LEVEL_CEH)
        params = {'first_name': "",
                       'last_name': "new last name",
                       'email': "new_email_addressname.new",
                       'workbench_username': "a" * (constants.DB_STRING_SIZE + 1)}

        response = self.app.post(
            url=url(controller='account', action='profile', id=self.user.id),
            params=params,
            expect_errors=False
        )

        assert_that(response.status_code, is_(200), "Response is redirect")
        assert_that(response.normal_body, contains_string("Enter a value not more than"))
        assert_that(response.normal_body, contains_string("Please enter a value"))
        assert_that(response.normal_body, contains_string("An email address must contain a single @"))