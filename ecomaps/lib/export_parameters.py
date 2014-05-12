"""
Classes for parameters for exports and the results.

@author: rwilkinson
"""
import logging
import re
import ecomaps.lib.outline_layer as outline_layer

log = logging.getLogger(__name__)

class ExportParameters:
    """Processes and holds the parameters for an export.
    """
    def __init__(self, params, figureOptions, commonLayerParams, layerInfoList, applicationUrl, configuration):
        self.params = params
        self.figureOptions = figureOptions
        self.formatName = params.get('animation-format', 'SVSX')
        fileNamePrefixIn = params.get('animation-prefix', '')
        self.fileNamePrefix = self.makeSafeFileName(fileNamePrefixIn, 20)
        if self.fileNamePrefix == '':
            self.fileNamePrefix = 'viewdataExport'
        else:
            self.fileNamePrefix = self.fileNamePrefix + '-'
        self.startValue = params.get('animation-start', None)
        self.endValue = params.get('animation-end', None)
        self.numberSteps = int(params.get('animation-number-steps', '1'))
        self.frameRate = params.get('animation-framerate', None)
        animationLayerNumberStr = params.get('animation-layer-number', None)
        self.animationLayerNumber = (int(animationLayerNumberStr) if animationLayerNumberStr != None else None)
        animationDimensionIn = params.get('animation-dimension', None)
        self.animationDimension = (animationDimensionIn.upper() if animationDimensionIn != None else None)

        self.commonLayerParams = commonLayerParams
        self.layerInfoList = layerInfoList
        self.dimensionValues = None
        self.applicationUrl = applicationUrl
        self.configuration = configuration

        # If lower layers are being suppressed from exports, the selected layer may be one of the
        # suppressed layers.
        if self.animationLayerNumber > len(layerInfoList):
            self.animationLayerNumber = None
            self.animationDimension = None

        # Select the top, non-outline layer if none is specified (or the outline layer if there is no other).
        if self.animationLayerNumber == None:
            self.animationLayerNumber = self.getTopNonOutlineLayerNumber()
            if self.animationLayerNumber == None:
                self.animationLayerNumber = 1 if len(layerInfoList) > 0 else None

        # Find the layer ID for the animation layer.
        if self.animationLayerNumber is not None:
            animationLayerInfo = layerInfoList[self.animationLayerNumber - 1]
            self.animationLayerId = animationLayerInfo.id
            log.debug("Export layer ID %s" % (self.animationLayerId))
            log.debug("Export dimension %s" % (self.animationDimension))
            log.debug("Export endpoint %s" % (animationLayerInfo.endpoint))
        else:
            log.debug("No animation layer")


    def setDimensionValues(self, dimensionValues):
        self.dimensionValues = dimensionValues

    def setExportDir(self, exportDir):
        self.exportDir = exportDir

    def isAnimation(self):
        return (self.animationDimension != None)

    def getOutlineLayerNumber(self):
        layerNumber = 1
        for layer in self.layerInfoList:
            if layer.id == outline_layer.OUTLINE_LAYER_ID:
                return layerNumber
            layerNumber += 1
        return None

    def getTopNonOutlineLayerNumber(self):
        layerNumber = 1
        for layer in self.layerInfoList:
            if layer.id != outline_layer.OUTLINE_LAYER_ID:
                return layerNumber
            layerNumber += 1
        return None

    @staticmethod
    def makeSafeFileName(filename, maxLen):
        """Makes a filename containing only a restricted set of characters that are
        safe on all(?) file systems and to pass in HTTP headers.
        """
        return str(re.sub('[^a-zA-Z0-9_-]', '', filename)[:maxLen])

class ExportResult:
    """Holds the results of an export.
    """
    def __init__(self, success, fileName = None, errorMessage = None):
        self.success = success
        self.fileName = fileName
        self.errorMessage = errorMessage
