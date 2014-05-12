"""
Performs WMS capabilities calls and processes the results.

@author: rwilkinson
"""

import logging
import re
import urlparse
import xml.dom.minidom

from ecomaps.lib.endpoint_hierarchy_builder import EndpointHierarchyBuilder, Node
from ecomaps.lib.wmc_util import parseEndpointString
from ecomaps.lib.wms_layer import WmsLayer
from ecomaps.lib.wms_capability_cache import WmsCapabilityCache
import ecomaps.lib.xml_util as xml_util

log = logging.getLogger(__name__)

XLINK_URI = 'http://www.w3.org/1999/xlink'

class WmsCapabilityReader():
    def __init__(self, config):
        self.wmsCapabilityCache = WmsCapabilityCache(config)
        self.proxyUrl = config.get('proxyUrl')

    def getEndpointServiceData(self, endpoint, forceRefresh):
        """Returns service data for an endpoint.
        """
        log.debug("getEndpointData called for %s", endpoint['wmsurl'])
        wmsUrl = self.makeProxiedUrl(endpoint['wmsurl'])
        wmcDoc = self.wmsCapabilityCache.getWmsCapabilities(wmsUrl, forceRefresh)

        dom = xml.dom.minidom.parseString(wmcDoc)
        # Get the namespace URI for the document root element.
        ns = dom.documentElement.namespaceURI

        # Get the version the WMS server responded with.
        wmsVersion = dom.documentElement.getAttribute('version')

        service = xml_util.getSingleChildByNameNS(dom.documentElement, ns, 'Service')
        if service == None:
            return None

        title = xml_util.getSingleChildTextByNameNS(service, ns, 'Title')
        abstract = xml_util.getSingleChildTextByNameNS(service, ns, 'Abstract')

        # Break internal references to facilitiate garbage collection.
        dom.unlink()

        return {
            'version': wmsVersion,
            'title': title,
            'abstract': abstract
            }

    def getLayers(self, endpoint, parentId, idMap, keywordData, forceRefresh):
        """Returns a list of 'endpoint_hierarchy_builder.Node's for the layers of an endpoint in a WMC document.
        Also, adds nodes to a map from node ID to node.
        """
        log.debug("getLayers called for %s", endpoint['wmsurl'])
        log.debug("  keywordData: %s" % keywordData)
        wmsUrl = self.makeProxiedUrl(endpoint['wmsurl'])
        wmcDoc = self.wmsCapabilityCache.getWmsCapabilities(wmsUrl, True)

        dom = xml.dom.minidom.parseString(wmcDoc)
        # Get the namespace URI for the document root element.
        ns = dom.documentElement.namespaceURI

        # Get the version the WMS server responded with.
        wmsVersion = dom.documentElement.getAttribute('version')

        nodes = []
        capability = xml_util.getSingleChildByNameNS(dom.documentElement, ns, 'Capability')
        if capability == None:
            return None

        getCapabilitiesUrlEl = xml_util.getSingleChildByPathNS(capability,
                                                               [(ns, 'Request'), (ns, 'GetCapabilities'), (ns, 'DCPType'),
                                                                (ns, 'HTTP'), (ns, 'Get'), (ns, 'OnlineResource')])
        getCapabilitiesUrl = getCapabilitiesUrlEl.getAttributeNS(XLINK_URI, 'href')
        if not getCapabilitiesUrl:
            getCapabilitiesUrl = xml_util.getAttributeByLocalName(getCapabilitiesUrlEl, 'href')
        log.debug("GetCapabilities URL: %s", getCapabilitiesUrl)
        getCapabilitiesUrl = parseEndpointString(getCapabilitiesUrl, {'REQUEST':'GetCapabilities', 'SERVICE':'WMS'})

        getFeatureInfoOnlineResourceEl = xml_util.getSingleChildByPathNS(capability,
                                                                         [(ns, 'Request'), (ns, 'GetFeatureInfo'),
                                                                          (ns, 'DCPType'), (ns, 'HTTP'),
                                                                          (ns, 'Get'), (ns, 'OnlineResource')])
        if getFeatureInfoOnlineResourceEl:
            getFeatureInfoUrl = getFeatureInfoOnlineResourceEl.getAttributeNS(XLINK_URI, 'href')
            if not getFeatureInfoUrl:
                getFeatureInfoUrl = xml_util.getAttributeByLocalName(getFeatureInfoOnlineResourceEl, 'href')
            log.debug("GetFeatureInfo URL: %s", getFeatureInfoUrl)
            getFeatureInfoUrl = getFeatureInfoUrl.rstrip('?&')
        else:
            getFeatureInfoUrl = None

        getMapOnlineResourceEl = xml_util.getSingleChildByPathNS(capability,
                                                               [(ns, 'Request'), (ns, 'GetMap'), (ns, 'DCPType'), (ns, 'HTTP'),
                                                                (ns, 'Get'), (ns, 'OnlineResource')])
        getMapUrl = getMapOnlineResourceEl.getAttributeNS(XLINK_URI, 'href')
        if not getMapUrl:
            getMapUrl = xml_util.getAttributeByLocalName(getMapOnlineResourceEl, 'href')
        log.debug("GetMap URL: %s", getMapUrl)
        getMapUrl = getMapUrl.rstrip('?&')
        getMapUrl = self.makeProxiedUrl(getMapUrl)

        commonData = {
            'getCapabilitiesUrl': getCapabilitiesUrl,
            'getFeatureInfoUrl': getFeatureInfoUrl,
            'getMapUrl': getMapUrl,
            'wmsVersion': wmsVersion
            }
        if 'wcsurl' in endpoint:
            commonData['getCoverageUrl'] = endpoint['wcsurl']
        for layer in xml_util.getChildrenByNameNS(capability, ns, 'Layer'):
            self.handleLayer(ns, layer, nodes, endpoint, parentId, commonData, keywordData, idMap)

        # Break internal references to facilitate garbage collection.
        dom.unlink()

        return nodes

    def handleLayer(self, ns, layerEl, nodes, endpoint, parentId, commonData, antecedentKeywordData, idMap):
        """Processes a layer.
        Determines whether the layer has sublayers, in which case this method is called recursively,
        or if it is a leaf, in which case a node is added to the node list.
        """
        subLayers = xml_util.getChildrenByNameNS(layerEl, ns, 'Layer')
        isLeaf = len(subLayers) == 0
        layer = WmsLayer()
        layer.populateFromLayerElement(ns, layerEl, commonData)
        log.debug("Layer %s %s" % (layer.name, layer.title))

        self.setLayerId(layer, parentId, isLeaf)

        # Merge all keyword data applicable to the layer.
        keywordData = self.getLayerDataFromEndpoint(endpoint, layer)
        if antecedentKeywordData:
            mergedKeywordData = antecedentKeywordData.copy()
            mergedKeywordData.update(keywordData)
        else:
            mergedKeywordData = keywordData

        log.debug("keywordData: %s" % mergedKeywordData)
        layer.generateDimensionDisplayValues(mergedKeywordData.get('dimension_format', None),
                                             mergedKeywordData.get('dimension_reverse', None))

        treeInfo = self.makeTreeInfo(endpoint, layer, isLeaf, keywordData)


        # Look for sublayers - if there any any, call this method recursively to add them to the tree,
        # otherwise just add a leaf node.
        children = []
        node = Node(layer.id, layer, children, treeInfo, keywordData)
        #idMap[layer.id] = node
        nodes.append(node)
        if isLeaf:
            log.debug("Found layer: title '%s' (ID=%s)", layer.title, layer.id)
        else:
            for lyr in subLayers:
                self.handleLayer(ns, lyr, children, endpoint, layer.id, commonData, antecedentKeywordData, idMap)

    def setLayerId(self, layer, parentId, isLeaf):
        """Constructs an id for the tree node.
        """
        if layer.name:
            layerId = layer.name
        else:
            layerId = layer.title

        if isLeaf:
            prefix = EndpointHierarchyBuilder.KEY_PREFIX_LEAF_LAYER
        else:
            prefix = EndpointHierarchyBuilder.KEY_PREFIX_CONTAINER_LAYER
        layer.id = prefix + layerId + EndpointHierarchyBuilder.LAYER_ID_SEPARATOR + parentId

    def getLayerDataFromEndpoint(self, endpoint, layer):
        """Finds keyword data configured for matching layers of an endpoint and stores them in the
        layer object.
        """
        if ((not layer.name) or (not 'layerSetData' in endpoint) or
            (not 'layers' in endpoint['layerSetData'])):
            return {}

        layers = endpoint['layerSetData']['layers']

        # Find whether one of the sets of layer data for the endpoint matches the layer name.
        layerKeywordData = {}
        for k, l in layers.iteritems():
            if 'name' in l:
                namePatt = l['name'].format(endpoint=endpoint['key']) + '\Z'
                log.debug("namePatt '%s'" % namePatt)
                if re.match(namePatt, layer.name):
                    log.debug("Matches %s" % layer.name)
                    layerKeywordData = l

        return layerKeywordData

    def makeTreeInfo(self, endpoint, layer, isLeaf, keywordData):
        """Empty implementation of method to populate additional information for layers in the layer tree.
        """
        return {}

    def ensureEndpointCached(self, endpoint, forceRefresh=False):
        """Retrieves and caches a WMS capabilities document if not already cached or if
        forceRefresh=True.
        """
        if 'wmsurl' in endpoint:
            log.debug("ensureEndpointCached called for %s", endpoint['wmsurl'])
            wmsUrl = self.makeProxiedUrl(endpoint['wmsurl'])
            wmcDoc = self.wmsCapabilityCache.getWmsCapabilities(wmsUrl, forceRefresh)
        else:
            log.error("No WMS URL configured for endpoint")

    def makeProxiedUrl(self, url):
        """Converts a URL into one using a proxy that accepts URLs of the form
        http://<proxy prefix>/<target scheme>/<target host>/<target port>/<target path>
        """
        if self.proxyUrl:
            urlParts = urlparse.urlsplit(url)
            netlocParts = urlParts.netloc.partition(':')
            host = netlocParts[0]
            port = netlocParts[2] if netlocParts[2] else '-'
            proxyParts = urlparse.urlsplit(self.proxyUrl)
            mergedPath = '/'.join([proxyParts.path.rstrip('/'), urlParts.scheme,
                                   host, port, urlParts.path.lstrip('/')])
            mergedParts = (proxyParts.scheme, proxyParts.netloc, mergedPath,
                           urlParts.query, urlParts.fragment)
            return urlparse.urlunsplit(mergedParts)
        else:
            return url
