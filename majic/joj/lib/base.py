"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from formencode.rewritingparser import html_quote
from pylons import cache, config, request, response, session, url
from pylons import tmpl_context as c
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect
from pylons.decorators import jsonify, validate
from pylons.i18n import ungettext, N_
from pylons.templating import render_genshi as render
from paste import httpexceptions
import paste.request
from sqlalchemy.orm.exc import NoResultFound
from joj.crowd.repoze_plugin import is_public_page, is_home_page

from joj.services.user import UserService
from joj.lib import helpers

app_globals = config['pylons.app_globals']


class BaseController(WSGIController):
    _user_service = None
    current_user = None

    def __init__(self, user_service=UserService()):
        """Constructor for the base controller, takes in a user services
            Params:
                user_service: User service to use within the controller
        """
        self._user_service = user_service


    def __call__(self, environ, start_response):
        """Invoke the Controller"""

        # Redirect to a canonical form of the URL if necessary.
        self._redirect_noncanonical_url(environ)

        if not is_public_page(environ):
            self.current_user = self._user_service.get_user_by_username(environ.get('REMOTE_USER'))

            if self.current_user:
                if self.current_user.access_level == "Admin":
                    c.admin_user = True
                else:
                    c.admin_user = False
            else:
            # It's OK to allow access to the home URL with no user logged in because the home controller
            # will sort out what page to show
                if not is_home_page(environ):
                    raise httpexceptions.HTTPUnauthorized()

        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

    def _redirect_noncanonical_url(self, environ):
        """Convert the URL to the form /{controller}/ if the request URL is of
        the form /{controller} and redirect.
        """
        if environ['PATH_INFO'] != '/' and environ['PATH_INFO'].lstrip('/').find('/') < 0:
            environ['PATH_INFO'] += '/'
            url = paste.request.construct_url(environ)
            raise httpexceptions.HTTPMovedPermanently(url)

    @staticmethod
    def error_formatter(error):
        """
        Custom htmlfill error formatter that doesn't add a <br/> (since this causes formatting
        problems on our forms).
        """
        return '<span class="error-message">%s</span>\n' % html_quote(error)

    def get_model_run_being_created_or_redirect(self, model_run_service):
        """
        Check whether there is a model currently being created for the user and, if not,
        redirect to the create model run page
        :param model_run_service: ModelRunService to use
        :return: ModelRun being created if there is one
        """
        try:
            return model_run_service.get_model_being_created_with_non_default_parameter_values(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before you can select a spatial extent")
            redirect(url(controller='model_run', action='create'))

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']


