# Copyright (C) 2007 STFC & NERC (Science and Technology Facilities Council).
# This software may be distributed under the terms of the
# Q Public License, version 1.0 or later.
# http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt
#
"""
 Controller for the 'View' tab - allowing the display of WMC map layers

 @author C Byrom Feb 08, Modified D Lowe, May 09
"""

from ecomaps.lib.base import *
from paste.request import parse_querystring
#from ows_server.models import Utilities
from ecomaps.lib.wmc_util import *
from ecomaps.model import selectedItem
from pylons import config
import copy, logging
log = logging.getLogger(__name__)
import urllib

class LayertestController(BaseController):
    
    def index(self):
        """
        Default controller method to handle the initial requests to the page
        """
        
        #get server information from config file
        g.server=config['app_conf']['serverurl']
        
        return render('layertest.html')
