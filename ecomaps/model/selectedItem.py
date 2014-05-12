# Copyright (C) 2007 STFC & NERC (Science and Technology Facilities Council).
# This software may be distributed under the terms of the
# Q Public License, version 1.0 or later.
# http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt
#
"""
 Simple data class to store basic info on selected items - for use with the selections + view tabs

 @author C Byrom Feb 08
"""

from ecomaps.lib import utilities
import logging

log = logging.getLogger(__name__)
           
class SelectedItem:
    ''' A simple object representing key info on selected items '''
    def __init__(self,entryID,title,kmlURL,wmcURL):
        """
        Constructor to initialise the selected item object
        @param entryID: Entry ID of related DIF record
        @param title: Title of selected item
        @param kmlURL: Endpoint of KML doc relating to selected item, if it exists
        @param wmcURL: WMC Endpoint of selected item, if it exists    
        """
        
        self.entryID = entryID
        self.title = title
        self.kmlURL = kmlURL
        self.wmcURL = wmcURL
        #self.kmlList = utilities.recreateListFromUnicode(kmlURL)
        #self.wmcList = utilities.recreateListFromUnicode(wmcURL)
        if kmlURL:
            self.kmlList = utilities.urlListDecode(kmlURL)
        else:
            self.kmlList = []
        if wmcURL:
            self.wmcList = utilities.urlListDecode(wmcURL)
        else:
            self.wmcList = []


        log.debug('SelectedItem: kmlURL = %s, wmcURL = %s, kmlList = %s, wmcList = %s' %
                  tuple(repr(x) for x in (self.kmlURL, self.wmcURL, self.kmlList, self.wmcList)))
