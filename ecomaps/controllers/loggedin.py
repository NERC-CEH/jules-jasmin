import logging

from ecomaps.lib.base import *
from paste.request import parse_querystring
import urllib2

log = logging.getLogger(__name__)

class LoggedinController(BaseController):
    def index(self):
	#self closes window
        return '<html><head></head><body onload="window.close()"></body></html>'

