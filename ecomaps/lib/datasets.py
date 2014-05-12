"""
Builds and manages the dataset/endpoint hierarchy, allowing node data to be retrieved and session
endpoints to be added and removed.

@author: rwilkinson
"""

import copy
import logging
from pylons import url
import re
import urllib
import urllib2
from ecomaps.lib.endpoint_hierarchy_builder import EndpointHierarchyBuilder
from ecomaps.lib.endpoint_hierarchy_builder import Node
import ecomaps.lib.outline_layer as outline_layer
import ecomaps.lib.session_endpoint_dataset as session_endpoint_dataset
from ecomaps.lib.viewdata_wms_capability_reader import ViewdataWmsCapabilityReader

log = logging.getLogger(__name__)

WMS_REGEX = re.compile(r'\bwms\b', re.I)

class Datasets:

    def __init__(self, config, enableAddSessionEndpoints):
        """Reads the configuration file if it hasn't been read already.
        @param enableAddSessionEndpoints: boolean indicating whether users should be allowed to add session endpoints
        """
        configFile = config.get('endpointExtendedConfig', None)
        self.sessionData = (config.get('share_endpoint_data', 'True').lower() != 'true')
        log.debug('Sharing of endpoint data is %s.' %
                  ('disabled' if self.sessionData else 'enabled'))
        log.debug('Reading config file %s', configFile)
        endpointHierarchyBuilder = EndpointHierarchyBuilder(configFile)

        # Cache of tree nodes in the form of a dictionary of nodes indexed by node ID
        self.idMap = endpointHierarchyBuilder.parsePage('wmsviz')
        log.debug('Read config file')

        # Add special outline layer entry.
        self.addNode(outline_layer.OUTLINE_LAYER_ID, None, [], outline_layer.treeInfo, {},
                     EndpointHierarchyBuilder.ROOT_NODE, False)

        if enableAddSessionEndpoints:
            # Add user session endpoints 'dataset' and 'new endpoint' nodes.
            self.addNode(session_endpoint_dataset.SESSION_ENDPOINTS_ID, None, [],
                         session_endpoint_dataset.sessionEndpointsTreeInfo, {},
                         EndpointHierarchyBuilder.ROOT_NODE, False)

            self.addNode(session_endpoint_dataset.NEW_ENDPOINT_ID, None, [],
                         session_endpoint_dataset.newEndpointTreeInfo, {},
                         session_endpoint_dataset.SESSION_ENDPOINTS_ID, False)

        # Make a map from endpoint URL to endpoint nodes for use by getLayerDataByEndpointAndName.
        self.endpointMap = {}
        for k, v in self.idMap.iteritems():
            if k.startswith(EndpointHierarchyBuilder.KEY_PREFIX_ENDPOINT):
                if v.entity and 'wmsurl' in v.entity:
                    self.endpointMap[v.entity['wmsurl']] = v

        self.wmsCapabilityReader = ViewdataWmsCapabilityReader(config)

    def load_dataset_types(self, dataset_types):
        """Constructs a treeview node set from a list of dataset types
            params:
                dataset_types: List of dataset types
        """

        nodes = []

        # Add the outline layer
        nodes.append(outline_layer.treeInfo)

        for dataset_type in dataset_types:

            tree_info = {
                'cls': 'folder',
                'id': 'type_%s' % dataset_type.id,
                'text': dataset_type.type
            }

            nodes.append(tree_info)

        return nodes

    def load_datasets(self, dataset_list):
        """Converts our dataset models into the endpoint info we need
            Params:
                dataset_list: List of datasets to convert
        """

        if len(dataset_list) is 0:
            return [{
                'text': 'No datasets found',
                'cls' : 'file',
                'leaf': True
            }]

        datasets = []

        for ds in dataset_list:
            datasets.append(
                {
                    'id': 'ds_%s' % ds.id,
                    'text': ds.name,
                    'wmsurl': ds.wms_url,
                    'cls': 'file',
                    'leaf': True
                }
            )

        return datasets

    def getDatasets(self, request, sessionEndpointData):
        """Returns the node tree information for the children of the specified node ID.
        @param request: HTTP request object
        @param sessionEndpointData: session data for endpoints added by user
        @return list of child nodes
        """
        # self._debugSessionIdMap(sessionEndpointData)
        if 'node' in request.params:
            log.debug('Request for node: ' + request.params['node'])
            nodeId = request.params['node']
        else:
            log.debug('Defaulting to root node')
            nodeId = EndpointHierarchyBuilder.ROOT_NODE

        children = []

        sessionNode = self.getSessionNode(nodeId, sessionEndpointData)
        if sessionNode != None:
            if sessionNode.children != None:
                for child in sessionNode.children:
                    children.append(child.treeInfo)
                log.debug("Session node found with %d children", len(sessionNode.children))

        else:
            node = self.getGlobalNode(nodeId, sessionEndpointData)
            if node != None:
                if node.children != None:
                    for child in node.children:
                        children.append(child.treeInfo)
                log.debug("Node found with %d children", len(children))
            else:
                log.debug("Node not found")

        return children

    def _debugSessionIdMap(self, sessionEndpointData):
        """Logs the session endpoint data for debugging
        @param sessionEndpointData: session data for endpoints added by user
        """
        if sessionEndpointData is not None:
            sessionIdMap = sessionEndpointData.getIdMap()
            log.debug("Session ID map has %d entries" % len(sessionIdMap))
            for k, v in sessionIdMap.iteritems():
                log.debug("  Session node: %s" % k)
                if v.children:
                    for c in v.children:
                        log.debug("    " + c.id)

    def getNode(self, nodeId, sessionEndpointData, forceRefresh=False):
        """Returns a node specified by ID, looking for its ID in the global or local node ID map
        depending on the form of the ID. If the node is an endpoint or a layer, the WMC capabilities
        for the endpoint need to be read in if not done yet.
        @param nodeId: ID of node to retrieve
        @param sessionEndpointData: session data for endpoints added by user
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        @return node or None if node not found
        """
        if Datasets._isSessionNodeId(nodeId) or self.sessionData:
            node = self.getSessionNode(nodeId, sessionEndpointData)
        else:
            node = self.getGlobalNode(nodeId, sessionEndpointData)
        return node

    def _getNode(self, nodeId, sessionEndpointData, forceRefresh=False):
        """Returns a node specified by ID, looking for its ID in the global or local node ID map
        depending on the form of the ID.
        @param nodeId: ID of node to retrieve
        @param sessionEndpointData: session data for endpoints added by user
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        @return node or None if node not found
        """
        # self._debugSessionIdMap(sessionEndpointData)
        if Datasets._isSessionNodeId(nodeId):
            if sessionEndpointData:
                node = sessionEndpointData.getIdMap().get(nodeId, None)
            else:
                node = None
        else:
            node = self.idMap.get(nodeId, None)
        return node

    def getGlobalNode(self, nodeId, sessionEndpointData, forceRefresh=False):
        """Returns a node specified by ID, looking for its ID in the global node ID map. If the
        node is an endpoint or a layer, the WMC capabilities for the endpoint need to be read in if
        not done yet.
        @param nodeId: ID of node to retrieve
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        @return node or None if node not found
        """
        log.debug("getGlobalNode: %s" % nodeId)
        if self.sessionData:
            idMap = {}
        else:
            idMap = self.idMap
        node = self._getNodeFromMap(nodeId, sessionEndpointData, self.idMap, idMap, forceRefresh)
        if self.sessionData:
            sessionEndpointData.setIdMapEntries(idMap)
        return node

    def getSessionNode(self, nodeId, sessionEndpointData, forceRefresh=False):
        """Returns a node specified by ID, looking for its ID in the session node ID map. If the
        node is an endpoint or a layer, the WMC capabilities for the endpoint need to be read in if
        not done yet.
        @param nodeId: ID of node to retrieve
        @param sessionEndpointData: session data for endpoints added by user
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        @return node or None if node not found
        """
        log.debug("getSessionNode: %s" % nodeId)
        if sessionEndpointData is not None:
            idMap = {}
            node = self._getNodeFromMap(nodeId, sessionEndpointData, sessionEndpointData.getIdMap(), idMap, forceRefresh)
            sessionEndpointData.setIdMapEntries(idMap)
            return node
        else:
            return None

    def _getNodeFromMap(self, nodeId, sessionEndpointData, idMap, newIdMap, forceRefresh=False):
        """Returns a node specified by ID, looking for its ID in the specified node ID map. If the
        node is an endpoint or a layer, the WMC capabilities for the endpoint need to be read in if
        not done yet.
        @param nodeId: ID of node to retrieve
        @param sessionEndpointData: session data for endpoints added by user
        @param idMap: map of IDs to existing nodes in which to look for the specified node
        @param newIdMap: map into which new nodes are entered
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        @return node or None if node not found
        """
        node = idMap.get(nodeId, None)
        if node == None:
            log.debug(" - node ID not found in map")
            # Node not found - the ID should be that of a layer from an endpoint for which the WMC
            # capabilities have not yet been read.
            epNode = self._findEndpointAntecedent(nodeId, idMap)
            if epNode != None:
                log.debug("Found antecedent endpoint node - populating")
                self._populateLayers(epNode, sessionEndpointData, newIdMap, forceRefresh)
            node = newIdMap.get(nodeId, idMap.get(nodeId, None))
        else:
            # If the node is an endpoint, a call must be made to find the layers, if not yet done.
            if nodeId.startswith(EndpointHierarchyBuilder.KEY_PREFIX_ENDPOINT):
                log.debug("Is endpoint node - populating")
                node = self._populateLayers(node, sessionEndpointData, newIdMap, forceRefresh)

        return node

    def _findEndpointAntecedent(self, nodeId, idMap):
        """Finds an endpoint node that is specified by the node ID or is an antecedent of that node.
        @param nodeId: ID of node
        @param idMap: map of IDs to nodes in which to look for the specified node
        @return node or None if node not found
        """
        epNode = None
        if (nodeId.startswith(EndpointHierarchyBuilder.KEY_PREFIX_CONTAINER_LAYER) or
            nodeId.startswith(EndpointHierarchyBuilder.KEY_PREFIX_LEAF_LAYER)):

            epIdStart = nodeId.find(EndpointHierarchyBuilder.LAYER_ID_SEPARATOR + EndpointHierarchyBuilder.KEY_PREFIX_ENDPOINT)
            if epIdStart >= 0:
                epId = nodeId[epIdStart + 1:]
                log.debug("Looking for endpoint node: %s" % epId)
                epNode = idMap.get(epId, None)
                log.debug(" - found" if epNode != None else " - not found")

        return epNode

    def findAntecedentNodeIds(self, nodeId, includeStartNode=False):
        """Returns the IDs of nodes that are antecedents of a node of specified ID.
        @param nodeId: ID of node from which to start
        @param includeStartNode: boolean indicating whether the ID of the starting node is to be
                included in the returned list
        @return list of node IDs
        """
        ids = []
        if includeStartNode:
            ids.append(nodeId)
        start = 0
        while start < len(nodeId):
            pos = nodeId.find('@', start)
            if pos == -1:
                break
            start = pos + 1
            ids.append(nodeId[start:])
        return ids

    def _getAntecedentKeywordData(self, node, sessionEndpointData, includeStartNode=False):
        """Returns the keyword data obtained from nodes that are antecedents of a node of specified
        ID. If the same keyword name is found for more than one antecedent, the value from the node
        lower down the tree is used.
        @param node: node for which to return keyword data
        @param sessionEndpointData: session data for endpoints added by user
        @param includeStartNode: boolean indicating whether the ID of the starting node is to be
                included in the returned list
        @return dict of keyword data
        """
        keywordData = {}
        antecedentIds = self.findAntecedentNodeIds(node.id, includeStartNode)
        for nodeId in reversed(antecedentIds):
            log.debug("antecedentId %s" % nodeId)
            antecedentNode = self._getNode(nodeId, sessionEndpointData)
            if antecedentNode and antecedentNode.keywordData:
                log.debug("  keywordData %s" % antecedentNode.keywordData)
                keywordData.update(antecedentNode.keywordData)
        return keywordData

    def _populateLayers(self, node, sessionEndpointData, newIdMap, forceRefresh):
        """Populates the layers for an endpoint if this has not been done already.
        @param node: endpoint node
        @param sessionEndpointData: session data for endpoints added by user
        @param newIdMap: map into which new nodes are entered
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        """
        log.debug("Finding layers for %s", node.id)

        if self.sessionData and (node.id in self.idMap) and (node.id not in sessionEndpointData.getIdMap()):
            # Make session-private copy of endpoint node to populate.
            retNode = copy.deepcopy(node)
            newIdMap[node.id] = retNode
        else:
            retNode = node

        if 'wmsurl' in retNode.entity:
            endpoint = retNode.entity
            wmsurl = endpoint['wmsurl']
            log.debug("endpoint URL %s", wmsurl)

            if 'wcsurl' not in endpoint:
                endpoint['wcsurl'] = None
                (wcsurl, numRepl) = WMS_REGEX.subn('wcs', wmsurl)
                log.debug("Trying WCS URL %s", wcsurl)
                if numRepl > 0:
                    endpoint['wcsurl'] = wcsurl

            if retNode.children == None:
                keywordData = self._getAntecedentKeywordData(retNode, sessionEndpointData, includeStartNode=True)
                retNode.children = self.wmsCapabilityReader.getLayers(endpoint, retNode.id, newIdMap,
                                                                      keywordData, forceRefresh)
                if retNode.children == None:
                    return
                if len(retNode.children) == 1:
                    # Skip a level if it is a container acting as a root node to all the sublayers.
                    containerNode = retNode.children[0]
                    del newIdMap[containerNode.id]
                    retNode.children = containerNode.children
        return retNode

    def getLayerDataAsDict(self, request, sessionEndpointData):
        """Returns the data for a layer specified by ID.
        @param request: HTTP request object
        @param sessionEndpointData: session data for endpoints added by user
        @return dict of layer data
        """
        if 'layerid' in request.params:
            log.debug('Request for layer: ' + request.params['layerid'])
            layerId = request.params['layerid']
        else:
            log.error('No layer ID parameter in layer data request.')
            return

        wmc = self.getLayerData(layerId, sessionEndpointData)

        if wmc != None:
            return wmc.getAsDict()
        else:
            return

    def create_ecomaps_data_url(self, dataset_id, query_string=''):

        return "%s?%s" % (url(controller='dataset', action='wms', id=dataset_id, qualified=True),
                                  query_string)

    def get_ecomaps_layer_data(self, dataset):
        """Looks up layer data in the given WMS url, and returns a layer entity object
            suitable for the map viewer
            Params:
                wms_url: URL to the descriptor service
        """

        qs = dataset.wms_url.split('?')[1]

        indirect_url = self.create_ecomaps_data_url(dataset.id, qs)

        (wcs_url, numRepl) = WMS_REGEX.subn('wcs', indirect_url)
        log.debug("Trying WCS URL %s", wcs_url)

        endpoint = {
            'wmsurl': indirect_url,
            'wcsurl': wcs_url
        }

        layer_info = self.wmsCapabilityReader.getLayers(endpoint, dataset.name, None, None, True)

        # The returned structure will have numerous child layers, however we're only interested in the
        # very last one, as that contains the map data

        def inspect_children(layer_col):

            layers = []

            for layer_obj in layer_col:

                # We need to swap out the 'internal' URLs attached
                # to each dataset with oens through our WMS proxy instead
                if len(layer_obj.children) == 0:

                    # The capability URL will have a query string that we want
                    # to transfer across
                    cap_qs = layer_obj.entity.getCapabilitiesUrl.split('?')[1]

                    layer_obj.entity.getMapUrl = self.create_ecomaps_data_url(dataset.id)
                    layer_obj.entity.getCapabilitiesUrl = self.create_ecomaps_data_url(dataset.id, cap_qs)
                    layer_obj.entity.getFeatureInfoUrl = self.create_ecomaps_data_url(dataset.id)

                    # Each layer may also have a number of 'styles', which have their
                    # own URL to a legend graphic
                    for style in layer_obj.entity.styles:
                        if 'legendURL' in style:
                            url_obj = style['legendURL']
                            style_qs = url_obj['onlineResource'].split('?')[1]
                            url_obj['onlineResource'] = self.create_ecomaps_data_url(dataset.id, style_qs)

                    layers.append(layer_obj)
                else:
                    layers.append(inspect_children(layer_obj.children))

            return layers

        return inspect_children(layer_info[0].children)


    def getLayerData(self, layerId, sessionEndpointData):
        """Returns a data for a layer, specified by ID, that was retrieved from the WMS capabilities
        document.
        @param layerId: ID of layer
        @param sessionEndpointData: session data for endpoints added by user
        @return layer entity object for node or None if layer not found
        """
        # Check that the node ID is for a layer.
        if not layerId.startswith(EndpointHierarchyBuilder.KEY_PREFIX_LEAF_LAYER):
            log.error('ID parameter in layer data request is not a leaf layer ID: %s.', layerId)
            return

        node = self.getNode(layerId, sessionEndpointData)
        if node is None:
            log.debug("Node not found for layer %s", layerId)
            return

        log.debug('Found layer %s', layerId)

        return node.entity

    def getLayerDataByEndpointAndName(self, endpoint, name, sessionEndpointData, forceRefresh=False):
        """Returns a data for a layer, specified by endpoint URL and layer name, that was retrieved
        from the WMS capabilities document.
        @param endpoint: endpoint URL
        @param name: name of layer
        @param sessionEndpointData: session data for endpoints added by user
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        @return layer entity object for node or None if layer not found
        """
        # If the endpoint is one in the dataset tree, use that node, otherwise create a temporary
        # endpoint node.
        if endpoint in self.endpointMap:
            log.debug('Endpoint in endpointMap')
            epNode = self.endpointMap[endpoint]
            idMap = self.idMap
        else:
            endpointEntity = {'wmsurl': endpoint}
            log.debug('Endpoint not in endpointMap')
            epNode = Node('tempid', endpointEntity, None, None, {})
            idMap = {}

        # Populate the layers for the endpoint if not yet done.
        self._populateLayers(epNode, sessionEndpointData, idMap, forceRefresh)

        # Find the named layer.
        node = Datasets._findDescendantLayerByName(epNode, name)
        if node is not None:
            return node.entity
        else:
            return None

    def ensureEndpointCached(self, nodeId, forceRefresh=False):
        """Causes the WMC capabilities for an endpoint node to be read and cached if not already
        cached or if forceRefresh=True.
        @param nodeId: ID of node to retrieve
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        """
        if not nodeId.startswith(EndpointHierarchyBuilder.KEY_PREFIX_ENDPOINT):
            log.error('Node ID %s is not an endpoint ID' % nodeId)
            return
        node = self.idMap.get(nodeId, None)
        if (node is None) or (node.entity is None):
            log.error('Node ID %s is not configured in endpoints file' % nodeId)
            return
        self.wmsCapabilityReader.ensureEndpointCached(node.entity, forceRefresh)

    @staticmethod
    def _findDescendantLayerByName(node, layerName):
        """Finds a layer of a specified name among the descendants of a node.
        @param node: node from which to start searching
        @param layerName: name of layer to find
        @return layer node or None if layer not found
        """
        if node.id.startswith(EndpointHierarchyBuilder.KEY_PREFIX_LEAF_LAYER) and (node.entity.name == layerName):
            return node
        for child in node.children:
            node = Datasets._findDescendantLayerByName(child, layerName)
            if node is not None:
                return node
        return None

    @staticmethod
    def _isSessionNodeId(nodeId):
        """Determines whether a ID is for a node in the session dataset tree by checking whether its
        root dataset is the session endpoints dataset.
        @param nodeId: ID of node
        @return boolean
        """
        lastDsPos = nodeId.rfind(EndpointHierarchyBuilder.LAYER_ID_SEPARATOR +
                                 EndpointHierarchyBuilder.KEY_PREFIX_DATASET)
        if lastDsPos == -1:
            return False
        dsId = nodeId[lastDsPos + 1:]
        return dsId == session_endpoint_dataset.SESSION_ENDPOINTS_ID

    def addNode(self, nodeId, entity, children, treeInfo, keywordData, parentId, prepend):
        """Creates and adds a node as a child of a specified parent.
        @param nodeId: ID of node
        @param entity: entity object that the node represents
        @param children: child nodes
        @param treeInfo: data representing the node in the dataset/endpoint/layer tree
        @param keywordData: keyword data for the node
        @param parentId: ID of parent node
        @param prepend: boolean indicating whether the new node is to be prepended to its parent's
               list of children
        """
        parent = self.idMap.get(parentId, None)
        if parent is None:
            log.error('Parent not found when adding node %s to parent %s' % (nodeId, parentId))
            return
        node = Node(nodeId, entity, children, treeInfo, keywordData)
        if parent.children is None:
            parent.children = []
        siblings = parent.children

        # Insert as first or last child depending on prepend value.
        if prepend:
            siblings.insert(0, node)
        else:
            siblings.append(node)

        # Add to the ID map.
        self.idMap[nodeId] = node

    def addSessionNode(self, nodeId, entity, children, treeInfo, keywordData, parentId, prepend, sessionEndpointData):
        """Creates and adds a node as a child of a specified parent, storing it in the ID/node map
        for the session.
        @param nodeId: ID of node
        @param entity: entity object that the node represents
        @param children: child nodes
        @param treeInfo: data representing the node in the dataset/endpoint/layer tree
        @param keywordData: keyword data for the node
        @param parentId: ID of parent node
        @param prepend: boolean indicating whether the new node is to be prepended to its parent's
               list of children
        @param sessionEndpointData: session data for endpoints added by user
        @return created node
        """
        log.debug("addSessionNode %s to %s" % (nodeId, parentId))

        # Find parent - if there is no session copy, create one from the global entity.
        sessionIdMap = sessionEndpointData.getIdMap()
        parent = sessionIdMap.get(parentId, None)
        if parent is None:
            globalParent = self.idMap.get(parentId, None)
            if globalParent is not None:
                parent = Node(parentId, globalParent.entity, None, globalParent.treeInfo, globalParent.keywordData)
                sessionIdMap = sessionEndpointData.setIdMapEntry(parentId, parent)
                log.debug("Added parent node %s to session ID map" % parentId)
        else:
            log.debug("Parent found in session ID map")

        if parent is None:
            log.error('Parent not found when adding node %s to parent %s' % (nodeId, parentId))
            return

        node = Node(nodeId, entity, children, treeInfo, keywordData)
        if parent.children is None:
            parent.children = []
        siblings = parent.children

        # Insert as first or last child depending on prepend value.
        if prepend:
            siblings.insert(0, node)
        else:
            siblings.append(node)

        # Add to the ID map.
        sessionIdMap[nodeId] = node
        sessionIdMap = sessionEndpointData.setIdMapEntry(nodeId, node)
        log.debug("Added node %s to session ID map" % nodeId)

        # self._debugSessionIdMap(sessionEndpointData)
        return node

    def getSessionEndpointData(self, endpoint, forceRefresh):
        """Returns service data for an endpoint.
        @param endpoint: endpoint object
        @param forceRefresh: re-read WMC capabilities from server even if previously cached
        @return service data for the endpoint or dict containing error entry
        """
        log.debug("getSessionEndpointData %s" % (endpoint['name']))
        try:
            return self.wmsCapabilityReader.getEndpointServiceData(endpoint, forceRefresh)
        except urllib2.HTTPError, exc:
            log.info("getEndpointServiceData request received HTTP error code %d" % exc.code)
            return {'error': "Error getting information about service: HTTP status %d" % exc.code}
        except urllib2.URLError, exc:
            return {'error': "Error getting information about service: " + exc.reason.__str__()}
        except Exception, exc:
            log.info("getEndpointServiceData threw exception %s" % exc.__str__())
            return {'error': "Error getting information about service"}

    def removeSessionNode(self, nodeId, parentId, sessionEndpointData):
        """Removes a node from its parent and from the session ID/node map.
        @param nodeId: ID of node to remove
        @param parentId: ID of parent node
        @param sessionEndpointData: session data for endpoints added by user
        """
        log.debug("removeSessionNode %s" % (nodeId,))

        sessionIdMap = sessionEndpointData.getIdMap()

        # Remove node from parent's children.
        parent = sessionIdMap.get(parentId, None)
        if parent and parent.children:
            childNodes = [c for c in parent.children if c.id != nodeId]
            parent.children = childNodes

        # Remove node and its descendants from ID map.
        node = sessionIdMap.get(nodeId, None)
        if node:
            nodeIds = []
            self.findTreeNodeIds(node, sessionEndpointData, nodeIds)
            sessionEndpointData.removeIdMapEntries(nodeIds)

    def findTreeNodeIds(self, root, sessionEndpointData, nodeList):
        """Finds the IDs of the nodes in the tree rooted at the specified node.
        @param root: node from which to start searching
        @param sessionEndpointData: session data for endpoints added by user
        @param nodeList: list to which to add IDs of found nodes
        """
        if root.children:
            for child in root.children:
                self.findTreeNodeIds(child, sessionEndpointData, nodeList)
        nodeList.append(root.id)

    def addSessionEndpoint(self, request, sessionEndpointData):
        """Add an endpoint to the session specific node tree.
        @param request: HTTP request object
        @param sessionEndpointData: session data for endpoints added by user
        @return tree info for created node
        """
        if sessionEndpointData is None:
            return {'error': 'Adding session map services is not possible currently.'}

        if 'url' in request.params:
            url = request.params['url']
            endpointId = (EndpointHierarchyBuilder.KEY_PREFIX_ENDPOINT + urllib.quote_plus(url) +
                          EndpointHierarchyBuilder.LAYER_ID_SEPARATOR +
                          session_endpoint_dataset.SESSION_ENDPOINTS_ID)

            endpoint = {
                'key': 'dataset:' + url,
                'name': url,
                'wmsurl': url
                }

            serviceData = self.getSessionEndpointData(endpoint, False)

            qtip = url
            if serviceData.get('error', None):
                qtip = serviceData['error']
            else:
                if serviceData.get('title', None):
                    qtip = serviceData['title']
                if serviceData.get('abstract', None):
                    qtip += " - " + serviceData['abstract']

            endpointTreeInfo = {
                'id': endpointId,
                'text': url,
                'qtip': qtip,
                'removable': True,
                'uiProvider': 'dataset',
                'cls': 'folder'
                }

            node = self.addSessionNode(endpointId, endpoint, None, endpointTreeInfo, {},
                                       session_endpoint_dataset.SESSION_ENDPOINTS_ID, False, sessionEndpointData)
            if node is not None:
                return endpointTreeInfo
            else:
                return None

    def removeSessionEndpoint(self, request, sessionEndpointData):
        """Remove an endpoint from the session specific node tree.
        @param request: HTTP request object
        @param sessionEndpointData: session data for endpoints added by user
        """
        if sessionEndpointData is None:
            return

        if 'endpointId' in request.params:
            endpointId = request.params['endpointId']
            self.removeSessionNode(endpointId, session_endpoint_dataset.SESSION_ENDPOINTS_ID, sessionEndpointData)

# Global dataset manager
datasetManager = None

def createDatasetManager(config, enableAddSessionEndpoints):
    """Creates a global dataset manager.
    @param config: application configuration
    @param enableAddSessionEndpoints: boolean indicating whether users should be allowed to add session endpoints
    @return global Datasets instance
    """
    global datasetManager
    datasetManager = Datasets(config, enableAddSessionEndpoints)
    return datasetManager
