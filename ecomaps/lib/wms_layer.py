"""
Holds data for a layer from a WMS capabilities document.

@author: rwilkinson
"""

import logging

import ecomaps.lib.dimension_format as dimension_format
import ecomaps.lib.xml_util as xml_util

log = logging.getLogger(__name__)

XLINK_URI = 'http://www.w3.org/1999/xlink'

class WmsLayer:
    """Holds the WMS data needed for layer.
    """
    def setValues(self, title, name, abstract, getMapUrl, getCapabilitiesUrl, getFeatureInfoUrl,
                  getDisplayOptionsUrl, dimensions, style):
        """Sets layer fields.
        @param title: display title for layer
        @param name: layer name
        @param abstract: layer abstract
        @param getMapUrl: URL for GetMap requests
        @param getCapabilitiesUrl: URL for GetCapabilities requests
        @param getFeatureInfoUrl: URL for GetFeatureInfo requests
        @param getDisplayOptionsUrl: URL for GetDisplayOptions requests
        @param dimensions: list of dimension data dicts
        @param style: list of style data dicts
        """
        self.title = title
        self.name = name
        self.abstract = abstract
        self.getMapUrl = getMapUrl
        self.getCapabilitiesUrl = getCapabilitiesUrl
        self.getFeatureInfoUrl = getFeatureInfoUrl
        self.getDisplayOptionsUrl = getDisplayOptionsUrl
        self.dimensions = dimensions
        self.styles = style

    def populateFromLayerElement(self, ns, layerEl, commonData):
        """Populates a WmsLayer instance from a WMS capabilities Layer element
        @param ns: namespace in capabilities document
        @param layerEl: Layer element
        @param commonData: dict of capabilities data that is not specific to the layer
        """
        self.title = xml_util.getSingleChildTextByNameNS(layerEl, ns, 'Title')
        self.name = xml_util.getSingleChildTextByNameNS(layerEl, ns, 'Name')
        self.abstract = xml_util.getSingleChildTextByNameNS(layerEl, ns, 'Abstract')
        self.getMapUrl = commonData['getMapUrl']
        self.getCapabilitiesUrl = commonData['getCapabilitiesUrl']
        self.getFeatureInfoUrl = commonData['getFeatureInfoUrl']
        self.wmsVersion = commonData['wmsVersion']
        self.getCoverageUrl = commonData['getCoverageUrl']

        # Parse Dimension element into attributes and list of values.
        # First look for pre-WMS 1.3.0 Extent elements.
        extents = {}
        for extentEl in xml_util.getChildrenByNameNS(layerEl, ns, 'Extent'):
            name = extentEl.getAttribute('name')
            extentData = extentEl.firstChild
            if extentData != None:
                extentStr = extentEl.firstChild.data.strip()
                extentValues = extentStr.split(',')
                extents[name] = extentValues

        # Find the Dimension elements.
        self.dimensions = []
        for dimensionEl in xml_util.getChildrenByNameNS(layerEl, ns, 'Dimension'):
            name = dimensionEl.getAttribute('name')
            units = dimensionEl.getAttribute('units')
            unitSymbol = dimensionEl.getAttribute('unitSymbol')
            default = dimensionEl.getAttribute('default')
            dimensionData = dimensionEl.firstChild
            if dimensionData != None:
                dimensionStr = dimensionEl.firstChild.data.strip()
                dimensionValues = dimensionStr.split(',')
            elif name in extents:
                dimensionValues = extents[name]
            else:
                dimensionValues = None
            if dimensionValues:
                dimension = {
                    'name': name,
                    'units': units,
                    'unitSymbol': unitSymbol,
                    'default': default,
                    'dimensionValues': dimensionValues
                    }
                self.dimensions.append(dimension)

        # Parse Style element into list of values.
        self.styles = []
        for styleEl in xml_util.getChildrenByNameNS(layerEl, ns, 'Style'):
            name = xml_util.getSingleChildTextByNameNS(styleEl, ns, 'Name')
            title = xml_util.getSingleChildTextByNameNS(styleEl, ns, 'Title')
            style = {
                'name': name,
                'title': title,
                }
            legendUrlEl = xml_util.getSingleChildByNameNS(styleEl, ns, 'LegendURL')
            if legendUrlEl != None:
                width = legendUrlEl.getAttribute('width')
                height = legendUrlEl.getAttribute('height')
                onlineResourceEl = xml_util.getSingleChildByNameNS(legendUrlEl, ns, 'OnlineResource')
                legendURL = onlineResourceEl.getAttributeNS(XLINK_URI, 'href')

                style['legendURL'] = {
                    'width': width,
                    'height': height,
                    'onlineResource': legendURL
                    }
            self.styles.append(style)

        self.getDisplayOptionsUrl = None
        for metadataUrlEl in xml_util.getChildrenByNameNS(layerEl, ns, 'MetadataURL'):
            metadataUrlType = metadataUrlEl.getAttribute('type')
            if metadataUrlType and (metadataUrlType == 'display_options') :
                if xml_util.getSingleChildTextByNameNS(metadataUrlEl, ns, 'Format') == 'application/json':
                    onlineResourceEl = xml_util.getSingleChildByNameNS(metadataUrlEl, ns, 'OnlineResource')
                    if onlineResourceEl:
                        self.getDisplayOptionsUrl = onlineResourceEl.getAttributeNS(XLINK_URI, 'href')

    def generateDimensionDisplayValues(self, dimensionFormat, dimensionReverse):
        """Creates dimension values formatted for display if there is an appropriate format.
        @param dimensionFormat: dimension format string for the layer
        @param dimensionReverse: dimensions for which to reverse order (comma separated string)
        """
        log.debug("Format: %s   reverse: %s" % (dimensionFormat, dimensionReverse))

        if dimensionReverse:
            dimensionsToReverse = [x.strip() for x in dimensionReverse.split(',')]
        else:
            dimensionsToReverse = []

        if dimensionFormat:
            formatDetails = dimension_format.parse_dimension_format_string(dimensionFormat)
            for dim in self.dimensions:
                dimName = dim['name']

                reverseDimension = ((dimName in dimensionsToReverse) and ('dimensionValues' in dim))
                if (reverseDimension):
                    dim['dimensionValues'].reverse()

                if dimName in formatDetails:
                    dimensionFormat = formatDetails[dimName]
                    labels = []
                    displayValues = []
                    startValues = []
                    for dimensionFieldFormat in dimensionFormat.dimensionFieldFormats:
                        labels.append(dimensionFieldFormat.label)
                        if 'dimensionValues' in dim:
                            displayValues.append(dimensionFieldFormat.applyFormat(dimName,
                                                                                  dim['dimensionValues']))
                            startValues.append(dimensionFieldFormat.getStartValue(dimName,
                                                                                  reverseDimension))
                    dim['label'] = dimensionFormat.label
                    dim['displayValues'] = displayValues
                    dim['displayLabels'] = labels
                    dim['startValues'] = startValues

    def getAsDict(self):
        """Returns the contents of the object as a dictionary (e.g., for conversion to a JSON object)
        """
        return {'id': self.id, 'title': self.title, 'name': self.name, 'abstract': self.abstract, 'getMapUrl': self.getMapUrl,
                'getCapabilitiesUrl': self.getCapabilitiesUrl, 'getFeatureInfoUrl': self.getFeatureInfoUrl,
                'wmsVersion': self.wmsVersion, 'getCoverageUrl': self.getCoverageUrl,
                'getDisplayOptionsUrl': self.getDisplayOptionsUrl, 'dimensions': self.dimensions, 'styles': self.styles}
