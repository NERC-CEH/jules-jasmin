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
import datetime
from hamcrest import *
from joj.model import session_scope, Session, AccountRequest

from joj.tests import *
from joj.services.user import UserService
from joj.utils import constants


class TestRedirectOnLogin(TestController):

    def setUp(self):
        super(TestRedirectOnLogin, self).setUp()

    def test_GIVEN_not_logged_in_WHEN_go_to_unknown_page_in_known_controller_THEN_redirect(self):

        pages = [
            ['home', 'unknown'],
            ['home', 'password_'],
            ['home', 'passwor'],
            ['not_a_controller', 'not_an_action'],
            ['model_run', 'index'],
            ['model_run', 'login'],
            ['model_run', 'request_account'],
        ]

        for controller, action in pages:
            response = self.app.get(
                url=url(controller=controller, action=action)
            )

            assert_that(response.status_code, is_(302), "For %s - %s" % (controller, action))

    def test_GIVEN_not_logged_in_WHEN_go_to_known_public_or_home_page_THEN_no_redirect(self):

        pages = [
            ['home', None, None],
            ['/', None, None],
            ['home', 'password', None],
            ['home', 'about', None],
            ['home', 'index', None],
            ['home', 'password', '4'],
            ['account', 'login', None],
            ['request_account', 'license', None],
            ['request_account', 'request', None]
        ]

        for controller, action, id in pages:
            if id:
                theurl = url(controller=controller, action=action, id=id)
            elif action:
                theurl = url(controller=controller, action=action)
            else:
                theurl = url(controller=controller)
            response = self.app.get(url=theurl)

            assert_that(response.status_code, is_(200), "For %s" % theurl)

    def test_GIVEN_not_logged_in_WHEN_post_to_known_public_or_home_page_THEN_no_redirect(self):

        pages = [
            ['account', 'dologin', None],
        ]

        for controller, action, id in pages:
            if id:
                theurl = url(controller=controller, action=action, id=id)
            elif action:
                theurl = url(controller=controller, action=action)
            else:
                theurl = url(controller=controller)
            response = self.app.post(url=theurl)

            assert_that(response.status_code, is_(302), "For %s" % theurl)
