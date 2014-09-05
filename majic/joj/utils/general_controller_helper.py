"""
# header
"""
import urllib
import logging
from decorator import decorator
from pylons import config
from joj.lib.base import render, c
from joj.lib.wmc_util import create_request_and_open_url

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


@decorator
def show_error_if_thredds_down(func, self, *args, **kwargs):
    """
    Renders an error page if the THREDDS server cannot be contacted
    :param func: Function that is decorated
    :param args: Arguments for the function
    :param kwargs: Named key word arguments
    :return: Rendered HTML
    """
    try:
        create_request_and_open_url(
            config['thredds.server_url'],
            timeout=int(config['thredds.server_timeout'])).read()
        thredds_up = True
    except:
        thredds_up = False
    if thredds_up:
        return func(self, *args, **kwargs)
    else:
        c.admin_email = config["email.admin_address"]
        page = render("map_down.html")
        return page