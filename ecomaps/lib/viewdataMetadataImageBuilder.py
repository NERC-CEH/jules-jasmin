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
import ecomaps.lib.image_util as image_util
import ecomaps.lib.user_interface_config as user_interface_config

log = logging.getLogger(__name__)

metadataFont = {'weight':'normal',
                'family':'sans-serif',
                'size':'12'}

titleFont = {'weight':'normal',
             'family':'sans-serif',
             'size':'16'}
        
borderColor = 'grey'
        
class ViewdataMetadataImageBuilder(object):
    def __init__(self, params):
        self.params = params

    def getFigureSpacings(self):
        """Returns the vertical spaces between the components of a figure.
        """
        return (30, 0, 0)
    
    def buildMetadataImage(self, layerInfoList, width):
        """
        Creates the metadata caption for figures in the style used by Viewdata.
        """
        metadataItems = self._buildMetadataItems(layerInfoList)
        height = 1600
        dpi = 100
        transparent = False

        figsize = (width / float(dpi), height / float(dpi))
        fig = Figure(figsize=figsize, dpi=dpi, facecolor='w', frameon=(not transparent))
        axes = fig.add_axes([0.04, 0.04, 0.92, 0.92],  frameon=True, xticks=[], yticks=[])
        renderer = Renderer(fig.dpi)


        title, titleHeight = self._drawTitleToAxes(axes, renderer, layerInfoList)
        
        txt, textHeight = self._drawMetadataTextToAxes(axes, renderer, metadataItems)

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
        
        lines = metadataItems
        text = '\n'.join(lines)
        txt = axes.text(0.02, 0.98 ,text,
                fontdict=metadataFont,
                horizontalalignment='left',
                verticalalignment='top',)

        extent = txt.get_window_extent(renderer)
        
        textHeight = (extent.y1 - extent.y0 + 10)
        return txt, textHeight        

    def _drawTitleToAxes(self, axes, renderer, layerInfoList):
        '''
        Draws the metadata tile text onto the axes
        
        @return: the text object, the height of the title text in pixels
        '''
        
        titleText = self._getTitleText(layerInfoList)

        title = axes.text(0.02,0.98,titleText,
                fontdict=titleFont,
                horizontalalignment='left',
                verticalalignment='top',)

        extent = title.get_window_extent(renderer)
        titleHeight = (extent.y1 - extent.y0 + 8)
        return title, titleHeight        

    def _getTitleText(self, layerInfoList):
        
        if 'animation-layer-number' in self.params:
            titleText = user_interface_config.getCustomTextOption('animationtitle')
        else:
            titleText = user_interface_config.getCustomTextOption('figuretitle')

        if titleText != "":
            for k, v in self._getTitleItems(layerInfoList).items():
                token = "<" + k + ">"
                log.debug("Replacing %s -> %s" % (token, v))
                if titleText.find(token) > 0:
                    titleText = titleText.replace(token, v)

        return titleText

    def _getTitleItems(self, layerInfoList):
        """
        """
        items = {}
        
        items['animationdimension'] = self.params.get('animation-dimension', '')
        if 'animation-layer-number' in self.params:
            try:
                li = int(self.params['animation-layer-number']) - 1
                layerInfo = layerInfoList[li]
                items['animationlayer'] = layerInfo.layerName
            except:
                items['animationlayer'] = ''

        items['date'] = time.strftime("%Y-%m-%d", time.localtime())
        items['datetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        return items

    def _buildMetadataItems(self, layerInfoList):
        items = []
        
        if 'figure-legend-show-bounding-box' in self.params and 'BBOX' in self.params:
            items.append("Bounding box: %s" % (self.params['BBOX']))

        for i in range(len(layerInfoList)):
            li = layerInfoList[i]
            layerNumber = i + 1
            prefixText = "Layer %s: " % (layerNumber);
            if 'figure-legend-show-layer-names' in self.params:
                items.append("%s%s (%s)" % (prefixText, li.layerName, li.endpoint))
                prefixText = "    "
            details = []
            if 'figure-legend-show-style-names' in self.params and 'STYLES' in li.params:
                details.append("Style: %s" % (li.params['STYLES']))
            if 'figure-legend-show-dimensions' in self.params and li.dimensionNames != None:
                # Split comma separated list and add information for each dimension.
                dimDetails = []
                for dim in li.dimensionNames:
                    dimKey = dim.upper()
                    if dimKey in li.params:
                        dimDetails.append("%s=%s" % (dim, li.params[dimKey]))
                if len(dimDetails) > 0:
                    details.append("Dimension%s:" % ("s" if len(dimDetails) > 0 else ""))
                    details.extend(dimDetails);
            if len(details) > 0:
                items.append(prefixText + "  ".join(details))
                
        return items
