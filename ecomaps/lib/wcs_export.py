"""
WCS export.

@author: rwilkinson
"""
import logging
import os
import re
import tempfile
import urllib

from owslib.wcs import WebCoverageService

from ecomaps.lib.base import response, config, request
import ecomaps.lib.date_util as date_util
from ecomaps.lib.export_parameters import ExportParameters, ExportResult
from ecomaps.lib.wmc_util import proxyFix, resetProxy, parseEndpointString

log = logging.getLogger(__name__)

# Regular expression to match one of
#   filename=a_file_name
#   filename="a_file_name"
# with optional white space around the = sign and/or at the end of the string.

CONTENT_FILENAME_REGEX = re.compile('filename\\s*=\\s*(?P<q>")?(?P<filename>.*?)(?(q)(?P=q)|(?<=\\S)(\\s|\\Z))', re.I)

def makeWcsExportFile(exportParams):
    """Retrieves an export file using WCS. If multiple dimension values are specified, the result
        will contain data for each.
    @param exportParams: object holding all the parametes for an export
    @return ExportResult holding request status and output file if successful
    """
    layerInfo = exportParams.layerInfoList[exportParams.animationLayerNumber - 1]

    # Modify parameters to take into account the dimension over which a range is specified.
    # Include workaround for COWS Server limitations - time must have start and end values, other
    # dimensions must be a single value or range start and end values only.
    baseParams = _getParams(layerInfo.params)
    log.debug("baseParams = %s" % (baseParams,))
    log.debug("Animation dimension is %s" % exportParams.animationDimension)
    if (exportParams.animationDimension != None) and (exportParams.animationDimension in baseParams):
        log.debug("Animation dimension found in parameters")
        if exportParams.animationDimension == 'TIME':
            vals = list(_orderValues(exportParams.startValue, exportParams.endValue, expectTime=True))
            baseParams[exportParams.animationDimension] = vals
            log.debug("Animation dimension is time: (start, end)=(%s, %s)" % (vals[0], vals[1]))
        else:
            # For WCS servers that accept comma separated list of dimension values, the following
            # would be used:
            # baseParams[exportParams.animationDimension] = exportParams.startValue
            # baseParams[exportParams.animationDimension] = ','.join(exportParams.dimensionValues)

            # Set dimension value or range.
            if exportParams.startValue == exportParams.endValue:
                baseParams[exportParams.animationDimension] = exportParams.startValue
            else:
                baseParams[exportParams.animationDimension] = (
                    "%s,%s" % _orderValues(exportParams.startValue, exportParams.endValue))
            log.debug("Animation dimension is not time: %s=%s" %
                      (exportParams.animationDimension, baseParams[exportParams.animationDimension]))
            if 'TIME' in baseParams:
                timeValue = baseParams['TIME']
                baseParams['TIME'] = [timeValue, timeValue]
                log.debug("Setting time to %s" % timeValue)

    baseParams['ENDPOINT'] = layerInfo.endpoint

    # Fetch the data to a file.
    errorReason = None
    try:
        (data, headers) = _getWcsData(baseParams)

        outFileName = headers.get('filename', None)
        if outFileName is not None:
            fileParts = os.path.basename(outFileName).rsplit('.', 1)
            fileSuffix = ('.' + fileParts[1]) if len(fileParts) == 2 else '.dat'
        outFile = tempfile.NamedTemporaryFile(prefix=exportParams.fileNamePrefix, suffix=fileSuffix, delete=False,
                                              dir=config.get('export_file_dir', tempfile.gettempdir()))
        log.debug("File: %s" % (outFile.name))
        outFile.write(data)
        outFile.close()
    except Exception, err:
        log.error("Exception retrieving WCS data: %s" % err)
        errorReason = err.__str__()
        outFile = None

    if outFile == None:
        errorMessage = 'WCS data retrieval failed'
        if errorReason:
            errorMessage += ': ' + errorReason
        return ExportResult(False, errorMessage=errorMessage)
    else:
        return ExportResult(True, fileName = os.path.basename(outFile.name))


def _orderValues(a, b, expectTime=False):
    """Orders two values in ascending value.
    @param a: first value
    @param b: second value
    @param expectTime: True if the values are expected to be time values, otherwise False (in which
        case the values are parsed as numbers first, and only if this fails are they parsed as times)
    @return tuple containing the supplied values in the appropriate order, or None if they values
        cannot be parsed
    """
    if expectTime:
        result = _orderValuesAsTimes(a, b)
        return result if result is not None else (a, b)
    else:
        result = _orderValuesAsNumbers(a, b)
        if result is None:
            result = _orderValuesAsTimes(a, b)
        return result if result is not None else (a, b)

