"""
Creates the metadata caption for figures in the style used by Viewdata.
Based on code originally in figure_builder.

@author rwilkinson
"""
import logging
import time
from cStringIO import StringIO
try:
    from PIL import Image
except:
    import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_cairo import FigureCanvasCairo as FigureCanvas
from matplotlib.backends.backend_cairo import RendererCairo as Renderer
from matplotlib.transforms import Bbox
from matplotlib.patches import Rectangle

import ecomaps.lib.caption_manager as caption_manager
import ecomaps.lib.image_util as image_util
import ecomaps.lib.outline_layer as outline_layer
import ecomaps.lib.user_interface_config as user_interface_config

log = logging.getLogger(__name__)

metadataFont = {'weight':'normal',
                'family':'sans-serif',
                'size':'12'}

titleFont = {'weight':'normal',
             'family':'sans-serif',
             'size':'16'}
        
class IpccDdcMetadataImageBuilder(object):
    def __init__(self, params):
        self.params = params

    def getFigureSpacings(self):
        """Returns the vertical spaces between the components of a figure.
        """
        return (0, 0, 0)

    def buildMetadataImage(self, layerInfoList, width):
        """
        Creates the metadata caption for figures in styles that display a title only.
        """
        # Find first non-outline layer.
        nonOutlineLayers = [l for l in layerInfoList if l.id != outline_layer.OUTLINE_LAYER_ID]
        layerInfo = nonOutlineLayers[0] if len(nonOutlineLayers) > 0 else None

        # Get the title of the first set of keyword data, i.e., that for the layer rather than one
        # of its antecedent layers or datasets.
        titleText = ''
        if layerInfo and (len(layerInfo.keywordData) > 0):
            titleText = layerInfo.keywordData[0].get('title', '')

        height = 500
        dpi = 100
        transparent = False

        figsize = (width / float(dpi), height / float(dpi))
        fig = Figure(figsize=figsize, dpi=dpi, facecolor='w', frameon=(not transparent))
        renderer = Renderer(fig.dpi)

        text = fig.text(0.5, 0.98, titleText,
                        fontdict=titleFont,
                        horizontalalignment='center',
                        verticalalignment='top')

        # Trim the height of the text image.
        extent = text.get_window_extent(renderer)
        textHeight = (extent.y1 - extent.y0 + 8)
        fig.set_figheight(textHeight / float(dpi))
        
        return image_util.figureToImage(fig)
    
    def buildDetailsImage(self, layerInfoList, width):
        """
        Creates the metadata details for figures using templates.
        """
        # Find first non-outline layer.
        nonOutlineLayers = [l for l in layerInfoList if l.id != outline_layer.OUTLINE_LAYER_ID]
        layerInfo = nonOutlineLayers[0] if len(nonOutlineLayers) > 0 else None

        # Flatten the keyword dictionaries, giving priority to entries from descendants over
        # antecedents.
        keywordData = {}
        if layerInfo:
            for kw in reversed(layerInfo.keywordData):
                keywordData.update(kw)

        detailsText = caption_manager.getCaption(layerInfo, keywordData)

        height = 500
        dpi = 100
        transparent = False

        figsize = (width / float(dpi), height / float(dpi))
        fig = Figure(figsize=figsize, dpi=dpi, facecolor='w', frameon=(not transparent))
        renderer = Renderer(fig.dpi)

        text = fig.text(0.02, 0.98, detailsText,
                        fontdict=metadataFont,
                        horizontalalignment='left',
                        verticalalignment='top')

        # Trim the height of the text image.
        extent = text.get_window_extent(renderer)
        textHeight = (extent.y1 - extent.y0 + 8)
        fig.set_figheight(textHeight / float(dpi))
        
        return image_util.figureToImage(fig)
