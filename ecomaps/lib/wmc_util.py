# Copyright (C) 2007 STFC & NERC (Science and Technology Facilities Council).
# This software may be distributed under the terms of the
# Q Public License, version 1.0 or later.
# http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt
"""
Utils to aid use of wmc docs - including interfacing these with the con terra client
and getting associated legend data

@author: Calum Byrom, modified for NDG Security by Dominic Lowe
"""
from ecomaps.lib.base import *
from ecomaps.model.WMC import WMC
from ecomaps.lib import exceptions
import urllib2, urllib
import os
import logging
import urlparse
log = logging.getLogger(__name__)


def getConTerraDoc(wmcURLs):
    """
    Construct an aggregated XML file and display this as a temporary webpage; this will automatically be
    POSTED so that the data is sent via POST to the Con Terra mapClient to visualise (as required by this client)
    @param wmcURLS: An array of URLs pointing to WMC docs to visualise
    """
    # firstly, retrieve each WMC doc
    wmcDocs = []
    for wmcURL in wmcURLs:
        wmcDocs.append(WMC(wmcURL))

    # now create a dictionary of WMS/layer from these docs - to avoid duplicate layers
    c.wms = {}
    for wmcDoc in wmcDocs:
        for layer in wmcDoc.layers:
            if layer.wmsURL not in c.wms:
                c.wms[layer.wmsURL] = [layer.name]
            else:
                if layer.name not in c.wms[layer.wmsURL]:
                    c.wms[layer.wmsURL].append(layer.name)

    # now create the form to post this data
    c.redirectToConterra = True; #TODO, remove?
    response.write(render('selectedItems'))



def GetWebMapContext(self):
    """
    Lookup a WMC doc and return it in the response
    """
    # retrieve context data from the specifiled url
    wmcDoc = RetrieveWebMapContext(self, self.inputs['ENDPOINT'])
    log.info('WMC RESPONSE %s'%response)
    response.headers['Content-Type'] = 'text/xml'
    response.write(wmcDoc)

def GetLegendUrl(self):
    """
    Look up the URL for a legend for a WMS map
    NB, all required parameters are already included in the endpoint by this stage
    """
    endpoint = self.inputs['ENDPOINT']

    if not endpoint:
        raise exceptions.MissingParameterValue, "ENDPOINT parameter required"
    log.debug("endpoint = %s" % (endpoint,))
    req = urllib2.Request(endpoint, None, {'Cookie': request.headers.get('Cookie', '')})
    url = req.get_full_url()

    return url

def GetLegend(self):
    """
    Look up a legend for a WMS map, returning an HTML fragment to display the legend.
    NB, all required parameters are already included in the endpoint by this stage
    """
    url = GetLegendUrl(self)

    return "<img src=\"%s\" />" % (url,)

def RetrieveWebMapContext(self, endpoint):
    """
    Get a WMC doc from a specified endpoint
    @param endpoint: endpoint to retrieve WMC doc from
    """
    if not endpoint:
        raise exceptions.MissingParameterValue, "ENDPOINT parameter required"
    log.info('Getting WebMapContext from endpoint: ' + endpoint)
    #urlstring=('%s&request=GetContext'%(str(endpoint)))
    urlstring=('%s?request=GetContext&service=WMS'%(str(endpoint)))
#    urlstring = str(endpoint)
    log.info("urlstring=%s" % (urlstring,))
    #cookies are passed to enable authorisation mechanisms e.g. ndg security
    #try:

    req = urllib2.Request(urlstring)
    try:
        req.add_header('Cookie', request.headers.get('Cookie', ''))
    except:
        pass
    filehandle = openURL(req)
    return filehandle.read()

def GetWebMapCapabilities(endpoint):
    
    urlstring = parseEndpointString(endpoint, {'REQUEST':'GetCapabilities',
                                               'SERVICE':'WMS',
                                               'VERSION':'1.3.0'} )
    log.debug("urlstring = %s" % (urlstring,))
    req = urllib2.Request(urlstring)
    try:
        req.add_header('Cookie', request.headers.get('Cookie', ''))
    except:
        pass

    try:    
        filehandle = openURL(req)
        return filehandle.read()
    except urllib2.HTTPError, e:            
        log.exception("exception occurred")
        if e.code == 401:
            log.info ('401 unauthorized error in ecomaps')
            return abort(401) #triggers ndg security framework
        elif e.code == 403:  #TODO: 403 response is UNTESTED.
            # User is authenticated but doesn't have the required permissions
            # or an error occurred in the authorization process
            # User is authenticated but doesn't have the required permissions
            # or an error occurred in the authorization process
            return abort(403)
        else:
            raise e

