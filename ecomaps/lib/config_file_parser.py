'''
Created on 12 Nov 2009

@author: pnorton
'''

from ecomaps.lib.base import config

from ConfigParser import SafeConfigParser
import logging
import os
import urllib

log = logging.getLogger(__name__)

class ParamNotFoundException(Exception):
    def _get_message(self): 
        return self._message

    def _set_message(self, message): 
        self._message = message

    message = property(_get_message, _set_message)

    def __init__(self, *args):
        self.message = args[0]
        Exception.__init__(self, args)

    def __str__(self):
        return repr(self.message)

class ConfigFileParser(object):
    
    def __init__(self, filePath):
        self.filePath = filePath
        self._config = SafeConfigParser()
        self.config=self._config #there's no need to have the raw config parser object as an internal attribute - it's too useful externally
        #however left _config for backwards compatibility
        self._returnDict = False
        self.fileRead = False

    def buildList(self, page, pageOption, itemPrefix, requiredParams=None):
        """Returns a list of items for a specified page option.
        """
        return self._readAndBuildCollectionForPage(page, pageOption, itemPrefix, requiredParams)

    def buildDict(self, page, pageOption, itemPrefix, requiredParams=None):
        """Returns a dictionary of items for a specified page option.
        """
        self._returnDict = True

        return self._readAndBuildCollectionForPage(page, pageOption, itemPrefix, requiredParams)
    
    def getConfigOption(self, section, option):
        if not self._readConfigFile():
            return None
        return  self._config.get(section, option)

    def _readConfigFile(self):
        """Reads the configuration file if not done so already.
        """
        if not self.fileRead:
            if not os.path.exists(self.filePath):
                log.warning("config file %s not found." % (self.filePath,))
                return False

            self._config.read(self.filePath)
            log.debug("Read config file %s" % self.filePath)
            self.fileRead = True
        return True

    def _readAndBuildCollectionForPage(self, page, pageOption, itemPrefix, requiredParams=None):

        if requiredParams is None:
            requiredParams = [];
        
        if self.filePath == None:
            return None

        if not self._readConfigFile():
            return None

        return self._buildCollectionForPage(page, pageOption, itemPrefix, requiredParams)

    def buildListForItem(self, page, pageOption):
        """Returns a list of items specified by the value of an option of a section for a page.
        """
        if not self._readConfigFile():
            return None
        return self._buildListForItem(page, pageOption)

    def _buildListForItem(self, page, pageOption):
        if not self._config.has_section(page):
            log.warning("section for page '%s' not found in file %s" \
                                           % (page, self.filePath))
            return None
        
        if not self._config.has_option(page, pageOption):
            log.warning("option %s not found for page %s in file %s" \
                                           % (pageOption, page, self.filePath))
            return None
        
        option = self._config.get(page, pageOption)
        if option.strip() == '':
            itemKeys = []
        else:
            itemKeys = [x.strip() for x in self._config.get(page, pageOption).split(',')]

        return itemKeys

    def _buildCollectionForPage(self, page, pageOption, itemPrefix, requiredParams):
        
        itemKeys = self._buildListForItem(page, pageOption)
        
        return self._buildItemCollection(itemPrefix, itemKeys, requiredParams)
    
    def buildItemDict(self, itemPrefix, itemKeys, requiredParams):
        """Returns a dictionary of items specified by a list of item keys and a prefix for the item section names.
        """
        if not self._readConfigFile():
            return None
        self._returnDict = True
        return self._buildItemCollection(itemPrefix, itemKeys, requiredParams)

    def _buildItemCollection(self, itemPrefix, itemKeys, requiredParams):
        
        if self._returnDict:
            retValue = {}
        else:
            retValue = []
        
        for key in itemKeys:
            sectionName = itemPrefix + ':' + key

            if self._config.has_section(sectionName):
                try:
                    item = self._getItemFromSection(sectionName, requiredParams)
                except ParamNotFoundException, e:
                    log.warning(e.message);
                else:
                    if self._returnDict:
                        retValue[key] = item
                    else:
                        retValue.append(item)
            else:
                log.warning("named section %s was not found in file %s." % (sectionName, self.filePath))
                
        return retValue
    
    def _getItemFromSection(self, sectionName, requiredParams):
        """
        Builds the item from the given section name
        """
        item = self._buildItemDictFromSection(sectionName)
        
        self._checkForRequiredParams(item, sectionName, requiredParams)
        
        return item 
    
    def _buildItemDictFromSection(self, sectionName):
        item = {}
        
        for opt in self._config.options(sectionName):
            item[opt] = self._config.get(sectionName, opt)
        
        return item
    
    def _checkForRequiredParams(self, item, sectionName, requiredParams):
        for p in requiredParams:
            if p not in item:
                msg = self._getParamWarn(p, sectionName)
                raise ParamNotFoundException(msg)
    
    def _getParamWarn(self, param, section):
        "Returns a warning string about a parameter not being found in the given section"
        return "Required parameter '%s' not found in section '%s' of %s" % (param, section, self.filePath)
    
