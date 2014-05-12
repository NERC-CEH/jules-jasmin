import unittest
import logging
from mock import Mock, patch
from ConfigParser import SafeConfigParser

import ecomaps.lib.config_file_parser as config_file_parser

log = logging.getLogger(__name__)

class TestDisplayOptionsConfig(unittest.TestCase):

    def setUp(self):
        
        self.path = "some/path/to/config.ini"
        
        self.options = {
            'page1': {'default_rules': 'set1,set2', 'hide_rules': 'set3,set4'},
            'DefaultOption:set1':{'endpoint':'ep1', 'layers':'l1', 'values':'a|1,b|2' },
            'DefaultOption:set2':{'endpoint':'ep2', 'layers':'l2,l3', 'values':'a|1' },
            'HideOption:set3':{'endpoint':'ep1', 'options':'opt1'},
            'HideOption:set4':{'endpoint':'ep2', 'options':'opt2a, opt2b'}
            }
         
        self.builder = config_file_parser.DisplayOptionsConfigParser()
        self.builder._config = Mock(spec=SafeConfigParser)
        #print self.builder._config._methods
        
        self.builder.filePath = self.path
        self.builder._config.has_section = lambda section: section in self.options
        self.builder._config.has_option = lambda section, option: option in self.options[section]
        self.builder._config.sections = lambda section: self.options.keys()
        self.builder._config.get = lambda section, option: self.options[section][option]
        self.builder._config.options.side_effect = lambda section: self.options[section].keys()

    def tearDown(self):
        pass
    
    @patch('ecomaps.lib.config_file_parser.config')
    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_001_returnsEmptyWhenNoSections(self, mockConfig, mockOsExists):
        mockOsExists.return_value = True
        mockConfig.get.return_value = self.path
        self.options = {'page1': {'default_rules': '', 'hide_rules': ''}}
        
        defaultOptions = self.builder.getDefaultOptions('page1')
        log.debug("defaultOptions: " + defaultOptions.__repr__())
        assert self.builder.getDefaultOptions('page1') == []
        assert self.builder.getHideOptions('page1') == []
        
    @patch('ecomaps.lib.config_file_parser.config')
    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_002_callsReadOnPath(self, mockConfig, mockOsExists):
        mockOsExists.return_value = True
        mockConfig.get.return_value = self.path

        options = self.builder.getDefaultOptions('page1');
        
        assert self.builder._config.read.call_count == 1
        
        self.builder._config.read.assert_called_with(self.path)
        
    @patch('ecomaps.lib.config_file_parser.config')
    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_003_createsHideOptions(self, mockConfig, mockOsExists):
        
        mockOsExists.return_value = True
        mockConfig.get.return_value = self.path
        
        options = self.builder.getHideOptions('page1');
        
        assert options == [
            {'endpoint':'ep1', 'options':['opt1']},
            {'endpoint':'ep2', 'options':['opt2a', 'opt2b']},
            ]
        
        
    @patch('ecomaps.lib.config_file_parser.config')
    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_004_createsDefaultOptions(self, mockConfig, mockOsExists):
        
        options = self.builder.getDefaultOptions('page1');
        
        assert options == [
            {'endpoint':'ep1', 'layers':['l1'], 'values':{'a':'1','b':'2'}},
            {'endpoint':'ep2', 'layers':['l2', 'l3'], 'values':{'a':'1'}},
            ]
        
        
                

def suite():
    suite = unittest.TestSuite()

    #use all methods that start with 'test' to make the suite
    suite.addTest(unittest.makeSuite(TestDisplayOptionsConfig))

    #suite.addTest(TestDateTimeOptionsBuilder("test_003_repeatedAll"))

    return suite
    
if __name__ == '__main__':
    import logging
    from ecomaps.tests import TEST_LOG_FORMAT_STRING
    logging.basicConfig(level=logging.DEBUG, format=TEST_LOG_FORMAT_STRING)
    
    s = suite()
    unittest.TextTestRunner(verbosity=1).run(s)
