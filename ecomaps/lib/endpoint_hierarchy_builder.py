"""
Constructs the hierarchy of endpoint information.

@author: rwilkinson
"""

import logging
from ecomaps.lib.config_file_parser import ConfigFileParser

log = logging.getLogger(__name__)

class EndpointHierarchyBuilder(ConfigFileParser):

    KEY_PREFIX_DATASET = 'ds:'
    KEY_PREFIX_ENDPOINT = 'ep:'
    KEY_PREFIX_CONTAINER_LAYER = 'cl:'
    KEY_PREFIX_LEAF_LAYER = 'll:'
    LAYER_ID_SEPARATOR = '@'
    ROOT_NODE = '0'
    ENTITY_KEYWORDS = ['abstract', 'layerset', 'metadatalink', 'name', 'title']

    def __init__(self, filePath):
        ConfigFileParser.__init__(self, filePath)

    def parsePage(self, page):
        """Parse the dataset, endpoint hierarchy for a specified page.
        """
        # Cache of tree nodes in the form of a dictionary of nodes indexed by node ID
        self.idMap = {}

        datasets = self.buildDict(page, 'keys', 'dataset', [])
        datasetList = self.buildListForItem(page, 'keys')

        # Set up the data for the tree node.
        treeId = self.ROOT_NODE
        treeInfo = {
            'id': treeId,
            'text': '',
            'cls': 'folder'
            }

        children = []
        node = Node(treeId, None, children, treeInfo, {})
        self.idMap[treeId] = node

        for key in datasetList:
            if key in datasets:
                cat = datasets[key]
                self.parseDataset(key, cat, children, None)

        return self.idMap

    def parseDataset(self, key, dataset, siblings, parentId):
        """Parse the entities referenced by a dataset.
        """
        log.debug("Parsing dataset %s", key)

        if self._checkForCircularity(key, dataset):
            log.error("Dataset nesting is circular: %s", key)
            return

        dataset['key'] = key

        keywordData = self._processKeywords(dataset)

        # Set up the data for the tree node.
        treeId = self.KEY_PREFIX_DATASET + key
        if parentId != None:
            treeId += self.LAYER_ID_SEPARATOR + parentId
        if 'title' in dataset:
            text = dataset['title']
        else:
            text = key

        if 'abstract' in dataset:
            qtip = dataset['abstract']
        else:
            qtip = text

        treeInfo = {
            'id': treeId,
            'text': text,
            'qtip': qtip,
            'uiProvider': 'dataset',
            'metadataURL': dataset.get('metadatalink', None),
            'cls': 'folder'
            }

        children = []

        node = Node(treeId, dataset, children, treeInfo, keywordData)
        self.idMap[treeId] = node
        siblings.append(node)

        if 'datasets' in dataset:
            datasetKeys = [x.strip() for x in dataset['datasets'].split(',')]
            datasets = self.buildItemDict('dataset', datasetKeys, [])
            dataset['datasetDict'] = datasets

            # Handle the datasets referenced by the dataset.
            for k in datasetKeys:
                if k in datasets:
                    ds = datasets[k]
                    ds['parentDataset'] = dataset
                    self.parseDataset(k, ds, children, treeId)

        if 'endpoints' in dataset:
            endpointKeys = [x.strip() for x in dataset['endpoints'].split(',')]
            endpoints = self.buildItemDict('endpoint', endpointKeys, [])

            # Add a reference back to the dataset.
            for k in endpointKeys:
                if k in endpoints:
                    ep = endpoints[k]
                    ep['dataset'] = dataset
                    self.parseEndpoint(k, ep, children, treeId)

            dataset['endpointDict'] = endpoints

    def parseEndpoint(self, key, endpoint, siblings, parentId):
        """Parse the entities referenced by an endpoint.
        """
        log.debug("Parsing endpoint %s", key)
        endpoint['key'] = key

        keywordData = self._processKeywords(endpoint)

        # Set up the data for the tree node.
        treeId = self.KEY_PREFIX_ENDPOINT + key + self.LAYER_ID_SEPARATOR + parentId
        if 'name' in endpoint:
            text = endpoint['name']
        elif 'title' in endpoint:
            text = endpoint['title']
        else:
            text = key

        if 'abstract' in endpoint:
            qtip = endpoint['abstract']
        else:
            qtip = text

        treeInfo = {
            'id': treeId,
            'text': text,
            'qtip': qtip,
            'uiProvider': 'dataset',
            'metadataURL': endpoint.get('metadatalink', None),
            'cls': 'folder'
            }

        # Children of endpoints are layers, which are not populated here. Set a value that indicates
        # that the chilren are not yet populated.
        children = None

        node = Node(treeId, endpoint, children, treeInfo, keywordData)
        self.idMap[treeId] = node
        siblings.append(node)

        self._processNewLayerNames(endpoint)
        self._processLayerData(endpoint)

    def _checkForCircularity(self, key, dataset):
        """Checks whether the dataset keys form  a circular reference set by checking this dataset's antecedents.
        """
        ds = dataset
        while 'parentDataset' in ds:
            ds = ds['parentDataset']
            if key == ds['key']:
                return True
        return False

    def _processKeywords(self, entity):
        """Processes any keyword/value data set for an entity.
        """
        # Get any keyword values configured for the entity.
        if 'keyworddata' in entity:
            keywordDataKey = entity['keyworddata']
            keywordData = self.buildItemDict('key', [keywordDataKey], []).get(keywordDataKey, {})
        else:
            keywordData = {}

        # Set values of entity properties that are unset but are set via a keyword.
        for key in self.ENTITY_KEYWORDS:
            if key not in entity and key in keywordData:
                entity[key] = keywordData[key]

        return keywordData

    def _processNewLayerNames(self, endpoint):
        """Processes any replacement layer names set for an endpoint.
        """
        if 'newlayernames' in endpoint:
            layerMap = {}
            layerNames = [x.strip() for x in endpoint['newlayernames'].split('\n')]
            for m in layerNames:
                k, s, name = m.partition(':')
                log.debug("Parsing new layer name %s", k)
                # Key must be unicode to match unicode layer names from capability documents.
                ucKey = unicode(k.strip(), 'ascii')
                layerMap[ucKey] = name.strip()
            endpoint['newLayerNamesDict'] = layerMap

    def _processLayerData(self, endpoint):
        """Processes any layerset keys for an endpoint: finds the corresponding layer set and the
        data for each variable in it.
        """
        if 'layerset' in endpoint:
            layerSetKey = endpoint['layerset']
            layerSetData = self.buildItemDict('layerset', [layerSetKey], []).get(layerSetKey, {})

            layerSetStr = layerSetData.get('layers', '')
            layerSet = [x.strip() for x in layerSetStr.split(',')] if layerSetStr else []

            layers = self.buildItemDict('layer', layerSet, [])
            layerSetData['layers'] = layers
            endpoint['layerSetData'] = layerSetData

class Node:
    def __init__(self, id, entity, children, treeInfo, keywordData):
        # Id of tree node
        self.id = id
        # Entity object
        self.entity = entity
        # Child nodes of this node
        self.children = children
        # Map of information used on tree
        self.treeInfo = treeInfo
        # Map of keyword data
        self.keywordData = keywordData