class EndpointConfigFileParser(ConfigFileParser):
    
    def __init__(self):
        ConfigFileParser.__init__(self, config.get('endpointConfig', None))
        log.debug("Read %s", config.get('endpointConfig', None))
        
    def buildEndpointList(self, page):
        return self.buildList(page, 'keys', 'Endpoint', ['service','url'])
        
    def _getItemFromSection(self, sectionName, requiredParams):
        log.debug("requiredParams = %s" % (requiredParams,))
        item = self._buildItemDictFromSection(sectionName)
        log.debug("item = %s" % (item,))
        self._checkForRequiredParams(item, sectionName, requiredParams)
                
        # all endpoints other than cows ones require a name
        if item['service'] != 'COWS':
            self._checkForRequiredParams(item, sectionName, ['name'])
           
            item['name'] = self._config.get(sectionName, 'name')
            
        return item
    
class OutlineLayersConfigParser(ConfigFileParser):
    def __init__(self):
        ConfigFileParser.__init__(self, config.get('outlineConfig', None))
        
    def getOutlineLayer(self, page):
        
        outlineList = self.buildList(page, 'outline', 'LayerConfig', ['params','url'])
        
        if not outlineList is None:
            return outlineList[0]
        else:
            return None
    
    def getOutlineLayerList(self, page):
        return self.buildList(page, 'outline', 'LayerConfig', ['params','url'])
        
    def _getItemFromSection(self, sectionName, requiredParams):
        """
        Builds the item from the given section name
        """
        item = self._buildItemDictFromSection(sectionName)
        
        self._checkForRequiredParams(item, sectionName, requiredParams)
        
        params = {}
        
        for paramString in item['params'].split(','):
            key, value = paramString.split(':')
            params[key] = value
            
        item['params'] = params
        
        return item

class FurtherInfoConfigParser(ConfigFileParser):
    def __init__(self):
        ConfigFileParser.__init__(self, config.get('furtherInfoConfig', None))
        
    def getFurtherInfoItems(self, page):
        return self.buildList(page, 'keys', 'FurtherInfo', ['endpoint', 'link'])
    

class DisplayOptionsConfigParser(ConfigFileParser):
    def __init__(self):
        ConfigFileParser.__init__(self, config.get('displayOptionsConfig', None))
        
    def getDefaultOptions(self, page):
        return self.buildList(page, 'default_rules', 'DefaultOption', ['endpoint','layers','values'])
    
    def getHideOptions(self, page):
        return self.buildList(page, 'hide_rules', 'HideOption', ['endpoint', 'options'])

    def _getItemFromSection(self, sectionName, requiredParams):
        """
        Builds the item from the given section name
        """
        item = self._buildItemDictFromSection(sectionName)
        
        self._checkForRequiredParams(item, sectionName, requiredParams)
        
        if sectionName.find('HideOption') == 0:
            item['options'] = item['options'].split(',')
            item['options'] = [x.strip() for x in item['options']]
            
        if sectionName.find('DefaultOption') == 0:
            item['layers'] = item['layers'].split(',')
            item['layers'] = [x.strip() for x in item['layers']]
            item['values'] = self._buildDefaultValuesDict(item['values'])
            
        item['endpoint'] = item['endpoint'].strip()
        return item
     
    def _buildDefaultValuesDict(self, defaultValsString):
        d = {}
        for defaultItem in defaultValsString.split(','):
            log.debug("defaultItem = %s" % (defaultItem,))
            key, value = defaultItem.split('|')
            d[key.strip()] = urllib.unquote(value.strip())
            
        return d    


class UserInterfaceConfigParser(ConfigFileParser):
    """Parses the user interface configuration options.
    """
    def __init__(self):
        ConfigFileParser.__init__(self, config.get('userInterfaceConfig', None))

    def getUserInterfaceOptions(self, page):
        return self.buildDict(page, 'features', 'feature', [])


class HelpTextConfigParser(ConfigFileParser):
    """Parses the help text configuration file.
    """
    def __init__(self):
        ConfigFileParser.__init__(self, config.get('helpTextConfig', None))

    def getHelpText(self):
        """Parses the help text file and returns a dictionary of the help items found.
        """
        if self.filePath:
            self._config.read(self.filePath)
            if self._config.has_section('helptext'):
                return self._buildItemDictFromSection('helptext')
        else:
            return {}