def GetFeatureInfo(endpoint):
    info_format = urllib.unquote(getQueryParameter(endpoint, 'info_format').lower())
    urlstring = parseEndpointString(endpoint, {'REQUEST':'GetFeatureInfo',
                                               'SERVICE':'WMS'} )
    log.debug("urlstring = %s" % (urlstring,))
    req = urllib2.Request(urlstring)
    try:
        req.add_header('Cookie', request.headers.get('Cookie', ''))
    except:
        pass

    try:
        filehandle = openURL(req)
        returned_format = filehandle.headers.type.lower()
        if returned_format != info_format:
            if returned_format == 'application/vnd.ogc.se_xml':
                raise Exception("GetFeatureInfo request error %s" % filehandle.read())
            else :
                raise Exception("GetFeatureInfo request returned Content-Type %s instead of requested %s" %
                                (returned_format, info_format))
        return filehandle.read()
    except urllib2.HTTPError, e:
        log.exception("exception occurred")
        if e.code == 401:
            log.info ('401 unauthorized error in cowsclient')
            return abort(401) #triggers ndg security framework
        elif e.code == 403:  #TODO: 403 response is UNTESTED.
            # User is authenticated but doesn't have the required permissions
            # or an error occurred in the authorization process
            return abort(403)
        else:
            raise e

def GetResponse(url):
    req = urllib2.Request(url)
    try:
        req.add_header('Cookie', request.headers.get('Cookie', ''))
    except:
        pass
    filehandle = openURL(req)
    return filehandle.read()    
    

noProxyOpener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.ProxyHandler({}))

def openURL(req):
    log.info("Making request: %s "%(req.get_full_url(),))
    if _shouldUseProxy(req.get_full_url()):
        log.debug("using proxy")
        fh = urllib2.urlopen(req)
    else:
        log.debug("not using proxy")
        fh = noProxyOpener.open(req)
        
    return fh

def _shouldUseProxy(urlstring) :
    no_proxy   = os.environ.get('no_proxy', '')
    
    urlObj = urlparse.urlparse(urlstring)
    for np in no_proxy.split(','):
        if urlObj.hostname == urlparse.urlparse(np).hostname:
            return False
    
    return True

def proxyFix(url):
    oldProxyVal = os.environ.get('http_proxy', None)
    
    if oldProxyVal != None:
        if os.environ['http_proxy'] != "" and not _shouldUseProxy(url):
            os.environ['http_proxy'] = ""
            reload(urllib2)

    return oldProxyVal


def resetProxy(oldProxyVal):
    
    if oldProxyVal == None or oldProxyVal == "":
        return
    
    if os.environ['http_proxy'] != oldProxyVal:
        os.environ['http_proxy'] = oldProxyVal
        reload(urllib2)


def parseEndpointString(endpointString, requiredParams):
    """
    Take an endpoint string and add the required params if they don't already appear
    on the string.
    """
    urlObj = urlparse.urlparse(endpointString)
    
    queryParams = _parse_qs(urlObj.query)
    
    for k, v in requiredParams.items():
        queryParams[k.lower()] = v
    
    queryString = _build_qs(queryParams)
    
    # as urlObj.query isn't writable extract the data to a list
    # and replace the query data with the new query string
    res = [x for x in urlObj]
    res[4] = queryString
                             
    return urlparse.urlunparse(res)

def getQueryParameter(url, name):
    """
    Returns the value of a query parameter from a URL (or None if the parameter
    is not present).
    """
    urlObj = urlparse.urlparse(url)
    queryParams = _parse_qs(urlObj.query)
    return queryParams.get(name.lower(), None)

def _parse_qs(queryString):
    """
    returns a dictionary of key, value pairs from the query string. The keys in
    the return dictionary are in all lowercase. Empty parameters are ignored.
    The query string shouln't have a leading '?' character.
    """
    queryDict = {}
    
    for kvString in queryString.split('&'):
        
        if kvString == '':
            continue
        
        key, value = kvString.split('=')
        
        if value in ['', None]:
            continue
            
        queryDict[key.lower()] = value
    
    return queryDict

def _build_qs(queryDict, upperCaseKeys=True):
    """
    Builds a url query string out of a dictionary. doesn't add the initial '?' character.
    
    If upperCaseKeys == True then all the dictionary keys will be included as capital letters.
    """
    
    queryStr = ""
    for k, v in queryDict.items():
        
        if upperCaseKeys:
            k = k.upper()
        
        queryStr += "%s=%s&" % (k, v)
    
    #remove the last &
    queryStr = queryStr[:-1]
    return queryStr
    