def _orderValuesAsTimes(a, b):
    """Orders two values in ascending value, parsing the supplied strings as times.
    @param a: first value
    @param b: second value
    @return tuple containing the supplied values in the appropriate order, or None if they values
        cannot be parsed
    """
    try:
        aCt = date_util.iso2comptime(a)
        bCt = date_util.iso2comptime(b)
        return (a, b) if aCt.compare(bCt) <= 0 else (b, a)
    except ValueError:
        return None

def _orderValuesAsNumbers(a, b):
    """Orders two values in ascending value, parsing the supplied strings as floats.
    @param a: first value
    @param b: second value
    @return tuple containing the supplied values in the appropriate order, or None if they values
        cannot be parsed
    """
    try:
        aFl = float(a)
        bFl = float(b)
        return (a, b) if aFl <= bFl else (b, a)
    except ValueError:
        return None

def _getWcsData(params):
    """Performs WCS retrieval for a set of parameters.
    @param params: parameters to use in WCS r equest
    @return tuple (WCS response data, content header information)
    """
    params = _getParams(params)
    log.debug("params = %s" % (params,))

    endpoint = params.get('ENDPOINT')

    # Set OWSlib WCS parameters.
    args = {}
    layerId = params['LAYERS'].partition(',')[0]
    args['identifier'] = layerId
    # Get the bounding box values (W, S, E, N).
    args['bbox'] = tuple(params.get('BBOX').split(','))
    args['format'] = params['FORMAT']
    args['crs'] = params['CRS']
    args['time'] = params.get('TIME')

    wcs, layers = _getWCSObj(endpoint)

    log.debug("wcs.url = %s" % (wcs.url,))

    if layerId not in layers:
        raise Exception("Layer %s is not available for WCS download" % layerId)

    # Find the dimension names for the layer, and if there are any request parameters with the same
    # name as a dimension, use them as a GetCoverage argument.
    layer = [x for x in wcs.items() if x[0] == layerId][0][1]
    for dimensionName in [a.name.upper() for a in layer.axisDescriptions]:
        log.debug("Checking for value for dimension %s" % dimensionName)
        if dimensionName in params:
            args[dimensionName] = params[dimensionName]
            log.debug("Found value %s" % params[dimensionName])

    log.debug("args = %s" % (args,))

    # Perform the GetCoverage request.
    oldProxy = proxyFix(endpoint)
    try:
        output = wcs.getCoverage(**args)
    except Exception, e:
        log.exception("Exception occurred")
        raise
    finally:
        resetProxy(oldProxy)

    # Retrieve the content disposition and type headers.
    responseHeaders = {}
    for k in output.headers.keys():
        v = output.headers[k]
        log.debug("Header %s=%s" % (k, v))

        if k.lower() == 'content-disposition':
            responseHeaders['Content-Disposition'] = v
            match = CONTENT_FILENAME_REGEX.search(v)
            try:
                responseHeaders['filename'] = match.group('filename')
            except IndexError:
                pass
        elif k.lower() == 'content-type':
            responseHeaders['Content-Type'] = v

    return (output.read(), responseHeaders)

def _getWCSObj(endpoint):
    """Contructs a WCS object for an endpoint.
    @param endpoint: endpoint URL
    @return WCS object
    """
    oldProxy = proxyFix(endpoint)
    try:

        log.debug("wcs endpoint = %s" % (endpoint,))

        getCapabilitiesEndpoint = parseEndpointString(endpoint, 
                                                      {'Service':'WCS', 'Request':'GetCapabilities'})

        log.debug("wcs endpoint = %s" % (getCapabilitiesEndpoint,))
        #requires OWSLib with cookie support
        wcs = WebCoverageService(getCapabilitiesEndpoint, version='1.0.0', cookies=request.headers.get('Cookie', ''))

        layers = [x[0] for x in wcs.items()]
    finally:
        resetProxy(oldProxy)

    return wcs, layers

def _getParams(params):
    """Process the input parameters, converting Unicode to strings.
    @param params: parameters to process
    @return dict of parameter names and values
    """
    outParams = {}
    for k in params.keys():
        value = params[k]
        if value == "":
            value = None

        if value.__class__ == unicode:
            value = value.encode('latin-1')

        outParams[k.upper()] = value

    return outParams
