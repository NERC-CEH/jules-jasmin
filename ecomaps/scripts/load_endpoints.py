"""
Loads the WMS capabilities for endpoints into the cache.

@author: rwilkinson
"""
import sys
import logging
from ecomaps.lib.datasets import Datasets
from ecomaps.lib.endpoint_hierarchy_builder import EndpointHierarchyBuilder

logging.basicConfig()
log = logging.getLogger(__name__)

def load(endpoint_file, cache_type, cache_data_dir, proxyUrl, endpointId):
    """Loads the WMS capabilities for endpoints into the cache.
    Reads the endpoint configuration file then iterates over each endpoint, fetching the
    corresponding node, which causes the WMS capabilities to be fetched from the WMS server and
    cached if not already found in the cache.
    """
    config = {
        'endpointExtendedConfig': endpoint_file,
        'proxyUrl': proxyUrl,
        'wmscapabilitycache.type': cache_type,
        'wmscapabilitycache.data_dir': cache_data_dir
        }
    datasets = Datasets(config, False)
    idMap = datasets.idMap

    try:
        if endpointId is None:
            for nodeId in idMap.keys():
                if nodeId.startswith(EndpointHierarchyBuilder.KEY_PREFIX_ENDPOINT):
                    loadEndpoint(datasets, nodeId, False)
        else:
            if endpointId.startswith(EndpointHierarchyBuilder.KEY_PREFIX_ENDPOINT):
                if endpointId in idMap:
                    loadEndpoint(datasets, endpointId, True)
            else:
                print("ID is not an endpoint ID: %s" % (endpointId,))
    except KeyboardInterrupt:
        print("Operation terminated by user interrupt.")

def loadEndpoint(datasets, nodeId, forceRefresh):
    print nodeId
    try:
        # datasets.getGlobalNode(id, forceRefresh)
        datasets.ensureEndpointCached(nodeId, forceRefresh)
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        print " - failed: " + e.__str__()

def main():
    """Loads the WMS capabilities for endpoints into the cache.
    Usage: load_endpoints.py <endpoint file> <cache type> <cache data_dir>
    <endpoint file> - extended endpoint configuration file used by the Viewdata application
    <cache type> - cache type: e.g., dbm or file
    <cache data_dir> - cache data directory
    The parameter values should match those configured in the app:main section of the COWS client
    application configuration file for the following options:
      endpointExtendedConfig
      wmscapabilitycache.type
      wmscapabilitycache.data_dir
    """
    if len(sys.argv) in range(4, 6):
        load(sys.argv[1], sys.argv[2], sys.argv[3],
             sys.argv[4] if len(sys.argv) > 4 else None,
             sys.argv[5] if len(sys.argv) > 5 else None)
    else:
        print("""Usage: load_endpoints.py <endpoint file> <cache type> <cache data_dir> [<proxy URL>] [<endpoint ID>]
    <endpoint file> - extended endpoint configuration file used by the Viewdata application
    <cache type> - cache type: e.g., dbm or file
    <cache data_dir> - cache data directory
    <proxy URL> - URL of an NDG Security proxy
    <endpoint ID> - ID of a an endpoint for which to load/refresh the capabilities
    The parameter values should match those configured in the app:main section of the COWS client
    application configuration file for the following options:
      endpointExtendedConfig
      wmscapabilitycache.type
      wmscapabilitycache.data_dir
        """)

if __name__== '__main__':
    main()
