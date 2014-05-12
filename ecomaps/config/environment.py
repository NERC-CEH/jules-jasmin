"""Pylons environment configuration"""
from formencode.htmlfill import FillingParser
import os

from genshi.template import TemplateLoader
from pylons.configuration import PylonsConfig

import ecomaps.lib.app_globals as app_globals
import ecomaps.lib.helpers
from ecomaps.config.routing import make_map
from ecomaps.model import initialise_session


def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='ecomaps', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = ecomaps.lib.helpers

    config['pylons.app_globals'].genshi_loader = TemplateLoader(
        paths['templates'], auto_reload=True)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    config['pylons.strict_tmpl_context'] = False

    # Setting up SQLAlchemy here
    initialise_session(config)

    # Hackery alert - the htmlfill function of formencode
    # fails when parsing html markup inside a CDATA section
    # which is bad for any JS that adds elements for example
    # Found a workaround here:
    # http://osdir.com/ml/python.formencode/2006-10/msg00019.html
    #
    FillingParser.CDATA_CONTENT_ELEMENTS = ()

    return config
