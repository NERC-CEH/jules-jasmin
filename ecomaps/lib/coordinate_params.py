"""
Handles variations in coordinate parameters.

@author: rwilkinson
"""
import logging

log = logging.getLogger(__name__)

NO_LAT_LONG_PROTOCOLS = ['WCS']
NO_LAT_LONG_VERSIONS = ['WCS1.0.0', 'WMS1.1.0', 'WMS1.1.1']

LAT_LONG_CRSS = ['EPSG:4326']

def adjustCoordinateOrderParams(params, protocol):
    """Handle variations in coordinate order depending on WMS version and CRS.
    """
    if (protocol not in NO_LAT_LONG_PROTOCOLS) and (protocol + params['VERSION'] not in NO_LAT_LONG_VERSIONS):
        crs = params['CRS']
        if crs in LAT_LONG_CRSS:
            bounds = params['BBOX'].split(',')
            params['BBOX'] = "%s,%s,%s,%s" % (bounds[1], bounds[0], bounds[3], bounds[2])
            log.debug("Transformed coordinates for %s %s,%s,%s,%s -> %s" %
                      (protocol + params['VERSION'], bounds[0], bounds[1], bounds[2], bounds[3], params['BBOX']))
