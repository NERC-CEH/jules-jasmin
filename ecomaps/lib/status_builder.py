'''
Created on 7 Oct 2009

@author: pnorton
'''

import re
import ecomaps.lib.utils as utils
import ecomaps.lib.config_file_parser as config_file_parser
from ConfigParser import NoOptionError, NoSectionError
from ecomaps.lib.base import config
import logging

log = logging.getLogger(__name__)

class StatusBuilder(object):
    '''
    Extracts the initial setup information from the config file and the session
    and uses it to generate the initial setup json to be used by the javascript
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.fiparser = config_file_parser.FurtherInfoConfigParser()
        self.displayOptionsParser = config_file_parser.DisplayOptionsConfigParser()
        self.userInterfaceConfigParser = config_file_parser.UserInterfaceConfigParser()
    
    def getCurrentStatus(self, page=None):
        
        status = {}
        
        status['WMSEndpointsList'] = self._getWMSEndpointList()
            
        status['HiddenDisplayOptions'] = self._getHiddenDisplayOptions()
        
        status['DefaultLayerParms'] = self._getDefaultParams()
                
        status['OutlineSettings'] = self._getOutlineSettings()
        
        status['FurtherInfoLinks'] = self._getFurtherInfoLinks(page)

        status['ViewDataUserInterfaceConfig'] = self._getUserInterfaceConfig('viewdata')
        
        status['CustomTextOptions'] = self._getCustomTextOptions()
                
        status['AnimationOptions'] = self._getAnimationOptions()
                
        status['BannerOptions'] = self._getBannerOptions()
                
        status['FigureOptions'] = self._getFigureOptions()
                
        status['LogoOptions'] = self._getLogoOptions()
                
        status['MapOptions'] = self._getMapOptions()
                
        status['DataOptions'] = self._getDataOptions()
                
        #log.debug('STATUS CUSTOM TEXT %s'%status['CustomTextOptions'])
        return status
        
    
    def _getWMSEndpointList(self):
        
        econfig = config_file_parser.EndpointConfigFileParser()
        
        endpointList = econfig.buildEndpointList('wmsviz')
        log.debug("endpointList = %s" % (endpointList,))
        
        wmsList = []
        
        if endpointList is not None:
            for e in endpointList:
                if e['service'] == 'COWS':
                    try:
                        for linkName, linkDict in utils.parseCowsCatalog(e['url']):
                            if 'WMS' in linkDict.keys():
                                wmsList.append(
                                    {'service':'WMS', 
                                     'url':linkDict['WMS'], 
                                     'name':linkName}
                                )
                    except:
                        log.exception("An error occurred while reading cows catalog at %s"\
                                      % (e['url'],))
                            
                elif e['service'] == 'WMS':
                    wmsList.append(e)
                
        return wmsList
    
    def _getHiddenDisplayOptions(self):
        return self.displayOptionsParser.getHideOptions('wmsviz')

    def _getDefaultParams(self):
        return self.displayOptionsParser.getDefaultOptions('wmsviz')        

    def _getOutlineSettings(self):
        
        outlineConfigParser = config_file_parser.OutlineLayersConfigParser()
        
        return outlineConfigParser.getOutlineLayer('wmsviz')
#    
    def _getFurtherInfoLinks(self, sectionName):
        return self.fiparser.getFurtherInfoItems('wmsviz')
    
    def _getUserInterfaceConfig(self, page):
        return self.userInterfaceConfigParser.getUserInterfaceOptions(page)

    def _getCustomTextOptions(self):
        CustomTextOptions = {}
        CustomTextOptions['abouttext'] = self._getUserInterfaceOption('customtext', 'abouttext', '', concatenateLines=True)
        CustomTextOptions['maptitle'] = self._getUserInterfaceOption('customtext', 'maptitle', 'Map')
        return CustomTextOptions

    def _getAnimationOptions(self):
        """Returns the options from the animation section.
        """
        animationOptions = {}
        animationOptions['minheight'] = self._getUserInterfaceOption('animation', 'height.min', 200)
        animationOptions['maxheight'] = self._getUserInterfaceOption('animation', 'height.max', 2048)
        animationOptions['defaultheight'] = self._getUserInterfaceOption('animation', 'height.default', 900)
        animationOptions['minwidth'] = self._getUserInterfaceOption('animation', 'width.min', 200)
        animationOptions['maxwidth'] = self._getUserInterfaceOption('animation', 'width.max', 2048)
        animationOptions['defaultwidth'] = self._getUserInterfaceOption('animation', 'width.default', 1200)
        animationOptions['maxnumbersteps'] = self._getUserInterfaceOption('animation', 'numbersteps.max', 100)
        animationOptions['defaultnumbersteps'] = self._getUserInterfaceOption('animation', 'numbersteps.default', 5)
        animationOptions['browsertimeout'] = self._getUserInterfaceOption('animation', 'browser.timeout', 300)
        animationOptions['style'] = self._getUserInterfaceOption('animation', 'style', '')
        return animationOptions

    def _getBannerOptions(self):
        """Returns the options from the banner section.
        """
        bannerOptions = {}
        bannerOptions['height'] = self._getUserInterfaceOption('banner', 'height', 125)
        bannerOptions['html'] = self._getUserInterfaceOption('banner', 'html', '', concatenateLines=True)
        bannerOptions['style'] = self._getUserInterfaceOption('banner', 'style', '')
        return bannerOptions

    def _getFigureOptions(self):
        """Returns the options from the figure section.
        """
        figureOptions = {}
        figureOptions['minheight'] = self._getUserInterfaceOption('figure', 'height.min', 200)
        figureOptions['maxheight'] = self._getUserInterfaceOption('figure', 'height.max', 2048)
        figureOptions['defaultheight'] = self._getUserInterfaceOption('figure', 'height.default', 900)
        figureOptions['minwidth'] = self._getUserInterfaceOption('figure', 'width.min', 200)
        figureOptions['maxwidth'] = self._getUserInterfaceOption('figure', 'width.max', 2048)
        figureOptions['defaultwidth'] = self._getUserInterfaceOption('figure', 'width.default', 1200)
        figureOptions['style'] = self._getUserInterfaceOption('figure', 'style', '')
        return figureOptions

    def _getLogoOptions(self):
        """Returns the options from the logo section.
        """
        logoOptions = {}
        logoOptions['height'] = self._getUserInterfaceOption('logo', 'height', 95)
        logoOptions['html'] = self._getUserInterfaceOption('logo', 'html', '', concatenateLines=True)
        logoOptions['style'] = self._getUserInterfaceOption('logo', 'style', '')
        return logoOptions

    def _getMapOptions(self):
        """Returns the options from the map section.
        """
        mapOptions = {}
        mapOptions['tilesize'] = self._getUserInterfaceOption('map', 'tilesize', None)
        mapOptions['numberZoomLevels'] = self._getUserInterfaceOption('map', 'numberzoomlevels', None)
        return mapOptions

    def _getDataOptions(self):
        """Returns the options from the data section.
        """
        dataOptions = {}
        dataOptions['maxnumbersteps'] = self._getUserInterfaceOption('data', 'numbersteps.max', 100)
        dataOptions['defaultnumbersteps'] = self._getUserInterfaceOption('data', 'numbersteps.default', 5)
        dataOptions['browsertimeout'] = self._getUserInterfaceOption('data', 'browser.timeout', 300)
        return dataOptions

    def _getUserInterfaceOption(self, section, option, default, concatenateLines=False):
        """Returns the value of an option in a section, or a default value if the option is not
        found.
        """
        try:
            result = self.userInterfaceConfigParser.getConfigOption(section, option)
        except (NoOptionError, NoSectionError, TypeError):
            result = default
        # This can be used to allow multi-line values in the configuration file, but collapse it to
        # a single line for JSON parsing.
        if concatenateLines:
            result = re.sub('[\n\r]+', ' ', result)
        return result
        
"""
initialStatusObject (made of primatives so it can be transformed into json

{
    'HideDisplayOptions':xxx,
    'DefaultDisplayOptions':xxx,
    'WMSEndpointsList':xxx,
    'baselayerParams':xxx,
    'baselayerUrl':xxx,
    'selectedEndpoints':xxx,
    'selectedLayers':xxx,
}

"""
