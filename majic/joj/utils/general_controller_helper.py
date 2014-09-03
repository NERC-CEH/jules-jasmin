"""
# header
"""
from decorator import decorator
from pylons import config
from joj.lib.base import render
import logging

log = logging.getLogger(__name__)


@decorator
def must_be_admin(func, self, *args, **kwargs):
    """
    Decorator to add to an action in a controller which means that if
    the user is not an admin the not found page is rendered
    :param func: function that is decorated
    :param args: arguments for the function
    :param kwargs: dictionary for the functions
    :return: rendered html
    """
    access_is_ok = False
    try:
        access_is_ok = self.current_user is not None and self.current_user.is_admin()
    except Exception:
        access_is_ok = False
        log.exception("Exception when accessing a admin only page")

    # call to render page must be outside exception block otherwise redirects do not work
    if access_is_ok:
        return func(self, *args, **kwargs)

    return render('not_found.html')


def put_errors_in_table_on_line(errors, error_key, field_name):
    """
    Make a set of errors which are in one category onto one input
    :param errors: the errors list
    :param error_key: main key for the error, e.g. region which would be a list of region error dictionaries
    :param field_name: name of the field to add the errors too
    """

    region_errors = errors.get(error_key)
    if region_errors is not None:
        for region_error, index in zip(region_errors, range(len(region_errors))):
            if region_error is not None:
                errors["{}-{}.{}".format(error_key, index, field_name)] = "Please correct"
        del errors[error_key]


class InTestDoNothing(object):
    """
    Decorator to indicate that the method should be stubbed in the test scenario
    """
    def __init__(self, func):
        pass

    def __call__(self, func):

        def _skip(init_self, *args, **kwargs):
            pass

        def _call(init_self, *args, **kwargs):
            func(init_self, *args, **kwargs)

        if 'run_in_test_mode' in config:
            if config['run_in_test_mode'].lower() == "true":
                return _skip
        return _call




    # def in_test_return_args(func, *args, **kwargs):
    # """
    #
    # :param func:
    # :param args:
    # :param kwargs:
    # :return:
    # """
    # return