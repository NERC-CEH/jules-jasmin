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

    def _get_json_abort_on_error(self):
        """
        raise a exception if this is not a post with a json body
        otherwise return the body

        """
        try:
            return request.json_body
        except JSONDecodeError:
            abort(400, "Only valid JSON Posts allowed")

    def _check_field_exists_in_json(self, field_name_description, json, json_field_name, is_int=False):
        """
        Check that an entry in the json dictionary exists and is not none. If it is an int check it is an int
        :param field_name_description: the field description for the error message
        :param json: the json to check
        :param json_field_name: the field name to look for
        :param is_int: True if validate it is an integer
        :return: nothing throw abort if validation fails
        """
        if not json_field_name in json or json[json_field_name] is None:
            abort(400, "Invalid %s" % field_name_description)

        if is_int and not isinstance(json[json_field_name], (int, long)):
            abort(400, "Invalid %s, not a number" % field_name_description)