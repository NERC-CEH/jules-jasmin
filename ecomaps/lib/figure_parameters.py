"""
Separates out the parameters for each layer in a figure, applying default values.
Moved from figure_builder.py.

@author: rwilkinson
"""
import logging
import ecomaps.lib.coordinate_params as coordinate_params
import ecomaps.lib.datasets as datasets
from ecomaps.lib.wmc_util import parseEndpointString

log = logging.getLogger(__name__)

class LayerInfo(object):
    """Object to hold the data needed to plot one layer in a figure, including its legend.
    """
    def __init__(self, id, endpoint, layerName, params, legendURL, capabilitiesURL, dimensionNames, wmsLayer, keywordData):
        self.id = id
        self.endpoint = endpoint
        self.layerName = layerName
        self.params = params
        self.legendURL = legendURL
        self.capabilitiesURL = capabilitiesURL
        self.dimensionNames = dimensionNames
        self.wmsLayer = wmsLayer
        self.keywordData = keywordData
        self.cachedImage = None

class LayerInfoBuilder(object):
    """Builds a list of objects holding the data needed to plot each layer in a figure.
    """
    def __init__(self, requestParams, defaults, protocol='WMS'):
        
        self.params = {}
        self.defaults = {}
        self.protocol = protocol

        for k, v in requestParams.items():
            self.params[k.upper()] = v
        
        for k, v in defaults.items():
            self.defaults[k.upper()] = v
        
    def buildInfo(self, sessionEndpointData):
        """Creates a list of LayerInfo objects each containing data for one layer in a figure.
        """
        
        infoList = []
        
        for i in range(1,11):
            s = '%s_' % (i)
            
            #find all the parameters that correspond to layer num i
            keys = filter(lambda x: x.find(s) == 0, self.params.keys())
            
            #if there are no parameters for this layer there won't be any more
            if len(keys) == 0:
                break
            
            if i == 10:
                raise Exception("Can't support 10 layers.")
            
            
            #get the parameters for this layer (taking the #_ off the front)
            p = {}
            for k in keys:
                if not self.params[k] in ['', None]: 
                    p[k[len(s):]] = self.params[k]

            for k,v in self.defaults.items():
                p.setdefault(k, v)

            log.debug("p = %s" % (p,))
            name = p['LAYERS']
            endpoint = p.pop('ENDPOINT')
            layerId = p.pop('LAYER_ID', None)

            coordinate_params.adjustCoordinateOrderParams(p, self.protocol)

            # Use the cached WMS capabilities data if available.
            li = makeLayerInfo(layerId, endpoint, name, p, sessionEndpointData)

            infoList.append(li)
            
        return infoList

def makeDefaultedParameters(params, specificDefaults):
    """Apply defaults to a set of parameters, returning the merged set.
    """
    log.debug("params = %s" % (params,))
    defaults = {
        'BBOX': "%s,%s,%s,%s" % (-180, -90, 180, 90),
        'WIDTH': 900,
        'HEIGHT': 600,
        'SRS': 'EPSG:4326',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'TRUE'
    }

    defaults.update(specificDefaults)

    for k in defaults.keys():
        if not params.get(k, None) in ['', None]:
            defaults[k] = params[k]

    defaults['REQUEST'] = 'GetMap'
    log.debug("defaults = %s" % (defaults,))

    return defaults

def updateLayerParameters(layerInfoList, updates):
    """Apply parameter updates contained in a dictionary to data for each layer in a list.
    """
    for layerInfo in layerInfoList:
        layerInfo.params.update(updates)

def makeLayerInfo(layerId, endpoint, name, params, sessionEndpointData):
    """Contruct LayerInfo from data retrieved from the Datasets cache.
    """
    log.debug("makeLayerInfo for %s (layerId: %s - endpoint: %s)" % (name, layerId, endpoint))
    keywordData = []
    if layerId != None:
        log.debug("- trying to retrieve from Datasets")
        layerData = datasets.datasetManager.getLayerData(layerId, sessionEndpointData)

        antecedentIds = datasets.datasetManager.findAntecedentNodeIds(layerId, includeStartNode=True)
        for nodeId in antecedentIds:
            node = datasets.datasetManager.getNode(nodeId, sessionEndpointData)
            if node:
                keywordData.append(node.keywordData)

    else:
        log.debug("- performing ad-hoc retrieval")
        layerData = datasets.datasetManager.getLayerDataByEndpointAndName(endpoint, name, sessionEndpointData)

    capabilitiesURL = None
    legendURL = None
    dimensionNames = []
    if layerData != None:
        capabilitiesURL = layerData.getCapabilitiesUrl
        # Find the legend URL for the style (or the first style if there isn't a styles parameter).
        styleData = None
        if 'STYLES' in params:
            style = params['STYLES']
            for s in layerData.styles:
                if s['name'] == style:
                    styleData = s
                    break
        else:
            if len(layerData.styles) > 0:
                styleData = layerData.styles[0]
        if styleData != None and 'legendURL' in styleData and 'onlineResource' in styleData['legendURL']:
            baseLegendURL = styleData['legendURL']['onlineResource']
            paramsWithoutRequest = params.copy()
            paramsWithoutRequest.pop('REQUEST')
            legendURL = parseEndpointString(baseLegendURL, paramsWithoutRequest)

        for dimension in layerData.dimensions:
            dimensionNames.append(dimension['name'])

    li = LayerInfo(layerId, endpoint, name, params, legendURL, capabilitiesURL, dimensionNames, layerData, keywordData)
    return li

class FigureOptions(object):
    """Object to hold the overall options for a figure.
    """
    def __init__(self, requestParams):
        self.style = requestParams.get('figure-style', 'default')
        self.grid = (requestParams.get('figure-grid', 'off') == 'on')
