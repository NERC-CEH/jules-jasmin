'''
Created on 14 Dec 2009

This contains a list of all the js files needed on each of the templates. The 
advantage of listing it here instead of on the template is that here it can be 
used by the script that runs jslint + compresses all the javascript.

All file paths are given relative to the 'js' folder in the public directory.

@author: pnorton
'''

_jsFiles = {
    'wmsviz': [
        'wmsc.js',
        'utils.js',
        'endpoint.js',
        'furtherInfoLink.js',
        'displayOptionsRetriever.js',
        'mapControl.js',
        'layerControl.js',
        'capabilities.js',
        'wcs.js',
        'layerFigureDownload.js',
        'layerInformation.js',
        'layerList.js',
        'layerDisplayOptions.js',
        'splitAxisConfig.js',
        'splitAxisSelect.js',
        'endpointSelection.js',
        'ajaxRetriever.js',
        'axisConfigRetriever.js',
        'layerDimensions.js',
        'layerParameters.js',
        'figureBuilder.js',
        'legendContainer.js',
        'boundsControl.js',
        'wmcRetriever.js',
        'layerDefaultSetter.js',
        'outlineControl.js'
    ],
    'wcsdown':
    [
      '',
    ],
}

def getJSFilesForPage(page):
    return _jsFiles[page]