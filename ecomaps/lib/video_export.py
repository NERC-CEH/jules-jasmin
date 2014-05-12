"""
Video export.

@author: rwilkinson
"""
import logging
import copy
import os, shutil, tempfile
from pylons import config
import ecomaps.lib.build_figure as build_figure
from ecomaps.lib.export_parameters import ExportResult
import ecomaps.lib.wmc_util as wmc_util

log = logging.getLogger(__name__)

def makeVideo(exportParams):
    """Generates a video export.
    Creates an image for each frame then combines this into a video according to the format specified.
    """
    # Check that the number of steps is within range.
    maxNumberSteps = int(exportParams.configuration['maxnumbersteps'])
    log.debug("Number steps %d  max %d" % (exportParams.numberSteps, maxNumberSteps))
    if exportParams.numberSteps > maxNumberSteps:
        return ExportResult(False,
                            errorMessage = ('The number of steps for a video cannot exceed %d' % maxNumberSteps))

    layerInfo = exportParams.layerInfoList[exportParams.animationLayerNumber - 1]

    animationLayerParams = layerInfo.params
    if (exportParams.animationDimension != None) and (exportParams.animationDimension in animationLayerParams):
        del animationLayerParams[exportParams.animationDimension]

    imageDir = tempfile.mkdtemp(prefix="viewdataVideoExport", suffix="", dir=exportParams.exportDir)

    # Create an image for each dimension value.
    imageIndex = 0
    if exportParams.animationDimension == None:
        createImage(exportParams.params, exportParams.figureOptions, exportParams.commonLayerParams,
                    exportParams.layerInfoList, imageDir, imageIndex, None)
    else:
        # Initialise a list of cached images to be used for layers that don't change between steps.
        imageCache = [None] * len(exportParams.layerInfoList)
        for val in exportParams.dimensionValues:
            # Clear the cached image for the layer that is being animated.
            imageCache[exportParams.animationLayerNumber - 1] = None
            # Set the current value of the animated dimension.
            animationLayerParams[exportParams.animationDimension] = val
            # Update the legend URL with the animated dimension value.
            animationLayerLegendUrl = layerInfo.legendURL
            layerInfo.legendURL = wmc_util.parseEndpointString(animationLayerLegendUrl, {exportParams.animationDimension: val})

            # Create the image file for this value.
            createImage(exportParams.params, exportParams.figureOptions, exportParams.commonLayerParams,
                        exportParams.layerInfoList, imageDir, imageIndex, imageCache)
            imageIndex = imageIndex + 1

    # Create the video from the individual images.
    try:
        outFilePath = createVideo(exportParams.formatName, exportParams.frameRate, imageDir, exportParams.exportDir,
                                  exportParams.fileNamePrefix)
    except Exception, err:
        log.error("Exception creating video: %s" % err)
        outFilePath = None

    # Remove the image directory, ignoring errors.
    shutil.rmtree(imageDir, True)

    if outFilePath == None:
        return ExportResult(False, errorMessage = 'Video creation failed')
    else:
        return ExportResult(True, fileName = os.path.basename(outFilePath))

def createImage(requestParams, figureOptions, commonLayerParams, layerInfoList, imageDir, imageIndex, imageCache):
    """Creates a PNG image forming one frame of the video.
    """
    outFileName = "image_%05d.png" % (imageIndex)
    outPath = os.path.join(imageDir, outFileName)
    log.debug("Creating image file: %s", outPath);

    img = build_figure.buildFigureForLayers(requestParams, figureOptions, commonLayerParams.copy(),
                                            copy.deepcopy(layerInfoList), imageCache)

    img.save(outPath, 'PNG')

def createVideo(formatName, frameRate, imageDir, exportDir, fileNamePrefix):
    """Combine the image into a video.
    """
    framesPerSecond = (float(frameRate) if frameRate != None else None)
    fileNameTemplate = "image_%05d.png"
    filePathTemplate = os.path.join(imageDir, fileNameTemplate)
    reserveFileSuffix = ".rsrv"

    # FFmpeg doesn't allow framerates below 20fps for MPEG-2. It will modify other values to one valid for the format.
    if formatName == "MPEG2" and framesPerSecond < 20:
        framesPerSecond = 20

    # Find the command template for converting to the specified format.
    formats = {
        "AVI_MJPEG": {'template': "%(converter)s -r %(framesPerSecond)g -i %(filePathTemplate)s -f avi -vcodec mjpeg -sameq '%(outFilePath)s'",
                      'converter': "ffmpeg",
                      'suffix': '.avi'},
        "FLV": {'template': "%(converter)s -r %(framesPerSecond)g -i %(filePathTemplate)s -f flv -sameq '%(outFilePath)s'",
                'converter': "ffmpeg",
                'suffix': '.flv'},
        "MOV": {'template': "%(converter)s -r %(framesPerSecond)g -i %(filePathTemplate)s -f mov -sameq '%(outFilePath)s'",
                'converter': "ffmpeg",
                'suffix': '.mov'},
        "MPEG2": {'template': "%(converter)s -r %(framesPerSecond)g -i %(filePathTemplate)s -f mpeg2video -vcodec mpeg2video -sameq '%(outFilePath)s'",
                  'converter': "ffmpeg",
                  'suffix': '.mpeg'}
        }
    if formatName in formats:
        fmt = formats[formatName]
        commandTemplate = fmt['template']
        converter = fmt['converter']
        outFileSuffix = fmt['suffix']
    else:
        return None
    log.debug("Video converter: %s" % converter)
    converterExe = config.get('video.converter.' + converter, converter)
    log.debug("Video converter program: %s" % converterExe)

    # Create a file of unique name for the output.
    reserveFile = tempfile.NamedTemporaryFile(prefix=fileNamePrefix, suffix=reserveFileSuffix, delete=False, dir=exportDir)
    reserveFile.close()
    outFilePath = reserveFile.name[:-len(reserveFileSuffix)] + outFileSuffix
    log.debug("File: %s" % (outFilePath))

    # Run the external executable to create the video file.
    command = commandTemplate % {'converter': converterExe, 'framesPerSecond': framesPerSecond, 'filePathTemplate': filePathTemplate, 'outFilePath': outFilePath}
    log.debug('Running command "%s"', command)
    rc = os.system(command)
    log.debug("Video creation process return code: %x", rc)

    # Check that a file was created.
    if not os.path.exists(outFilePath):
        return None

    return outFilePath
