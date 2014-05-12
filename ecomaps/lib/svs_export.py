"""
Export in the SVS exchange format.

@author: rwilkinson
"""
import logging
import urllib
import os, tempfile
import xml.dom.minidom
from ecomaps.lib.export_parameters import ExportResult
import ecomaps.lib.wmc_util as wmc_util
import ecomaps.lib.xml_util as xml_util

log = logging.getLogger(__name__)

def makeSVSExchangeFormatFile(exportParams):
    """Generates a SVS export. If multiple time values are specified, the result will contain a WMS URL for each.
    """
    layerInfo = exportParams.layerInfoList[exportParams.animationLayerNumber - 1]

    # Make a set of parameters that excludes the dimension over which animation is to occur.
    baseParams = layerInfo.params.copy()
    if (exportParams.animationDimension != None) and (exportParams.animationDimension in baseParams):
        del baseParams[exportParams.animationDimension]

    baseUrl = wmc_util.parseEndpointString(layerInfo.endpoint, baseParams)

    # Create the export XML file.
    domImpl = xml.dom.minidom.getDOMImplementation()
    doc = domImpl.createDocument(None, "MovieExport", None)
    rootEl = doc.documentElement
    movieEl = doc.createElement("Movie")
    movieEl.setAttribute("framesPerSecond", exportParams.frameRate)
    rootEl.appendChild(movieEl)

    # Add a "wmsURL" for each dimension value.
    if exportParams.animationDimension == None:
        requestUrl = baseUrl
        xml_util.appendElement(doc, movieEl, "wmsURL", baseUrl)
    else:
        for val in exportParams.dimensionValues:
            requestUrl = baseUrl + "&" + urllib.urlencode({exportParams.animationDimension: val})
            log.debug("URL: %s" % (requestUrl));
            xml_util.appendElement(doc, movieEl, "wmsURL", requestUrl)

    # Include the outline URL.
    outlineLayerNumber = exportParams.getOutlineLayerNumber()
    if outlineLayerNumber != None:
        outlineInfo = exportParams.layerInfoList[outlineLayerNumber - 1]
        outlineUrl = wmc_util.parseEndpointString(outlineInfo.endpoint, outlineInfo.params)
        xml_util.appendElement(doc, movieEl, "outlineURL", outlineUrl)

    # Include the legend URL if included in the layer data.
    if layerInfo.legendURL != None:
        log.debug("legendURL %s" % (layerInfo.legendURL))
        xml_util.appendElement(doc, movieEl, "legendURL", layerInfo.legendURL);

    # Include the capabilities URL if included in the layer data.
    if layerInfo.capabilitiesURL != None:
        log.debug("capabilitiesURL %s" % (layerInfo.capabilitiesURL))
        xml_util.appendElement(doc, movieEl, "capabilitiesURL", layerInfo.capabilitiesURL)

    outFile = tempfile.NamedTemporaryFile(prefix=exportParams.fileNamePrefix, suffix=".xml", delete=False,
                                          dir=exportParams.exportDir)
    log.debug("File: %s" % (outFile.name))
    doc.writexml(outFile, addindent="  ", newl="\n", encoding="utf-8")
    outFile.close()

    return ExportResult(True, fileName = os.path.basename(outFile.name))
