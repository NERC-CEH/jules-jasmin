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
import urllib2
import urlparse
from cStringIO import StringIO
import xml.sax.saxutils as saxutils

#from ows_server.models import Utilities
from paste.httpexceptions import HTTPNotFound
from paste.request import parse_querystring
import ecomaps.lib.utils as utils

# ecomaps imports
from ecomaps.model import selectedItem
from ecomaps.lib.base import BaseController, response, config, request, c, session, render, abort
from ecomaps.lib.base import app_globals as g
from ecomaps.lib.wmc_util import GetWebMapContext, GetWebMapCapabilities, GetLegend, GetLegendUrl, GetFeatureInfo, openURL, GetResponse, parseEndpointString, getQueryParameter
from ecomaps.lib.build_figure import build_figure
from ecomaps.lib.status_builder import StatusBuilder

from ecomaps.lib.base import request

log = logging.getLogger(__name__)

class WmsvizController(BaseController):
    
    _pilImageFormats = {
        'image/png': 'PNG',
        'image/jpg': 'JPEG',
        'image/jpeg': 'JPEG',
        'image/gif': 'GIF',
        'image/tiff': 'TIFF'
    }
    
    indexTemplate = 'wmsviz.html'
    
    def index(self):
        """
        Default controller method to handle the initial requests to the page
        """
        log.debug('entered wmsviz controller index action')

        return HTTPNotFound
        
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
                log.debug("finished wmsviz controller index action, req = GetWebMapContext")
                return wmc
           
            if self.inputs['REQUEST'] == 'GetWebMapCapabilities':
                wmcDoc = GetWebMapCapabilities(self.inputs['ENDPOINT'])
                
                response.headers['Content-Type'] = 'text/xml'
                log.debug("finished wmsviz controller index action, req = GetWebMapCapabilities")
                return wmcDoc
            
            elif self.inputs['REQUEST'] == 'GetLegend':
                resp = GetLegend(self)
                log.debug("finished wmsviz controller index action, req = GetLegend")
                return resp
            
            elif self.inputs['REQUEST'] == 'GetLegendUrl':
                resp = GetLegendUrl(self)
                log.debug("finished wmsviz controller index action, req = GetLegendUrl")
                return resp
            
            if self.inputs['REQUEST'] == 'GetDisplayOptions':
                
                jsonTxt = GetResponse(self.inputs['URL'])
                
                response.headers['Content-Type'] = 'application/json'
                log.debug("finished wmsviz controller index action, req = GetDisplayOptions")
                return jsonTxt
            
            if self.inputs['REQUEST'] == 'GetAxisConfig':
                
                respText = GetResponse(self.inputs['URL'])
                
                response.headers['Content-Type'] = 'text/xml'
                return respText

            if self.inputs['REQUEST'] == 'proxy':
                # Client is requesting to use server as a proxy. Only forward the request if the
                # request parameter value is for an acceptable request type.
                url = self.inputs['URL']
                requestType = getQueryParameter(url, 'request')
                if requestType.lower() == 'getfeatureinfo':
                    try:
                        info = GetFeatureInfo(url)
                    except Exception, exc:
                        log.info("REQUEST:proxy Error making request to %s: %s" % (self.inputs['URL'], exc.__str__()))
                        info = "<p>Information is not available for this layer or position.</p>"
                    log.debug("finished wmsviz controller index action, req = GetFeatureInfo")
                    return "<FeatureInfo>" + saxutils.escape(info) + "</FeatureInfo>"
                else:
                    log.info("Proxy forwarding refused for request of type %s to URL %s" % (requestType, url))
                    return None

        
        #get server information from config file
        g.server=config['app_conf']['serverurl']
    
        statusBuilder = StatusBuilder()
        
        status = statusBuilder.getCurrentStatus('wmsviz')

        initialSetup = self._buildInitialSetup(self.inputs.get('ENDPOINT'))
        

        session.save()  
        log.info('SAVED SESSION')

        c.initialSetupJSON = utils.toJSON(initialSetup) 
        c.initialStatus = utils.toJSON(status)
        
        
        log.debug("request.params = %s" % (request.params,))
        log.debug("request.headers = %s" % (request.headers,))
        
        log.debug("finished wmsviz controller index action")
        
        return render(self.indexTemplate)

    def _buildInitialSetup(self, endpointParam):
        initialSetup = []
        
        if endpointParam != None:
            
            for ep in self.inputs['ENDPOINT'].split(','):
                endpoint = {}
                o = urlparse.urlparse(ep)
                
                if o.path.find(':') > 0:
                    path = o.path[:o.path.find(':')]

                    url = "%(scheme)s://%(hostname)s%(port)s%(path)s" % {
                        'scheme' : o.scheme if o.scheme != None else '',
                        'hostname' : o.hostname if o.hostname != None else '',
                        'port' : ':' + str(o.port) if o.port != None else '',
                        'path': path,
                    }
                    layers = o.path[o.path.find(':')+1:].split('|')
                    
                    endpoint['layers'] = layers
                else:
                    url = ep
                    layers = ""
                
                endpoint['url'] = url

                initialSetup.append(endpoint)
                
        return initialSetup       

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
        
    def get_figure(self):
        log.debug("running wmsvis.get_figure")
        
        # Use .copy() on params to get a *writeable* MultiDict instance
        params = request.params.copy()
        
        log.debug("params = %s" % (params,))
        
        # The response headers must be strings, not unicode, for modwsgi -
        # ensure that the format is a string, omitting any non-ASCII
        # characters.
        format = params.pop('figFormat', 'image/png')
        formatStr = format.encode('ascii', 'ignore')
        finalImage = build_figure(params)
        
        buffer = StringIO()
        finalImage.save(buffer, self._pilImageFormats[formatStr])
        
        response.headers['Content-Type'] = formatStr

        # Remove headers that prevent browser caching, otherwise IE will not
        # allow the image to be saved in its original format.
        if 'Cache-Control' in response.headers:
            del response.headers['Cache-Control']
        if 'Pragma' in response.headers:
            del response.headers['Pragma']

        return buffer.getvalue()
