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
        log.exception("Exception when accessing a admin only page")
        access_is_ok = False

    if access_is_ok:
        return func(self, *args, **kwargs)

    return render('not_found.html')


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