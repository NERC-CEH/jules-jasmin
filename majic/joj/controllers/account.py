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
import logging
import formencode

from pylons import request, tmpl_context as c, url, config
from pylons.controllers.util import redirect
from pylons.decorators import validate
from webob.exc import HTTPFound
from joj.crowd.client import ClientException

from joj.lib.base import BaseController, render
from repoze.who.api import get_api
from joj.model.loginform import LoginForm
from formencode import htmlfill
from joj.model.schemas.account_profile_edit import AccountProfileEdit
from joj.services.general import ServiceException
from joj.services.user import UserService

log = logging.getLogger(__name__)


class AccountController(BaseController):
    """Encapsulates operations on a user's account"""

    _user_service = None

    def __init__(self, user_service=UserService()):
        """Constructor for the user controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(BaseController, self).__init__()

        self._user_service = user_service

    def login(self):
        """Action for the 'log in' view"""

        identity = request.environ.get('REMOTE_USER')
        came_from = request.params.get('came_from', None)
        message = request.params.get('message', None)

        if identity is not None:
            if came_from:
                redirect(url(str(came_from)))

        return render('login.html', extra_vars={'came_from': came_from, 'message': message})

    def dologin(self):
        """ Handles the log in request"""

        who_api = get_api(request.environ)
        message = ''
        came_from = request.params.get('came_from')

        if not request.POST:
            return redirect(url(controller='account', action='login', came_from=came_from))

        if came_from is u'' or came_from is None:
            came_from = '/home'

        schema = LoginForm()
        c.form_errors = {}

        if request.POST:

            try:
                c.form_result = schema.to_python(request.params)
            except formencode.Invalid, error:
                message = 'Could not log you in as there are missing values'
                c.form_result = error.value
                c.form_errors = error.error_dict or {}
            else:
                c.form_result['login'] = c.form_result['login'].strip()
                try:
                    authenticated, headers = who_api.login(c.form_result)

                    if authenticated:

                        # Who is this user?
                        # If we've got enough info, we should see if they are in
                        # the database already

                        if request.environ['user.username']:

                            user_name = request.environ['user.username']

                            log.debug("Looking for %s in Majic DB" % user_name)

                            try:

                                u = self._user_service.get_user_by_username(request.environ['user.username'])

                                if not u:

                                    log.debug("Couldn't find %s in Majic DB, creating user" % user_name)

                                    self._user_service.create(user_name,
                                                              request.environ['user.first-name'],
                                                              request.environ['user.last-name'],
                                                              request.environ['user.email'],
                                                              None)

                                return HTTPFound(location=came_from, headers=headers)

                            except ServiceException as sx:

                                # Something has gone wrong at a fundamental level, so we can't realistically continue
                                message = 'The Majic database is unavailable, please try again later or alert ' \
                                          'the Majic administrator: %s' % config['email.admin_address']
                                log.exception("Majic database unavailable: %s" % sx)

                    else:
                        # Authentication not successful
                        message = 'Login failed: check your username and/or password.'
                except ClientException:
                    message = 'Login failed: The authentication server is not responding correctly. ' \
                              'Please try again later. If the problem persists please report it to {}.'\
                        .format(config['email.admin_address'])
        else:
            # Forcefully forget any existing credentials.
            _, headers = who_api.login({})

            request.response_headerlist = headers
        if 'REMOTE_USER' in request.environ:
            del request.environ['REMOTE_USER']

        return htmlfill.render(
            render('login.html', extra_vars={'came_from': came_from, 'message': message}),
            defaults=c.form_result,
            errors=c.form_errors,
            auto_error_formatter=_custom_formatter
        )

    def logout(self):
        """Action to log the user out - removing their session"""

        who_api = get_api(request.environ)
        who_api.logout()

        redirect(url(controller='home', action='index'))

    @validate(schema=AccountProfileEdit(), form='profile', post_only=False, on_get=False, prefix_error=False,
              auto_error_formatter=BaseController.error_formatter)
    def profile(self):
        """
        Deal with a logged in users profile
        :return: page to render
        """

        c.user_to_edit = self.current_user
        if request.POST:
            self._user_service.update(
                self.current_user.id,
                self.form_result['first_name'],
                self.form_result['last_name'],
                self.form_result['email'],
                self.form_result['workbench_username']
            )
            return redirect(url(controller='home', action='index'))
        else:
            values = c.user_to_edit.__dict__
            errors = {}

        # render the form if there are errors on Post or if this is a get
        return htmlfill.render(
            render('account/profile.html'),
            defaults=values,
            errors=errors,
            auto_error_formatter=BaseController.error_formatter)


def _custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )
