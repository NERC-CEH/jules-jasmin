
from ecomaps.lib.wmc_util import openURL

import logging
import urllib2 
import urlparse
import simplejson as json
import libxml2dom

log = logging.getLogger(__name__)

def parseCowsCatalog(cowsEndpoint):
    req = urllib2.Request(cowsEndpoint)
    fh = openURL(req)
    htmlString = fh.read()
    fh.close()
    
    doc = libxml2dom.parseString(htmlString, html=1)
    
    COWSLinks = []
    
    for liElt in doc.getElementsByTagName("li"):
    
        childText = ""
        links = {}
    
        for c in liElt.childNodes:
    
            # get the name by adding together all the text elements and then
            # stripping whitespace and [].
            if c.nodeType == 3:
                childText += c.nodeValue
    
            # build a dictionary of the links with their ascociated text
            elif c.nodeName == 'a' and c.hasAttribute('href'):
                liknName = str(''.join(c.textContent.split())) # removing whitespace and converting from unicode
                
                href = c.getAttribute('href')
                    
                linkTarget =  urlparse.urljoin(cowsEndpoint, href)
                links[liknName] = str(linkTarget)
    
        childText = ''.join(childText.split()) # strip the whitespace
        childText = str(childText.replace('[]','')) # remove any angle brackets
    
        COWSLinks.append((childText, links))
    
    return COWSLinks

def toJSON(obj):
    return json.dumps(obj).replace('"', '\\"')

def filterEnpointList(endpointList, requiredType, searchCowsIndex=True):
        epList = []
        
        if endpointList is not None:
            for e in endpointList:
                if requiredType!= 'COWS' and e['service'] == 'COWS' and searchCowsIndex:
                    try:
                        for linkName, linkDict in parseCowsCatalog(e['url']):
                            if requiredType in linkDict.keys():
                                epList.append(
                                    {'service':requiredType, 
                                     'url':linkDict[requiredType], 
                                     'name':linkName}
                                )
                    except:
                        log.exception("An error occurred while reading cows catalog at %s"\
                                      % (e['url'],))
                            
                elif e['service'] == requiredType:
                    epList.append(e)
                
        return epList    
