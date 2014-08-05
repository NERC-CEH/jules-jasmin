"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons import request
from pylons.controllers import WSGIController
from pylons.controllers.util import abort
from simplejson import JSONDecodeError


class BaseController(WSGIController):
    """
    Base WSGI controller for webapp
    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

    def get_json_abort_on_error(self):
        """
        raise a exception if this is not a post with a json body
        otherwise return the body

        """
        try:
            return request.json_body
        except JSONDecodeError:
            abort(400, "Only valid JSON Posts allowed")
