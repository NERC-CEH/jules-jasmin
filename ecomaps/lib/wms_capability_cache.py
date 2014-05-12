"""
Manages a Beaker cache of WMS capabilities documents.

@author: rwilkinson
"""

import logging
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from ecomaps.lib.wmc_util import GetWebMapCapabilities

log = logging.getLogger(__name__)

class WmsCapabilityCache():
    """ Manages a Beaker cache of WMS capabilities documents.
    """
    def __init__(self, config):
        """Creates a cache using the supplied configuration parameters or defaults.
        """
        self.enableCache = (config.get('wmscapabilitycache.enable', 'True').lower() == 'true')
        if self.enableCache:
            cache_opts = {
                'cache.expire': config.get('wmscapabilitycache.expire', None),
                'cache.type': config.get('wmscapabilitycache.type', 'file'),
                'cache.data_dir': config.get('wmscapabilitycache.data_dir', '/tmp/ecomaps/wmscapabilitycache/data'),
                'cache.lock_dir': config.get('wmscapabilitycache.lock_dir', None)
                }
            cacheMgr = CacheManager(**parse_cache_config_options(cache_opts))
    
            self.cache = cacheMgr.get_cache('getWmsCapabilities')
        log.info("WMS capability caching %s" % ("enabled" if self.enableCache else "disabled"))

    def getWmsCapabilities(self, wmsurl, forceRefresh):
        """Gets the WMS capabilities for an endpoint URL from the cache or WMS server if not found in the cache.
        """
        if self.enableCache:
            def __doGet():
                """Makes request for capabilities.
                """
                log.debug("WMS capabilities not found in cache for %s" % search_param)
                return GetWebMapCapabilities(search_param)
    
            search_param = wmsurl
            if forceRefresh:
                self.cache.remove_value(key = search_param)
            log.debug("Looking for WMS capabilities in cache for %s" % search_param)
            return  self.cache.get(key = search_param, createfunc = __doGet)
        else:
            log.debug("Fetching WMS capabilities for %s (caching disabled)" % wmsurl)
            return GetWebMapCapabilities(wmsurl)
