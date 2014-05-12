"""
Extension of WMS capabilities reader to include information for the Viewdata dataset/endpoint/layer tree.

@author: rwilkinson
"""

import logging

from ecomaps.lib.wms_capability_reader import WmsCapabilityReader

log = logging.getLogger(__name__)

class ViewdataWmsCapabilityReader(WmsCapabilityReader):

    def makeTreeInfo(self, endpoint, layer, isLeaf, keywordData):
        """Makes the information used to populate the viewdata dataset tree.
        """
        self._mergeLayerKeywordData(layer, keywordData)

        # Title and abstract are intended to be human readable; name is for machine use. Title is
        # mandatory, name and abstract are not. Construct the text and tooltip for the node from
        # most appropriate supplied values.
        displayText = layer.title

        if layer.name:
            name = layer.name
            qtip = name
            # Use replacement name from endpoints configuration file as text if provided.
            if 'newLayerNamesDict' in endpoint:
                layerMap = endpoint['newLayerNamesDict']
                if name in layerMap:
                    displayText = layerMap[name]
            if layer.abstract:
                if layer.configuredAbstract:
                    # Assume that if an abstract has been set by configuration, this is the correct
                    # text to show.
                    qtip = layer.abstract
                else:
                    qtip = qtip + " - " + layer.abstract
        else:
            if layer.abstract:
                qtip = layer.abstract
            else:
                qtip = ''

        treeId = layer.id
        if isLeaf:
            treeInfo = {
                'id': treeId,
                'text': displayText,
                'qtip': qtip,
                'cls': 'file',
                'leaf': True
                }
        else:
            treeInfo = {
                'id': treeId,
                'text': displayText,
                'qtip': qtip,
                'cls': 'folder',
                'leaf': False
                }

        return treeInfo

    def _mergeLayerKeywordData(self, layer, keywordData):
        """Substitutes certain layer data from corresponding keyword data.
        """
        layer.configuredAbstract = False
        if keywordData:
            if 'title' in keywordData:
                layer.title = keywordData['title']
            if 'abstract' in keywordData:
                layer.abstract = keywordData['abstract']
                layer.configuredAbstract = True
