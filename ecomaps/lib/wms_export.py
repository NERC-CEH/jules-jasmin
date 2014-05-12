"""
WMS details export.

@author: rwilkinson
"""
import logging
import os, tempfile
import urllib
import xml.dom.minidom
from ecomaps.lib.export_parameters import ExportResult
import ecomaps.lib.wmc_util as wmc_util
import ecomaps.lib.xml_util as xml_util

log = logging.getLogger(__name__)

def makeWmsDetailsFile(exportParams):
    """Generates a WMS export containing the URLs for the map, capabilities and legend for the current map.
    """

    # Create the export XML file.
    domImpl = xml.dom.minidom.getDOMImplementation()
    doc = domImpl.createDocument(None, "WmsDetails", None)
    rootEl = doc.documentElement

    # Construct a WMS GetMap URL for each layer.
    layerNumber = 1
    for layerInfo in exportParams.layerInfoList:
        wmsURL = wmc_util.parseEndpointString(layerInfo.endpoint, layerInfo.params)
        wmsUrlEl = doc.createElement("wmsURL")
        wmsUrlEl.setAttribute("layer", layerNumber.__str__())
        wmsUrlTextEl = doc.createTextNode(wmsURL)
        wmsUrlEl.appendChild(wmsUrlTextEl)
        rootEl.appendChild(wmsUrlEl)
        layerNumber += 1

    # Include the legend URL if included in the layer data.
    layerInfo = exportParams.layerInfoList[exportParams.animationLayerNumber - 1]
    if layerInfo.legendURL != None:
        log.debug("legendURL %s" % (layerInfo.legendURL))
        xml_util.appendElement(doc, rootEl, "legendURL", layerInfo.legendURL);

    outFile = tempfile.NamedTemporaryFile(prefix=exportParams.fileNamePrefix, suffix=".xml", delete=False,
                                          dir=exportParams.exportDir)
    log.debug("File: %s" % (outFile.name))
    doc.writexml(outFile, addindent="  ", newl="\n", encoding="utf-8")
    outFile.close()

    return ExportResult(True, fileName = os.path.basename(outFile.name))
