"""
Creates the metadata caption for figures in the style used by WMSViz.
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
from pylons import config

import ecomaps.lib.image_util as image_util

log = logging.getLogger(__name__)

metadataFont = {'weight':'normal',
                'family':'sans-serif',
                'size':'12'}

titleFont = {'weight':'normal',
             'family':'sans-serif',
             'size':'16'}
        
borderColor = 'grey'
        
class WmsvizMetadataImageBuilder(object):
    def __init__(self, params):
        pass

    def getFigureSpacings(self):
        """Returns the vertical spaces between the components of a figure.
        """
        return (30, 0, 0)
    
    def buildMetadataImage(self, layerInfoList, width):
        """
        Creates the metadata caption for figures in the style used by WMSViz.
        """
        self.metadataItems = self._buildMetadataItems(layerInfoList)
        self.width = width
        
        width=self.width;height=1600;dpi=100;transparent=False
        figsize=(width / float(dpi), height / float(dpi))
        fig = Figure(figsize=figsize, dpi=dpi, facecolor='w', frameon=(not transparent))
        axes = fig.add_axes([0.04, 0.04, 0.92, 0.92],  frameon=True,xticks=[], yticks=[])
        renderer = Renderer(fig.dpi)


        title, titleHeight = self._drawTitleToAxes(axes, renderer)
        
        txt, textHeight = self._drawMetadataTextToAxes(axes, renderer, self.metadataItems)

        # fit the axis round the text

        pos = axes.get_position()
        newpos = Bbox( [[pos.x0,  pos.y1 - (titleHeight + textHeight) / height], [pos.x1, pos.y1]] )
        axes.set_position(newpos )

        # position the text below the title

        newAxisHeight = (newpos.y1 - newpos.y0) * height
        txt.set_position( (0.02, 0.98 - (titleHeight/newAxisHeight) ))

        for loc, spine in axes.spines.iteritems():
            spine.set_edgecolor(borderColor)
        
        # Draw heading box
        
        headingBoxHeight = titleHeight - 1
        
        axes.add_patch(Rectangle((0, 1.0 - (headingBoxHeight/newAxisHeight)), 1, (headingBoxHeight/newAxisHeight),
                       facecolor=borderColor,
                      fill = True,
                      linewidth=0))

        # reduce the figure height
        
        originalHeight = fig.get_figheight()
        pos = axes.get_position()
        topBound = 20 / float(dpi)
        
        textHeight = (pos.y1 - pos.y0) * originalHeight
        
        newHeight = topBound * 2 + textHeight
        
        # work out the new proportions for the figure
        
        border = topBound / float(newHeight)
        newpos = Bbox( [[pos.x0,  border], [pos.x1, 1 - border]] )
        axes.set_position(newpos )
        
        fig.set_figheight(newHeight)
        
        return image_util.figureToImage(fig)
    
    def _drawMetadataTextToAxes(self, axes, renderer, metadataItems):
        '''
        Draws the metadata text to the axes
        
        @param axes: the axes to draw the text on
        @type axes: matplotlib.axes.Axes
        @param renderer: the matplotlib renderer to evaluate the text size
        @param metadataItems: a list of metadata items to get the text form
        
        @return: the text object, the total metadata text height in pixels
        '''
        
        lines = self.metadataItems
        text = '\n'.join(lines)
        txt = axes.text(0.02, 0.98 ,text,
                fontdict=metadataFont,
                horizontalalignment='left',
                verticalalignment='top',)

        extent = txt.get_window_extent(renderer)
        
        textHeight = (extent.y1 - extent.y0 + 10)
        return txt, textHeight        

    def _drawTitleToAxes(self, axes, renderer):
        '''
        Draws the metadata tile text onto the axes
        
        @return: the text object, the height of the title text in pixels
        '''
        
        titleText = self._getTitleText()

        title = axes.text(0.02,0.98,titleText,
                fontdict=titleFont,
                horizontalalignment='left',
                verticalalignment='top',)

        extent = title.get_window_extent(renderer)
        titleHeight = (extent.y1 - extent.y0 + 8)
        return title, titleHeight        

    def _getTitleText(self):
        
        titleText = "Plot Metadata:"
        additionalText = config.get('additional_figure_text', '')
        
        if additionalText != "":
        
            if additionalText.find('<date>') > 0:
                timeString = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                additionalText = additionalText.replace("<date>", timeString)
            
            titleText += " %s" % (additionalText,)
        
        return titleText

    def _buildMetadataItems(self, layerInfoList):
        items = []
        
        for i in range(len(layerInfoList)):
            li = layerInfoList[i]
            j = i + 1
            items.append("%s:endpoint = %s layerName = %s" % (j, li.endpoint, li.layerName))
            items.append("%s:params = %s" % (j, li.params))
                
        return items
