"""
Format captions for figures

The figure caption style can be configured using the config. option
'caption_style'.  This option is interpreted by getCaption() to call a caption
formatting function in this module.

How to create a formatter
-------------------------

Create a function like formatObs() with the same arguments and add the
function to the _caption_formaters dictionary with a suitable key
name.  Select this style for a WMS by adding the following to
the WMS's configuration file:

caption_style: <formatter-key>


@author: Stephen Pascoe

"""

from datetime import datetime
import logging
import ecomaps.lib.date_util as date_util

logger = logging.getLogger(__name__)

months = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']

def formatObs(layerInfo, keywordData):
    field = layerInfo.layerName
    try:
        fieldcaption = keywordData['title']
    except KeyError:
        fieldcaption = field
    period = keywordData['period']
    time = date_util.iso2comptime(layerInfo.params['TIME'])
    today = datetime.today().strftime('%d %B, %Y')

    if period == '10':
        minYear = time.year - (time.year % 10) + 1
        maxYear = minYear + 9
    elif period == '30':
        minYear = time.year - ((time.year - 1900) % 30) + 1
        maxYear = minYear + 29
        
    
    
    caption = '''Observed %s, %s %s-%s mean.
Climatic Research Unit Climatology (New et al., 1999).
Figure obtained from www.ipcc-data.org. %s.''' % (fieldcaption, months[time.month-1],
                                                  minYear, maxYear,
                                                  today)

    return caption


def formatProj(layerInfo, keywordData):
    field = layerInfo.layerName
    time = date_util.iso2comptime(layerInfo.params['TIME'])
    try:
        fieldcaption = keywordData['varcaption']
    except KeyError:
        fieldcaption = field
    institute=keywordData['caption']
    model=keywordData['model']
    projection=keywordData['short']
    ref=keywordData['ref']
    today = datetime.today().strftime('%d %B, %Y')
    period = int(keywordData['period'])

    try:
        report = keywordData['report']
    except KeyError:
        report = 'IPCC 2007'

    # This algorithm is copied from the ddc javascript where it seems to work for AR4
    # there is a workaround for TAR that would need putting here too if we use formatProj
    # for the TAR data.
    dy = period / 2
    minYear = time.year - dy + 1
    maxYear = time.year - dy + period

    caption = '''%s, %s %s-%s mean.
Projected by the %s;
Scenario: %s (%s); Model %s (%s).
Figure obtained from www.ipcc-data.org. %s.''' % (fieldcaption, months[time.month-1],
                                                  minYear, maxYear,
                                                  institute,
                                                  projection, ref, model, report,
                                                  today)

    return caption
    
def formatSim(layerInfo, keywordData):
    field = layerInfo.layerName
    time = date_util.iso2comptime(layerInfo.params['TIME'])
    fieldcaption = keywordData['varcaption']
    institute=keywordData['caption']
    model=keywordData['model']
    projection=keywordData['short']
    ref=keywordData['ref']
    today = datetime.today().strftime('%d %B, %Y')
    period = int(keywordData['period'])

    # This algorithm is copied from the ddc javascript where it seems to work for AR4
    # there is a workaround for TAR that would need putting here too if we use formatProj
    # for the TAR data.
    dy = period / 2
    minYear = time.year - dy + 1
    maxYear = time.year - dy + period

    caption = '''%s, %s %s-%s mean.
Simulated by the %s; 
Scenario %s (%s); Model %s (IPCC 2007).
Figure obtained from www.ipcc-data.org. %s.''' % (fieldcaption, months[time.month-1],
                                                  minYear, maxYear,
                                                  institute,
                                                  projection, ref, model,
                                                  today)

    return caption
    
    
_caption_formatters = {
    'observation': formatObs,
    'projection': formatProj,
    'simulation': formatSim
    }

def getCaption(layerInfo, keywordData):
    """
    @param layerInfo: The layer data for the layer being plotted
    @param keywordData: A dictionary of keyword values for the layer

    """
    if layerInfo is None:
        return ''
    logger.info('Layer prefs = %s' % keywordData)

    try:
        captionStyle = keywordData['caption_style']
    except KeyError:
        logger.warn("No caption style found for layer %s" % `layerInfo.layerName`)
        return '%s at %s' % (layerInfo.layerName, layerInfo.params)

    try:
        formatter = _caption_formatters[captionStyle]
    except KeyError:
        logger.error("Caption style %s not recognised" % captionStyle)
        return '%s at %s' % (layerInfo.layerName, layerInfo.params)

    try:
        return formatter(layerInfo, keywordData)
    except KeyError:
        logger.exception("Caption formatting failed for layer %s" % `layerInfo.layerName`)
        return '%s at %s' % (layerInfo.layerName, layerInfo.params)
