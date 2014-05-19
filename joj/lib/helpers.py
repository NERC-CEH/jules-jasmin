"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from genshi.core import Markup
from webhelpers import *
import webhelpers.html.tags as html_tags
from pylons import config, url


def jsonParseIfNotEmpty(var):
    if var is not None and var != "":
        return 'JSON.parse("%s")' % var
    else:
        return 'null'
    
def getOpenLayersImportPath():
    return config.get('openlayers_js_path', config['serverurl'] + '/js/OpenLayers.js')


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