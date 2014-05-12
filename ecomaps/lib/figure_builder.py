import copy, logging

try:
    from PIL import Image
except:
    import Image

log = logging.getLogger(__name__)

from ecomaps.lib.legend_image_builder import LegendImageBuilder
from ecomaps.lib.ipccDdcMetadataImageBuilder import IpccDdcMetadataImageBuilder
from ecomaps.lib.viewdataMetadataImageBuilder import ViewdataMetadataImageBuilder
from ecomaps.lib.wmsvizMetadataImageBuilder import WmsvizMetadataImageBuilder


class FigureBuilder(object):
    """Builds the complete figure from the map image and metadata.
    """
    # Metadata image builder classes for each figure style
    METADATA_IMAGE_BUILDERS = {
        'default': ViewdataMetadataImageBuilder,
        'ipcc-ddc': IpccDdcMetadataImageBuilder,
        'viewdata': ViewdataMetadataImageBuilder,
        'wmsviz': WmsvizMetadataImageBuilder}

    def __init__(self, params, figureOptions, layerInfoList):
        """
        @param params: request parameters
        @param figureOptions: overall options for the figure
        @param layerInfoList: list of LayerInfo defining layers to include in the figure
        """
        self.layerInfoList = layerInfoList
        figureStyle = figureOptions.style
        if figureStyle not in self.METADATA_IMAGE_BUILDERS.keys():
            log.warn("Invalid figure type requested: %s" % figureStyle)
            figureStyle = 'default'
        self.metadataBuilder = self.METADATA_IMAGE_BUILDERS[figureStyle](params)
        self.legendBuilder = LegendImageBuilder()

    def buildImage(self, mapImage, points):
        '''
        Builds a composite image of the metadata, map and legends

        @param mapImage: the image of the map
        @type mapImage: PIL Image
        @param points: the points on the map that locate the four corners
        (this is excluding the labels)
        @type points: 4-tuple
        '''

        log.debug("mapImage.size = %s" % (mapImage.size,))

        metadataImage = self.metadataBuilder.buildMetadataImage(self.layerInfoList,
                                                                mapImage.size[0])
        metadataImageHeight = metadataImage.size[1]
        log.debug("metadataImageHeight %d" % metadataImageHeight)

        legendImage = self.legendBuilder.buildLegendImage(self.layerInfoList,
                                                          mapImage.size[0])
        legendImageHeight = legendImage.size[1]

        log.debug("legendImage.size = %s" % (legendImage.size,))
        log.debug("metadataImage.size = %s" % (metadataImage.size,))

        if hasattr(self.metadataBuilder, 'buildDetailsImage'):
            detailsImage = self.metadataBuilder.buildDetailsImage(self.layerInfoList,
                                                                  mapImage.size[0])
            log.debug("detailsImage.size = %s" % (detailsImage.size,))
            detailsImageHeight = detailsImage.size[1]
        else:
            detailsImage = None
            detailsImageHeight = 0

        mapImageHeight = mapImage.size[1]
        log.debug("mapImageHeight %d" % mapImageHeight)

        (metadataSpace, legendSpace, detailsSpace) = self.metadataBuilder.getFigureSpacings()
        log.debug("metadataSpace %d" % metadataSpace)


        # if the top of the map is a long way from the top of the map image then
        # we can overlay the metadata and legend images slightly.

        log.debug("points = %s" % (points,))

        (left, bottom, right, top) = points

        # Allow space for frame, axes and labels.
        mapTopOffset = 10
        mapBottomOffset = 50

        topOverlap = mapImageHeight - top - metadataSpace - mapTopOffset
        if topOverlap < 0:
            topOverlap = 0

        bottomOverlap = bottom - legendSpace - mapBottomOffset
        if bottomOverlap < 0:
            bottomOverlap = 0

        log.debug("topOverlap = %s, bottomOverlap = %s" % (topOverlap, bottomOverlap,))
        compositeIm = Image.new('RGBA',
                                (mapImage.size[0],
                                 (metadataImageHeight + mapImageHeight + legendImageHeight +
                                  detailsImageHeight - topOverlap - bottomOverlap)))


        detailsBox = (0,
                      metadataImageHeight + mapImageHeight + legendImageHeight - topOverlap - bottomOverlap,
                      legendImage.size[0],
                      metadataImageHeight + mapImageHeight + legendImageHeight + detailsImageHeight - topOverlap - bottomOverlap)

        legendBox = (0, metadataImageHeight + mapImageHeight - topOverlap - bottomOverlap,
                     legendImage.size[0], metadataImageHeight + mapImageHeight + legendImageHeight - topOverlap - bottomOverlap)

        mapBox = (0, metadataImageHeight - topOverlap,
                  mapImage.size[0], mapImageHeight + metadataImageHeight  - topOverlap)

        metadataBox = (0, 0, metadataImage.size[0], metadataImageHeight)

        compositeIm.paste(mapImage, mapBox)
        compositeIm.paste(metadataImage, metadataBox)
        compositeIm.paste(legendImage, legendBox)
        if detailsImage:
            compositeIm.paste(detailsImage, detailsBox)

        return compositeIm


