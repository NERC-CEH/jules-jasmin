"""
Reads and holds the user interface configuration options.

@author rwilkinson
"""
import logging
import ecomaps.lib.config_file_parser as config_file_parser
from ConfigParser import NoOptionError, NoSectionError
from ecomaps.lib.status_builder import StatusBuilder

log = logging.getLogger(__name__)

_customTextOptions = None

def getCustomTextOption(option):
    """Returns the value for one of the custom text options.
    """
    if _customTextOptions == None:
        _loadOptions()

    return _customTextOptions.get(option, None)

def _loadOptions():
    """Reads the relevant options from the user interface configuration file.
    """
    global _customTextOptions
    _customTextOptions = {}
    userInterfaceConfigParser = config_file_parser.UserInterfaceConfigParser()
    _customTextOptions['animationtitle'] = _getOption(userInterfaceConfigParser, 'customtext', 'animationtitle', 'Animation <date>')
    _customTextOptions['figuretitle'] = _getOption(userInterfaceConfigParser, 'customtext', 'figuretitle', 'Figure <date>')
    _customTextOptions['maptitle'] = _getOption(userInterfaceConfigParser, 'customtext', 'maptitle', 'Map')

def _getOption(parser, section, option, default):
    """Retrieves an option value referenced by section and option names, returning a default if the option is not found.
    """
    try:
        value = parser.getConfigOption(section, option)
    except (NoOptionError, NoSectionError):
        value = default
    return value
