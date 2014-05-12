import unittest
import nose
import nose.tools as nt

from mock import Mock, patch
from ConfigParser import SafeConfigParser

import ecomaps.lib.config_file_parser as config_file_parser

class TestEndpointConfigParser(unittest.TestCase):

    def setUp(self):
        pass
                    
    def tearDown(self):
        pass
    
    @patch('ecomaps.lib.config_file_parser.config')
    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_001_buildsItemsList(self, mockOsExists, mockConfig):
       
        mockOsExists.return_value = True
        mockConfig.get.return_value = 'endpoint_file.ini'
        self.parser = config_file_parser.EndpointConfigFileParser()
        
        self.config_data = {
            'page':{'keys':'a,b'},
            'Endpoint:a':{'service':'WMS','url':'url1','name':'url_name'},
            'Endpoint:b':{'service':'COWS','url':'url2',},
            }
        
        def conf_get(section,option):
            return self.config_data[section][option] 
        
        def conf_opts(section):
            return self.config_data[section].keys()
        
        self.parser._config = Mock(spec=SafeConfigParser)
        self.parser._config.has_section.return_value = True
        self.parser._config.has_option.return_value = True
        self.parser._config.get.side_effect = conf_get
        self.parser._config.options.side_effect = conf_opts
        
        itemList = self.parser.buildEndpointList('page')

        nt.assert_equal(len(itemList), 2)
        # the order should be the order from the 'page','options' string
        nt.assert_equal(itemList[0], self.config_data['Endpoint:a'])
        nt.assert_equal(itemList[1], self.config_data['Endpoint:b'])
        
    @patch('ecomaps.lib.config_file_parser.config')
    def test_002_readsPathFromConfigFile(self, mockConfig):
        
        mockConfig.get.return_value = "endpoint_file.ini"
        self.parser = config_file_parser.EndpointConfigFileParser()
        
        nt.assert_equal(self.parser.filePath, mockConfig.get.return_value)
        mockConfig.get.assert_called_with('endpointConfig', None)
        
        
if __name__ == '__main__':   
    nose.runmodule()
