"""
KML export.

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

def makeKmlFile(exportParams):
    """Generates a KML export. If multiple dimension values are specified, the result will contain an overlay for each.
    """
    layerInfo = exportParams.layerInfoList[exportParams.animationLayerNumber - 1]

    # Make a set of parameters that excludes the dimension over which animation is to occur.
    baseParams = layerInfo.params.copy()

    # Determine if animation over multiple values is to occur.
    do_animation = ((exportParams.animationDimension != None) and
        (exportParams.dimensionValues != None) and (len(exportParams.dimensionValues) > 1))

    if do_animation and (exportParams.animationDimension in baseParams):
        del baseParams[exportParams.animationDimension]

    # Get the bounding box values [W, S, E, N].
    bounds = exportParams.commonLayerParams['BBOX'].split(',')

    baseUrl = wmc_util.parseEndpointString(layerInfo.endpoint, baseParams)

    # Create the export XML file.
    domImpl = xml.dom.minidom.getDOMImplementation()
    doc = domImpl.createDocument("http://earth.google.com/kml/2.2", "kml", None)
    rootEl = doc.documentElement

    folderEl = doc.createElement("Folder")
    rootEl.appendChild(folderEl)
    xml_util.appendElement(doc, folderEl, "name", layerInfo.layerName)
    xml_util.appendElement(doc, folderEl, "open", "1")

    # Add a "wmsURL" for each dimension value.
    layerIndex = 0
    if do_animation:
        itr = iter(exportParams.dimensionValues)
        val = itr.next()
        for nextVal in itr:
            makeKmlGroundOverlayFile(doc, folderEl, layerInfo.layerName, baseUrl, exportParams.animationDimension,
                                     val, val, nextVal, bounds, layerIndex)
            val = nextVal
            layerIndex += 1
        makeKmlGroundOverlayFile(doc, folderEl, layerInfo.layerName, baseUrl, exportParams.animationDimension,
                                 val, val, None, bounds, layerIndex)
    else:
        makeKmlGroundOverlayFile(doc, folderEl, layerInfo.layerName, baseUrl, None, None, None, None, bounds, layerIndex)

    outFile = tempfile.NamedTemporaryFile(prefix=exportParams.fileNamePrefix, suffix=".kml", delete=False, dir=exportParams.exportDir)
    log.debug("File: %s" % (outFile.name))
    doc.writexml(outFile, addindent="  ", newl="\n", encoding="utf-8")
    outFile.close()

    return ExportResult(True, fileName = os.path.basename(outFile.name))

def makeKmlGroundOverlayFile(doc, parentEl, name, baseUrl, animationDimension, dimensionValue, begin, end, bounds, layerIndex):
    """Adds a GroundOverlay element for the specified dimension value.
    """
    isTimeAnimation = (animationDimension != None and animationDimension.lower() == "time")
    goEl = doc.createElement("GroundOverlay")
    parentEl.appendChild(goEl)
    xml_util.appendElement(doc, goEl, "name", (dimensionValue if dimensionValue != None else name))
    # If animating over time, make all layers visible since only one applies at a given time, otherwise just the first layer.
    xml_util.appendElement(doc, goEl, "visibility", ("1" if (isTimeAnimation or (layerIndex == 0)) else "0"))

    # Include time span if data supplied.
    if isTimeAnimation and (begin != None or end != None):
        tsEl = doc.createElement("TimeSpan")
        goEl.appendChild(tsEl)
        if begin != None:
            xml_util.appendElement(doc, tsEl, "begin", begin)
        if end != None:
            xml_util.appendElement(doc, tsEl, "end", end)

    # Include the URL for the image.
    if animationDimension == None:
        requestUrl = baseUrl
    else:
        requestUrl = baseUrl + "&" + urllib.urlencode({animationDimension: dimensionValue})
    iconEl = doc.createElement("Icon")
    goEl.appendChild(iconEl)
    xml_util.appendElement(doc, iconEl, "href", requestUrl)
    xml_util.appendElement(doc, iconEl, "refreshMode", "onExpire")

    # Add the bounding box.
    llEl = doc.createElement("LatLonBox")
    goEl.appendChild(llEl)

    xml_util.appendElement(doc, llEl, "north", bounds[3])
    xml_util.appendElement(doc, llEl, "south", bounds[1])
    xml_util.appendElement(doc, llEl, "east", bounds[2])
    xml_util.appendElement(doc, llEl, "west", bounds[0])
