# Copyright (C) 2007 STFC & NERC (Science and Technology Facilities Council).
# This software may be distributed under the terms of the
# Q Public License, version 1.0 or later.
# http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt
#
"""

"""

import time
import logging

import paste
from owslib.wcs import WebCoverageService

from ecomaps.lib.base import BaseController, response, config, request, c, render
from ecomaps.lib.base import app_globals as g
from ecomaps.lib.wmc_util import proxyFix, resetProxy, parseEndpointString
from ecomaps.model.date_time_options import DateTimeOptionsBuilder
import ecomaps.lib.utils as utils

from ecomaps.lib.config_file_parser import OutlineLayersConfigParser, EndpointConfigFileParser

import pprint

log = logging.getLogger(__name__)

class WcsdownController(BaseController):
    
    
    def index(self):
        """
        Default controller method to handle the initial requests to the page
        """
        st = time.time()
        params = self._getParams()

        #get the list of default WCS endpoints
        ep = EndpointConfigFileParser()
        endpointList = ep.buildEndpointList('wcsdown')
        wcsEPList = utils.filterEnpointList(endpointList, 'WCS')
        #log.debug("wcsEPList = %s" % (pprint.pformat(wcsEPList),))
        
        c.defaultWCSEndpoints = utils.toJSON(wcsEPList)
        
        log.debug("params = %s" % (params,))
        
        endpoint = params.get('ENDPOINT', None)
        bbox = params.get('BBOX', None)
        c.time = params.get('TIME', None)
        c.time_end = params.get('TIME_END', None)
        layer = params.get('LAYER', None)
        format = params.get('FORMAT', None)
        crs = params.get('CRS', None)
        c.message = params.get('MESSAGE', "")
        c.singleTimePoint = params.get('SINGLE_TIME', "")
        
        layers = []
        supportedFormats = []
        supportedCRS = []
        bboxLimits = None
        timepositions = None
        
        if endpoint != None:
            
            st1 = time.time()
            wcs, layers = self._getWCSObj(endpoint)
            log.debug("retrieved wcs metadata in  = %s" % (time.time() - st1,))
            
            if layer != None:
                st1 = time.time()
                layerMetadata, bboxLimits, timepositions, supportedFormats, supportedCRS =\
                       self._getWCSMetadata(wcs, layer)
                log.debug("retrieved layer metadata in  = %s" % (time.time() - st1,))
                
        
        if bbox != None:
            c.selected_bbox = bbox
        elif bboxLimits != None:
            c.selected_bbox = bboxLimits
        else:
            c.selected_bbox = '-180.0,-90.0,180.0,90.0'
        
        log.debug("timepositions = %s" % (timepositions,))
        if timepositions != None and timepositions != [None]:
            builder = DateTimeOptionsBuilder(timepositions)
            options = builder.buildOptions()
            #log.debug("options = %s" % (options,))
            c.timedata = utils.toJSON(options) 
            
        c.endpoint = endpoint
        
        c.selected_layer = layer
        c.layer_options = [(x,x) for x in layers]
        c.layer_options.insert(0, ("","")) #add an empty value at the start
        
        c.selected_format = format
        c.format_options = [(x,x) for x in supportedFormats]
        c.format_options.insert(0, ("","")) #add an empty value at the start
        
        c.selected_crs = crs
        c.crs_options = [(x,x) for x in supportedCRS]
        c.crs_options.insert(0, ("","")) #add an empty value at the start
        
        # get server information from config file
        g.server=config['app_conf']['serverurl']
        
        lp = OutlineLayersConfigParser()

                
        layersList = lp.getOutlineLayerList('wcsdown')
        log.debug("layerList = %s" % (layersList,))
        
        c.baseLayerJSON = utils.toJSON(layersList) 
        
        log.debug("rendering template after %ss" % (time.time() - st,))
        return render('wcsdown.html')
    
    
    def download(self):
        
        params = self._getParams()
        log.debug("params = %s" % (params,))
        
        endpoint = params.get('ENDPOINT')
        
        args = {}
        args['identifier'] = params['LAYER']
        args['bbox'] = tuple(params.get('BBOX').split(','))
        args['format'] = params['FORMAT']
        args['crs'] = params['CRS']

        if (params.get('SINGLE_TIME',"").upper() == 'TRUE'):
            args['time'] = [params.get('TIME')]
        else:
            args['time'] = [params.get('TIME'), params.get('TIME_END')]
        
        wcs, layers = self._getWCSObj(endpoint)
        
        log.debug("wcs.url = %s" % (wcs.url,))
        
        assert args['identifier'] in layers
        
        log.debug("args = %s" % (args,))
        
        oldProxy = proxyFix(endpoint)
        try:
            output = wcs.getCoverage(**args)
        except Exception, e:
            log.exception("Exception occurred")
            raise
        finally:
            resetProxy(oldProxy)
        
        log.debug("output = %s" % (output,))
        
        log.debug("output.headers.keys() = %s" % (output.headers.keys(),))
        log.debug("output.geturl() = %s" % (output.geturl(),))
        
        response.headers['Content-Type']=output.headers['Content-Type']
        
        log.debug("output.headers.keys() = %s" % (output.headers.keys(),))
        
        contentDescription = None
        
        for k in output.headers.keys():
            if k.lower() == 'content-disposition':
                contentDescription = output.headers[k]
        
        if contentDescription is not None:
            log.debug("contentDescription = %s" % (contentDescription,))
            response.headers['Content-Disposition'] = contentDescription
        else:
            response.headers['Content-Disposition'] = paste.httpheaders.CONTENT_DISPOSITION(attachment=True, filename='download')
            
        return output.read()
        
        

    def _getWCSObj(self, endpoint):
        oldProxy = proxyFix(endpoint)
        try:
            
            log.debug("wcs endpoint = %s" % (endpoint,))
            
            getCapabilitiesEndpoint = parseEndpointString(endpoint, 
                        {'Service':'WCS', 'Request':'GetCapabilities'})
            
            log.debug("wcs endpoint = %s" % (getCapabilitiesEndpoint,))
            #requires OWSLib with cookie support
            wcs=WebCoverageService(getCapabilitiesEndpoint, version='1.0.0',cookies= request.headers.get('Cookie', ''))
            
            layers = [x[0] for x in wcs.items()]
        finally:
            resetProxy(oldProxy)
        
        return wcs, layers
    
    def _getWCSMetadata(self, wcs, layer):
        
        oldProxy = proxyFix(wcs.url)
        try:
            layerMetadata = wcs[layer]
            bboxLimits = ','.join([str(x) for x in layerMetadata.boundingBoxWGS84])
            timepositions = layerMetadata.timepositions
            supportedFormats = layerMetadata.supportedFormats  
            supportedCRS = layerMetadata.supportedCRS          

        finally:
            resetProxy(oldProxy)
        
        return layerMetadata, bboxLimits, timepositions, supportedFormats, supportedCRS
        
    def _getParams(self):
        
        params = {}
        for k in request.params.keys():
            value = request.params[k]
            if value == "":
                value = None
            
            if value.__class__ == unicode:
                value = value.encode('latin-1')
                
            params[k.upper()] = value
        
        return params
        
