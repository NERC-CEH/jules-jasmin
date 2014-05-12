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
from ecomaps.lib.base import app_globals as g
from paste.request import parse_querystring
#from ows_server.models import Utilities
from ecomaps.lib.wmc_util import *
from ecomaps.model import selectedItem
from pylons import config
import copy, logging
log = logging.getLogger(__name__)
import urllib

class OldwmsvizController(BaseController):
    
    def index(self):
        """
        Default controller method to handle the initial requests to the page
        """
        log.debug('wmsviz controller')
        
        g.helpIcon='layout/icons/help.png'  #needs to go in config
        

        self.inputs=dict(parse_querystring(request.environ))
        log.info(self.inputs)
        c.wmcURL = ""
        
        # check if all we're doing is removing a view item
        if 'removeItem' in self.inputs:
            return self.removeViewItem(self.inputs['removeItem'])
        
        # check if we're doing an AJAX callback to get some WMC data
        if 'REQUEST' in self.inputs:
                        
            if self.inputs['REQUEST'] == 'GetWebMapContext':
                wmc= GetWebMapContext(self)
                return wmc
            
            elif self.inputs['REQUEST'] == 'GetLegend':
                return GetLegend(self)

        
        #get server information from config file
        g.server=config['app_conf']['serverurl']
    
        
        #TODO: WORK OUT HOW TO COUPLE THIS TO BROWSE
        # otherwise, we can get here by two routes:
        # i) either by clicking on the WMC icon in the details view - if so, get passed endpoint and add to
        #    selected items;
        # ii) or from the selections tab - which will already have set up the correct selected items
            
        # if ENDPOINT specified, we've reached the page via the WMC icon
                
        if ('ENDPOINT' in self.inputs):
	    #clear out old endpoints NOTE. this means only one endpoint at a time can be viewed. May want to
        #rethink this to enable 'shopping cart' type selection. 
            self.removeAllViewItems()
            urlstring=str(self.inputs['ENDPOINT'])
            req = urllib2.Request(urlstring)
            req.add_header('Cookie', request.headers.get('Cookie', ''))
            try:
	            filehandle = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                if e.code == 401:
                    log.info ('401 unauthorized error in ecomaps')
                    return abort(401) #triggers ndg security framework
                elif e.code == 403:  #TODO: 403 response is UNTESTED.
                    # User is authenticated but doesn't have the required permissions
                    # or an error occurred in the authorization process
                    # Read response
                    response = e.read()
                    # Send response to user
                    self.start_response("%d %s" % (e.code, e.msg), e.headers.dict.items())
                    return response
            self.addViewItem(self.inputs['ENDPOINT'])
        
        # avoid page crashing if we come here without view items defined
#        if 'viewItems' not in session:
#            h.redirect(h.url(controller='discovery'))
#                                        
        session.save()  
        log.info('SAVED SESSION')
        
        # check if page has been visited before; if not display tab
#        if (Utilities.isTabRequired(c.pageTabs, 'View')):
#            c.pageTabs.append(('View', h.url(controller='viewItems',action='index')))

        return render('old_wmsviz.html')


    def addViewItem(self,endpoint):
        """
        Add a selected item to the session
         - if this is the first item, then display the selections tab
         @param endpoint: WMC endpoint 
        """
        
        item = selectedItem.SelectedItem(None, None, None, endpoint)
        
        selections = [item,]
        # avoid duplicates
        if 'viewItems' in session:
            for selection in session['viewItems']:
                if selection.wmcURL != endpoint:
                    selections.append(selection)
                    
        session['viewItems'] = selections
        session.save()  
        
    
    def removeViewItem(self,endpoint):
        """
        Remove view item from session data 
        - NB, do this by rebuilding the session data without the input data included
        @param endpoint: The WMC endpoint of the view item to remove 
        """
        selections = []
        for selection in session['viewItems']:
            if selection.wmcURL != endpoint:
                selections.append(selection)
                
        # if the new list is empty, remove the session variable
        if len(selections) == 0:
            del session['viewItems']
            c.UpdatePageTabs=1
        else:
            session['viewItems'] = selections
        session.save()
        
    def removeAllViewItems(self):
        """
        Remove all old view items - clears out old endpoints 
        """
        session['viewItems']=[]
        session.save()
