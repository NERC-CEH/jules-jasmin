
import math
import urllib, urllib2, time
from cStringIO import StringIO
import logging

try:
    from PIL import Image
except:
    import Image

from ecomaps.lib.base import request
import ecomaps.lib.image_util as image_util
from ecomaps.lib.png_combine import merge
from ecomaps.lib.figure_builder import FigureBuilder
import ecomaps.lib.figure_parameters as figure_parameters
from ecomaps.lib.figure_parameters import LayerInfoBuilder
import ecomaps.lib.wmc_util as wmc_util

log = logging.getLogger(__name__)

try:
    from matplotlib.figure import Figure
    from matplotlib.ticker import FuncFormatter
    mplAvailable=True
except:
    log.info("importing matplotlib failed, not using matplotlib for figure generation")
    mplAvailable=False

def build_figure(requestParams, sessionEndpointData=None):
    """Generates a figure image for a set of layers defined though request parameters.
    @param requestParams: HTTP request parameters
    @param sessionEndpointData: data defining endpoints added during session
    """
    figureOptions = figure_parameters.FigureOptions(requestParams)
    commonLayerParams = figure_parameters.makeDefaultedParameters(requestParams, {})
    layerInfoBuilder = LayerInfoBuilder(requestParams, commonLayerParams)
    layerInfoList = layerInfoBuilder.buildInfo(sessionEndpointData)
    if len(layerInfoList) == 0:
        raise Exception("There are no layers to draw in the figure.")

    return buildFigureForLayers(requestParams, figureOptions, commonLayerParams, layerInfoList, None)

def buildFigureForLayers(requestParams, figureOptions, commonLayerParams, layerInfoList, imageCache):
    """Generates a figure image for a set of layers.
    @param requestParams: HTTP request parameters
    @param figureOptions: overall options for the figure
    @param commonLayerParams: parameters that apply to all layers
    @param layerInfoList: list of LayerInfo defining layers to include in the figure
    @param imageCache: cache of images that have been generated for layers (used for animations
           where dimensions only vary in the layer over which animation occurs)
    """
    if mplAvailable:
        finalImg, points = addAxisToImage(figureOptions, commonLayerParams, layerInfoList, imageCache)
        
        fb = FigureBuilder(requestParams, figureOptions, layerInfoList)
        finalImg  = fb.buildImage(finalImg, points)
    
    else:
        finalImg = buildImage(layerInfoList, imageCache)
    
    return finalImg

def buildImage(layerInfoList, imageCache):
    """Fetches and merges the figure images.
    @param layerInfoList: list of LayerInfo defining layers to include in the figure
    @param imageCache: cache of images that have been generated for layers (used for animations
           where dimensions only vary in the layer over which animation occurs)
    """
    images = []
    st = time.time()
    
    log.debug("Starting buildImage")
    
    size = None
    layerIndex = 0
    for layerInfo in layerInfoList:
        if imageCache == None or imageCache[layerIndex] == None:
            requestURL = wmc_util.parseEndpointString(layerInfo.endpoint, layerInfo.params)

            req = urllib2.Request(requestURL)
            req.add_header('Cookie', request.headers.get('Cookie', ''))

            filehandle = wmc_util.openURL(req)           
            imageString = StringIO(filehandle.read())
            img = Image.open(imageString)
            layerInfo.cachedImage = img
            if imageCache != None:
                imageCache[layerIndex] = img
        else:
            img = imageCache[layerIndex]

        images.append(img)
        size = img.size
        log.debug("img.size = %s, img.mode = %s" % (img.size, img.mode,))
        layerIndex = layerIndex + 1
    
    background = Image.new('RGBA', size, (255,255,255,255))

    log.debug("creating final image...")
    
    images.reverse()
    images.insert(0, background)
    finalImg = merge(*images)
    
    log.debug("finished buildImage in %s" % (time.time() - st,))
    
    return finalImg

    
