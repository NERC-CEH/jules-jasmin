"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from genshi.core import Markup
from webhelpers import *
import webhelpers.html.tags as html_tags
from pylons import config, url
from pylons import session
from webhelpers.pylonslib.flash import Flash as _Flash
from joj.utils import constants
from joj.utils import utils as utils


#Flash area for errors
error_flash = _Flash("errors")

# Flash area for success messages
success_flash = _Flash("success")


def jsonParseIfNotEmpty(var):
    if var is not None and var != "":
        return 'JSON.parse("%s")' % var
    else:
        return 'null'


def getOpenLayersImportPath():
    return config.get('openlayers_js_path', config['serverurl'] + '/js/OpenLayers.js')


def display_date(date, format):
    """
    Return the date as a string or none if the date isn't set
    :param date: date
    :param format: format for the date
    :return: formatted date or "" if the date isn't set
    """
    if date is None:
        return ""
    return date.strftime(format)


def wrap_helpers(localdict):
    def helper_wrapper(func):
        def wrapped_helper(*args, **kw):
            if not callable(func(*args, **kw)):
                return Markup(func(*args, **kw))
            else:
                return Markup(func(*args, **kw)())
        wrapped_helper.__name__ = func.__name__
        return wrapped_helper
    for name, func in localdict.iteritems():
        if not callable(func) or not func.__module__.startswith('webhelpers.rails'):
            continue
        localdict[name] = helper_wrapper(func)
wrap_helpers(locals())


def get_progress_bar_class_name(storage_percent_used):
    """
    Get the class to use for a storage allocation bar
    :param storage_percent_used: the percentage of storage used
    """
    if storage_percent_used < constants.QUOTA_WARNING_LIMIT_PERCENT:
        return "success"
    elif storage_percent_used < constants.QUOTA_ABSOLUTE_LIMIT_PERCENT:
        return "warning"
    else:
        return "danger"
