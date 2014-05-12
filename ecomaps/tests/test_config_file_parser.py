import unittest
import nose
import nose.tools as nt

from mock import Mock, patch
from ConfigParser import SafeConfigParser

import ecomaps.lib.config_file_parser as config_file_parser

class TestConfigFileParser(unittest.TestCase):

    def setUp(self):
        
        self.filepath = "/path/to/config/file.ini"
        self.parser = config_file_parser.ConfigFileParser(self.filepath)
                    
    def tearDown(self):
        pass
    
    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_001_buildsItemsList(self, mockOsExists):
       
        mockOsExists.return_value = True
        
        self.config_data = {
            'page':{'option':'a,c,b'},
            'Item:a':{'param1':'one', 'param2':'two',},
            'Item:b':{'a':'1', 'b':'2', 'c':'3'},
            'Item:c':{'alpha':'a', 'beta':'b',},
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
        
        itemList = self.parser.buildList('page', 'option', 'Item')

        nt.assert_equal(len(itemList), 3)
        # the order should be the order from the 'page','options' string
        nt.assert_equal(itemList[0], self.config_data['Item:a'])
        nt.assert_equal(itemList[1], self.config_data['Item:c'])
        nt.assert_equal(itemList[2], self.config_data['Item:b'])

    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_002_requiredParams(self, mockOsExists):
       
        mockOsExists.return_value = True       
    
        self.config_data = {
            'page':{'option':'one,two'},
            'Item:one':{'a':'1', 'b':'2'},
            'Item:two':{'a':'1', 'b':'2', 'c':'3'},
            
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
        
        itemList = self.parser.buildList('page', 'option', 'Item', ['a','b','c'])

        nt.assert_equal(len(itemList), 1)
        # the order should be the order from the 'page','options' string
        nt.assert_equal(itemList[0], self.config_data['Item:two'])
        
if __name__ == '__main__':   
    nose.runmodule()