def addAxisToImage(figureOptions, commonLayerParams, layerInfoList, imageCache):
    """Generates the main figure image with axes.
    @param figureOptions: overall options for the figure
    @param commonLayerParams: parameters that apply to all layers
    @param layerInfoList: list of LayerInfo defining layers to include in the figure
    @param imageCache: cache of images that have been generated for layers (used for animations
           where dimensions only vary in the layer over which animation occurs)
    """
    width = int(commonLayerParams.get('WIDTH'))
    height = int(commonLayerParams.get('HEIGHT'))
    log.debug("addAxisToImage %d x %d" % (width, height))
    dpi = 100;
    figsize=(width / float(dpi), height / float(dpi))
    # Figure has transparent background so that it can be the top layer, making the grid visible.
    facecolor = 'none' if figureOptions.grid else 'w'
    edgecolor = 'none' if figureOptions.grid else 'w'
    aspect = 'equal'
    transparent=False
    
    bounds = commonLayerParams['BBOX'].split(',')
    log.debug("bounds = %s" % (bounds,))
    lonLimits = (float(bounds[0]), float(bounds[2]))
    latLimits = (float(bounds[1]), float(bounds[3]))
    log.debug("lonLimits = %s, latLimits = %s" % (lonLimits, latLimits,))
    
    # create an empty image with the axes drawn
    fig = Figure(figsize=figsize, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor, frameon=(not transparent))

    # Add axes, allowing space for the axis legends and centering the map laterally within the figure.
    sideOffset = 95
    sideOffsetFraction = float(sideOffset) / float(width)
    bottomOffset = 50
    bottomOffsetFraction = float(bottomOffset) / float(height)
    bbox = [sideOffsetFraction, bottomOffsetFraction,
            (1 - 2 * sideOffsetFraction), (1 - 2 * bottomOffsetFraction)]
    log.debug("bbox %s" % bbox)

    axes = fig.add_axes(bbox, frameon=True)
    axes.patch.set_facecolor(facecolor)

    axes.set_aspect(aspect)
    log.debug("axes.get_position(original=False) = %s" % (axes.get_position(original=False),))

    axes.set_xlabel('Longitude')
    axes.set_ylabel('Latitude')
    
    axes.set_xlim(lonLimits)
    axes.set_ylim(latLimits)
     
    # Use tick values that are more suited to longitude and latitude if an appropriate set can be
    # found, otherwise use default ticks.
    xTicks = _getAxisTicksAtMultiplesOfBase(lonLimits, 15, 6, 9)
    if xTicks:
        axes.set_xticks(xTicks)
    yTicks = _getAxisTicksAtMultiplesOfBase(latLimits, 15, 4, 7)
    if yTicks:
        axes.set_yticks(yTicks)

    axes.xaxis.set_major_formatter(FuncFormatter(xMajorFormatter))
    axes.yaxis.set_major_formatter(FuncFormatter(yMajorFormatter))

    # Add grid.
    axes.grid(figureOptions.grid, linestyle='--')

    axesImage = image_util.figureToImage(fig)

    # Use the points to get the size of the new image.
    points = axes.get_position().get_points()    
    
    bottom = int(round(height * points[0][1]))
    left = int(round(width * points[0][0]))
    right = int(round(width * points[1][0]))
    top = int(round(height * points[1][1]))
    
    box = (left, bottom, right, top)

    # Calculate the new width & height.
    commonLayerParams['WIDTH'] = str(right-left)
    commonLayerParams['HEIGHT'] = str(top-bottom)
    
    log.debug("commonLayerParams['WIDTH'] = %s" % (commonLayerParams['WIDTH'],))
    log.debug("commonLayerParams['HEIGHT'] = %s" % (commonLayerParams['HEIGHT'],))

    # Apply the new size to the layer parameters.
    figure_parameters.updateLayerParameters(layerInfoList,
                                            {'WIDTH': commonLayerParams['WIDTH'], 'HEIGHT': commonLayerParams['HEIGHT']})
    
    # Request the new GetMap images.
    mapImage = buildImage(layerInfoList, imageCache)
    
    log.debug("axesImage.size = %s, mapImage.size = %s, box = %s" % (axesImage.size, mapImage.size, box,))

    if figureOptions.grid:
        # Build the combined image on a white, opaque background.
        size = axesImage.size
        combinedImage = Image.new('RGBA', size, (255, 255, 255, 255))

        # Note that the alpha channel in the images is ignored by paste - the image must be explicitly
        # set as a mask.
        combinedImage.paste(mapImage, box, mapImage)
        combinedImage.paste(axesImage, (0, 0, size[0], size[1]), axesImage)
    else:
        # No grid so map image can be pasted into axes.
        combinedImage = axesImage
        combinedImage.paste(mapImage, box, mapImage)
        
    return combinedImage, box

def _getAxisTicksAtMultiplesOfBase(limits, base, minTicks, maxTicks):
    """Sets axis ticks at values that are multiples of base if the limit values are also multiples
    of base, otherwise returns None. Also returns None if the resulting number of ticks would be
    less than minTicks or more than maxTicks. This is intended to be used for longitude and
    latitude, where it may be preferred to use tick values that are multiples of 15 or 30 degrees in
    preference to multiples of 10.
    """
    if minTicks < 2 or maxTicks < 2:
        return None
    (low, high) = limits

    interval = base
    mult = 1
    while low % interval == 0 and high % interval == 0:
        diff = high - low
        numIntervals = diff / interval
        if numIntervals + 1 < minTicks:
            return None
        if numIntervals + 1 <= maxTicks:
            return [float(x) * interval + low for x in xrange(numIntervals + 1)]
        mult += 1
        interval = base * mult
    return None

def _getAxisTicksAtPowerOfTwoMultiplesOfBase(limits, base, minTicks, maxTicks):
    """Sets axis ticks at values that are power-of-two multiples of base if the limit values are
    also multiples of base, otherwise returns None. Also returns None if the resulting number of
    ticks would be less than minTicks or more than maxTicks. This is intended to be used for
    longitude and latitude, where it may be preferred to use tick values that are multiples of 15 or
    30 degrees in preference to multiples of 10.
    """
    if minTicks < 2 or maxTicks < 2:
        return None
    (low, high) = limits

    interval = base
    while low % interval == 0 and high % interval == 0:
        diff = high - low
        numIntervals = diff / interval
        if numIntervals + 1 < minTicks:
            return None
        if numIntervals + 1 <= maxTicks:
            return [float(x) * interval + low for x in xrange(numIntervals + 1)]
        interval *= 2
    return None

TICK_LABEL_FORMAT = u"%s\u00b0%s"
def xMajorFormatter(val, i):
    if math.trunc(val) == val:
        valStr = int(abs(val)).__str__()
    else:
        valStr = abs(val).__str__()

    if val < 0:
        outStr = TICK_LABEL_FORMAT % (valStr, 'W')
    elif val > 0:
        outStr = TICK_LABEL_FORMAT % (valStr, 'E')
    else:
        outStr = TICK_LABEL_FORMAT % (valStr, '')
    return outStr

def yMajorFormatter(val, i):
    if math.trunc(val) == val:
        valStr = int(abs(val)).__str__()
    else:
        valStr = abs(val).__str__()

    if val < 0:
        outStr = TICK_LABEL_FORMAT % (valStr, 'S')
    elif val > 0:
        outStr = TICK_LABEL_FORMAT % (valStr, 'N')
    else:
        outStr = TICK_LABEL_FORMAT % (valStr, '')
    return outStr
