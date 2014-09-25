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
import datetime
from hamcrest import *
from joj.model import session_scope, Session, AccountRequest

from joj.tests import *
from joj.services.user import UserService
from joj.utils import constants


class TestAccountRequestController(TestController):

    def setUp(self):
        super(TestAccountRequestController, self).setUp()
        self.clean_database()

    def test_GIVEN_nothing_WHEN_password_THEN_page_with_error(self):

        response = self.app.get(
            url=url(controller='home', action='password')
        )
        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Correct page")

    def test_GIVEN_nothing_WHEN_post_password_THEN_page_with_error(self):

        response = self.app.post(
            url=url(controller='home', action='password'),
            params={}
        )
        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Correct page")

    def test_GIVEN_id_but_no_uuid_WHEN_password_THEN_page_with_error(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)

        response = self.app.get(
            url=url(controller='home', action='password', id=user.id)
        )
        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Correct page")

    def test_GIVEN_id_but_no_uuid_WHEN_post_password_THEN_page_with_error(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)

        response = self.app.post(
            url=url(controller='home', action='password', id=user.id),
            params={}
        )
        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Correct page")

    def test_GIVEN_valid_id_and_uuid_WHEN_password_THEN_page_with_no_error(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)
        user = user_service.get_user_by_username(username)

        response = self.app.get(
            url=url(controller='home', action='password', id=user.id, uuid=user.forgotten_password_uuid)
        )

        assert_that(response.normal_body, contains_string("Password Request"), "Correct page")
        assert_that(response.normal_body, is_not(contains_string("Your new password")), "tooltip is rewriten")
        assert_that(response.normal_body, contains_string('title="Username"'), "Username tooltip")
        assert_that(response.normal_body, contains_string('title="New password"'), "Username tooltip")
        assert_that(response.normal_body, contains_string('title="Retype your new password"'), "Username tooltip")

    def test_GIVEN_valid_id_and_invalid_uuid_WHEN_password_THEN_page_with_error(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)

        response = self.app.get(
            url=url(controller='home', action='password', id=user.id, uuid="not that uuid")
        )

        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Invalid password page")

    def test_GIVEN_valid_id_and_invalid_uuid_WHEN_post_password_THEN_page_with_error(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)

        response = self.app.post(
            url=url(controller='home', action='password', id=user.id),
            params={'uuid':"not that uuid"}
        )

        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Invalid password page")

    def test_GIVEN_invalid_id_and_valid_uuid_WHEN_password_THEN_page_with_error(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)

        response = self.app.get(
            url=url(controller='home', action='password', id=user.id + 1, uuid=user.forgotten_password_uuid)
        )

        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Invalid password page")

    def test_GIVEN_invalid_id_and_valid_uuid_WHEN_post_password_THEN_page_with_error(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)

        response = self.app.post(
            url=url(controller='home', action='password', id=user.id + 1),
            params={'uuid': user.forgotten_password_uuid}
        )

        assert_that(response.normal_body, contains_string("Invalid Password Request"), "Invalid password page")

    def test_GIVEN_valid_id_and_valid_uuid_which_has_expired_WHEN_password_THEN_reset_forgotten_password(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)
        with session_scope() as session:
            user = user_service.get_user_by_id(user.id)
            user.forgotten_password_expiry_date = datetime.datetime.now() - datetime.timedelta(minutes=1)
            session.add(user)
        original_uuid = user.forgotten_password_uuid

        response = self.app.get(
            url=url(controller='home', action='password', id=user.id, uuid=original_uuid)
        )

        assert_that(response.normal_body, contains_string("Expired Password Request"), "Expired password page")
        with session_scope() as session:
            user = user_service.get_user_by_id(user.id)
            assert_that(user.forgotten_password_uuid, is_not(original_uuid), "uuid reset")

    def test_GIVEN_valid_id_and_valid_uuid_which_has_expired_WHEN_post_password_THEN_reset_forgotten_password(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)
        with session_scope() as session:
            user = user_service.get_user_by_id(user.id)
            user.forgotten_password_expiry_date = datetime.datetime.now() - datetime.timedelta(minutes=1)
            session.add(user)
        original_uuid = user.forgotten_password_uuid

        response = self.app.post(
            url=url(controller='home', action='password', id=user.id),
            params={'uuid':original_uuid}
        )

        assert_that(response.normal_body, contains_string("Expired Password Request"), "Expired password page")
        with session_scope() as session:
            user = user_service.get_user_by_id(user.id)
            assert_that(user.forgotten_password_uuid, is_not(original_uuid), "uuid reset")

    def test_GIVEN_valid_id_and_uuid_WHEN_post_new_password_THEN_login_page_with_message(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)
        user = user_service.get_user_by_username(username)
        new_password = 'long and hard to guess password'

        response = self.app.post(
            url=url(controller='home', action='password', id=user.id),
            params={
                'uuid': user.forgotten_password_uuid,
                'password_one': new_password,
                'password_two': new_password}
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='account', action='login')), "url")
        with session_scope() as session:
            user = user_service.get_user_by_id(user.id)
            assert_that(user.forgotten_password_uuid, is_(None), "uuid blanked")

    def test_GIVEN_valid_id_and_uuid_non_matching_password_WHEN_post_new_password_THEN_error_message(self):
        user_service = UserService()
        username = "unique test name"
        user_service.create(username, "test", "test", "email", constants.USER_ACCESS_LEVEL_EXTERNAL)
        user = user_service.get_user_by_username(username)
        user_service.set_forgot_password(user.id)
        user = user_service.get_user_by_username(username)
        new_password = 'long and hard to guess password'

        response = self.app.post(
            url=url(controller='home', action='password', id=user.id),
            params={
                'uuid': user.forgotten_password_uuid,
                'password_one': new_password,
                'password_two': "not new password"}
        )

        assert_that(response.normal_body, contains_string("passwords are not the same"))
