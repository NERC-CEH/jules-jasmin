"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import cache, config, request, response, session
from pylons import tmpl_context as c
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect
from pylons.decorators import jsonify, validate
from pylons.i18n import ungettext, N_
from pylons.templating import render_genshi as render
from paste import httpexceptions
import paste.request

from ecomaps.services.user import UserService

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

        # Before we do anything, is there a "REMOTE USER"?
        # If not, we've not been authenticated!
        if not environ.get('REMOTE_USER') and 'login' not in environ.get('PATH_INFO'):
            raise httpexceptions.HTTPUnauthorized()

        # Redirect to a canonical form of the URL if necessary.
        self._redirect_noncanonical_url(environ)

        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict'

        if 'login' not in environ.get('PATH_INFO'):
            self.current_user = self._user_service.get_user_by_username(environ.get('REMOTE_USER'))

            if not self.current_user:
                raise httpexceptions.HTTPUnauthorized()

            if self.current_user.access_level == "Admin":
                c.admin_user = True
            else:
                c.admin_user = False

        return WSGIController.__call__(self, environ, start_response)

    def _redirect_noncanonical_url(self, environ):
        """Convert the URL to the form /{controller}/ if the request URL is of
        the form /{controller} and redirect.
        """
        if environ['PATH_INFO'] != '/' and environ['PATH_INFO'].lstrip('/').find('/') < 0:
            environ['PATH_INFO'] += '/'
            url = paste.request.construct_url(environ)
            raise httpexceptions.HTTPMovedPermanently(url)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
