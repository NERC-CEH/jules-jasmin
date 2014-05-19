"""
Holds data relating to session endpoints for storage in the session object.

@author: rwilkinson
"""
import logging
log = logging.getLogger(__name__)

class SessionEndpointData:
    idMapKey = 'SESSION_ENDPOINT_ID_MAP'

    def __init__(self, session):
        self.session = session

    def getIdMap(self):
        """Returns the session endpoint ID map.
        """
        idMap = self.session.get(self.idMapKey, None)
        if idMap is None:
            idMap = {}
            self.session[self.idMapKey] = idMap
        return idMap

    def setIdMapEntry(self, id, node):
        """Sets an entry in the session endpoint ID map.
        """
        idMap = self.getIdMap()
        idMap[id] = node
        self.session.save()
        log.debug("Saved session")
        return idMap

    def setIdMapEntries(self, idMap):
        """Sets entries from a dict of IDs and endpoint nodes in the session endpoint ID map.
        """
        sessionIdMap = self.getIdMap()
        for k, v in idMap.iteritems():
            sessionIdMap[k] = v
        if len(idMap) > 0:
            self.session.save()
            log.debug("Saved session")
        return idMap

    def removeIdMapEntry(self, id):
        """Removes an entry from the session endpoint ID map.
        """
        idMap = self.getIdMap()
        del idMap[id]
        self.session.save()
        log.debug("Saved session")
        return idMap

    def removeIdMapEntries(self, idList):
        """Removes an entry from the session endpoint ID map.
        """
        idMap = self.getIdMap()
        for i in idList:
            del idMap[i]
        self.session.save()
        log.debug("Saved session")
        return idMap
