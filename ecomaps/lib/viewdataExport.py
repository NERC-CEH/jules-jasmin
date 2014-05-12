"""
Export generation including animations.

@author: rwilkinson
"""
import logging
import os, tempfile
from pylons import config
import ecomaps.lib.figure_parameters as figure_parameters
from ecomaps.lib.figure_parameters import LayerInfoBuilder
import ecomaps.lib.endpoint_hierarchy_builder as endpoint_hierarchy_builder
from ecomaps.lib.export_parameters import ExportParameters, ExportResult
import ecomaps.lib.kml_export as kml_export
import ecomaps.lib.svs_export as svs_export
import ecomaps.lib.video_export as video_export
import ecomaps.lib.wcs_export as wcs_export
import ecomaps.lib.wms_export as wms_export

log = logging.getLogger(__name__)

def make_export(params, applicationUrl, configuration, sessionEndpointData):
    """Generates an export of a type depending on the request parameters. Depending on whether
    multiple dimension values are specified, the result may be an animation or a static map.
    """
    # Process the parameters for the specified layers.
    figureOptions = figure_parameters.FigureOptions(params)
    commonLayerParams = figure_parameters.makeDefaultedParameters(params, {'WIDTH': 800, 'HEIGHT': 400})

    protocol = 'WCS' if params['animation-format'] == 'WCS' else 'WMS'
    layerInfoBuilder = LayerInfoBuilder(params, commonLayerParams, protocol)
    layerInfoList = layerInfoBuilder.buildInfo(sessionEndpointData)
    if len(layerInfoList) == 0:
        return ExportResult(False, errorMessage = "There are no layers to export.")

    exportParams = ExportParameters(params, figureOptions, commonLayerParams, layerInfoList, applicationUrl, configuration)

    # Check that the limit on the number of steps is not exceeded.

    # If there is a dimension to animate over, find the dimension values within the specified range.
    if exportParams.isAnimation():
        # Retrieve the WMC data for the layer.
        layerInfo = layerInfoList[exportParams.animationLayerNumber - 1]
        layerData = layerInfo.wmsLayer
        if layerData == None:
            return ExportResult(False, errorMessage = "Information about requested layers no longer held. Please refresh your browser.")

        # Find the set of dimension values corresponding to the specified name.
        dimension = None
        for dim in layerData.dimensions:
            if dim['name'].upper() == exportParams.animationDimension:
                dimension = dim
                break
        if dimension == None:
            return ExportResult(False, errorMessage = "Information about requested layers no longer held. Please refresh your browser.")

        # Find the values for the dimension that is to vary in the animation within the required range.
        try:
            dimValueSet = findDimensionRange(dimension['dimensionValues'], exportParams.startValue,
                                             exportParams.endValue, exportParams.numberSteps)
        except ValueError, exc:
            return ExportResult(False, errorMessage = exc.__str__())

        exportParams.setDimensionValues(dimValueSet)

    # Find and create if necessary the directory for the export file.
    exportDir = getExportDir()
    if (exportDir != None) and (not os.path.exists(exportDir)):
        os.makedirs(exportDir)
    exportParams.setExportDir(exportDir)

    return {
        'AVI_MJPEG': video_export.makeVideo,
        'FLV': video_export.makeVideo,
        'MOV': video_export.makeVideo,
        'MPEG2': video_export.makeVideo,
        'KML': kml_export.makeKmlFile,
        'SVSX': svs_export.makeSVSExchangeFormatFile,
        'WMS': wms_export.makeWmsDetailsFile,
        'WCS': wcs_export.makeWcsExportFile
        }.get(exportParams.formatName, invalidFormat)(exportParams)

def invalidFormat(exportParams):
    log.error("Invalid format %s requested" % exportParams.formatName)
    return ExportResult(False, errorMessage = ("Invalid format: %s" % exportParams.formatName))

def getExportDir():
    return config.get('export_file_dir', tempfile.gettempdir())

def findDimensionRange(dimensionValues, startValue, endValue, numberSteps):
    """Find the dimension values in the set specified by the start and end values with the specified
    number of steps.
    """
    dimValueSet = []
    startIndex = None
    endIndex = None
    idx = 0
    for val in dimensionValues:
        if val == startValue:
            startIndex = idx
        if val == endValue:
            endIndex = idx
        idx += 1

    if startIndex is None or endIndex is None:
        raise ValueError("Start or end value is not in the set of valid dimension values for this layer.")

    log.debug("Dimension indices %d to %d" % (startIndex, endIndex))

    if numberSteps > 1:
        for i in xrange(numberSteps):
            idx = int(round(float(endIndex - startIndex) / (numberSteps - 1) * i + startIndex))
            dimValueSet.append(dimensionValues[idx])
    else:
        dimValueSet.append(dimensionValues[0])

    for val in dimValueSet:
        log.debug("Dimension value: %s" % (val))

    return dimValueSet
