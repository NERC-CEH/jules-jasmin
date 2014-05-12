# Copyright (C) 2007 STFC & NERC (Science and Technology Facilities Council).
# This software may be distributed under the terms of the
# Q Public License, version 1.0 or later.
# http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt
#
"""
 Controller for the 'View' tab - allowing the display of WMC map layers

 @author C Byrom Feb 08, Modified D Lowe, May 09
"""

import logging

from ecomaps.controllers.wmsviz import WmsvizController

log = logging.getLogger(__name__)

class Wmsviz2Controller(WmsvizController):
    
    indexTemplate = "wmsviz2.html"

