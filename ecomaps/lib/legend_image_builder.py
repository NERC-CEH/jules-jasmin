"""
Creates the legend image for a figure, possibly combining the legends for a number of layers.
Based on code originally in figure_builder.

@author rwilkinson
"""
import urllib2
import logging
import pkg_resources

try:
    from PIL import Image
except:
    import Image

from ecomaps.lib.base import request
from ecomaps.lib.wmc_util import openURL

from cStringIO import StringIO

log = logging.getLogger(__name__)

from pylons import config

class LegendImageBuilder(object):

    def __init__(self):

        self.topBorder = 2
        self.sideBorder = 10
        self.verticalOffset = 5

        self.omitLabelForSingleLegend = (config.get('omit_label_for_single_legend', 'false').lower() == 'true')
        log.debug('Omitting label for figure legend if only one legend' if self.omitLabelForSingleLegend
                  else 'Including label for figure legend even if only one legend')

        imageFolder = config.get('image_folder', None)
        if imageFolder:
            self.externalImages = True
            imagePath = imageFolder + "/"
        else:
            self.externalImages = False
            imagePath = ""

        self.legendLabels = {
            1  : imagePath + "one.png",
            2  : imagePath + "two.png",
            3  : imagePath + "three.png",
            4  : imagePath + "four.png",
            5  : imagePath + "five.png",
            6  : imagePath + "six.png",
            7  : imagePath + "seven.png",
            8  : imagePath + "eight.png",
            9  : imagePath + "nine.png",
            10 : imagePath + "ten.png",
        }


    def buildLegendImage(self, infoList, width):

        legendImages = self._getLegendImages(infoList)

        height = self._calculateHeight(legendImages)

        combinedImage = Image.new('RGBA', (width, height), (255,255,255,255))

        self._pasteImages(combinedImage, legendImages)

        return combinedImage


    def _pasteImages(self, combinedImage, legendImages):

        top = self.topBorder

        if self.omitLabelForSingleLegend and (len(legendImages) == 1):
            for labelImage, legendImage in legendImages:

                legendDownShift = 0

                totalWidth = legendImage.size[0] + (self.sideBorder * 2)
                rightShift = self._getRightShift(totalWidth, combinedImage.size[0])

                log.debug("legendDownShift = %s, rightShift = %s" % (legendDownShift, rightShift,))

                combinedImage.paste(legendImage, (rightShift + self.sideBorder, top + legendDownShift))

                legHeight = legendImage.size[1]
                top += (legHeight + self.verticalOffset)

        else:
            for labelImage, legendImage in legendImages:

                labelDownShift = 0
                legendDownShift = 0

                if labelImage.size[1] > legendImage.size[1]:
                    legendDownShift = self._getDownShift(legendImage.size[1], labelImage.size[1])
                else:
                    labelDownShift = self._getDownShift(labelImage.size[1], legendImage.size[1])

                totalWidth = labelImage.size[0] + legendImage.size[0] + (self.sideBorder * 3)
                rightShift = self._getRightShift(totalWidth, combinedImage.size[0])

                log.debug("legendDownShift = %s, labelDownShift = %s, rightShift = %s" %
                          (legendDownShift, labelDownShift, rightShift,))

                combinedImage.paste(labelImage, (self.sideBorder + rightShift, top + labelDownShift))
                combinedImage.paste(legendImage, (rightShift + (self.sideBorder * 2) + labelImage.size[0], top + legendDownShift))

                legHeight = max([labelImage.size[1], legendImage.size[1]])
                top += (legHeight + self.verticalOffset)

    def _getDownShift(self, shortHeight, tallHeight):

        return int( (tallHeight - shortHeight ) / 2.0 )

    def _getRightShift(self, smallWidth, wideWidth):
        return int( (wideWidth - smallWidth) / 2.0 )


    def _calculateHeight(self, legendImages):
        if len(legendImages) == 0:
            return 0

        height = 2 * self.topBorder + (len(legendImages) - 1) * self.verticalOffset

        for labelImage, legendImage in legendImages:
            height += max([labelImage.size[1], legendImage.size[1]])

        return height


    def _getLegendImages(self, infoList):

        legendImages = []
        for i in range(len(infoList)):
            j = i + 1
            info = infoList[i]

            if info.legendURL is None:
                continue

            req = urllib2.Request(info.legendURL)
            req.add_header('Cookie', request.headers.get('Cookie', ''))

            try:
                filehandle = openURL(req)
                buffer = StringIO(filehandle.read())
                im = Image.open(buffer)
                filehandle.close()
            except Exception, exc:
                log.error("Error retrieving legend from URL %s: %s" % (info.legendURL, exc.__str__()))
            else:
                log.debug("info.legendURL = %s, im.size = %s" % (info.legendURL, im.size,))

                labelImage = self._getLabelImage(j)

                legendImages.append( (labelImage, im) )

        return legendImages

    def _getLabelImage(self, legendNumber):
        """Retrieves a label image from a directory if one is configured, otherwise from a resource.
        @param legendNumber: the number that the legend label is to represent (starts at 1)
        @type legendNumber: integer
        """
        labelLocation = self.legendLabels[legendNumber]
        if self.externalImages:
            labelImageSource = labelLocation
        else:
            inStrm = pkg_resources.resource_stream('ecomaps.resources.images', labelLocation)
            labelImageSource = StringIO(inStrm.read())
        return Image.open(labelImageSource)
