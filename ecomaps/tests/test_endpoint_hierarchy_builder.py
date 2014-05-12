"""
Tests construction of the hierarchy of endpoint information.

@author: rwilkinson
"""

import unittest
import nose
import nose.tools as nt

from mock import Mock, patch
from ConfigParser import SafeConfigParser

import ecomaps.lib.endpoint_hierarchy_builder as endpoint_hierarchy_builder

class TestEndpointHierarchyBuilder(unittest.TestCase):

    def setUp(self):
        self.filepath = "/path/to/config/file.ini"
        self.config_data = {}

        self.parser = endpoint_hierarchy_builder.EndpointHierarchyBuilder(self.filepath)
        self.parser._config = Mock(spec=SafeConfigParser)
        self.parser._config.has_section = lambda section: section in self.config_data
        self.parser._config.has_option = lambda section, option: option in self.config_data[section]
        self.parser._config.sections = lambda section: self.config_data.keys()
        self.parser._config.get.side_effect = lambda section, option: self.config_data[section][option]
        self.parser._config.options.side_effect = lambda section: self.config_data[section].keys()

    def tearDown(self):
        pass

    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_001_buildsHierarchyForPage(self, mockOsExists):
        """Tests reading of valid configuration data with nested and un-nested datasets.
        """

        mockOsExists.return_value = True

        self.config_data = {
            'page1': {'keys': 'Data Category 1, Data Category 2'},

            'dataset:Data Category 1': {'datasets': 'set11, set12, set13'},
            'dataset:Data Category 2': {'datasets': 'set21, set22'},

            'dataset:set11': {'datasets': 'set111, set112, set113', 'title': 'Data Set 1.1', 'metadataLink': 'http://www.cat1.org/set11'},
            'dataset:set12': {'datasets': 'set121, set122, set123', 'title': 'Data Set 1.2', 'metadataLink': 'http://www.cat1.org/set12'},
            'dataset:set13': {'datasets': 'set131, set132, set133', 'title': 'Data Set 1.3', 'metadataLink': 'http://www.cat1.org/set13'},

            'dataset:set111': {'endpoints': 'ep1111, ep1112'},
            'dataset:set112': {'endpoints': 'ep1121, ep1122'},
            'dataset:set113': {'endpoints': 'ep1131, ep1132'},
            'dataset:set121': {'endpoints': 'ep1211, ep1212'},
            'dataset:set122': {'endpoints': 'ep1221, ep1222', 'title': 'Data Set 1.2.2', 'metadataLink': 'http://www.cat1.org/set122'},
            'dataset:set123': {'endpoints': 'ep1231, ep1232'},
            'dataset:set131': {'endpoints': 'ep1311, ep1312'},
            'dataset:set132': {'endpoints': 'ep1321, ep1322'},
            'dataset:set133': {'endpoints': 'ep1331, ep1332'},

            'endpoint:ep1111': {'wmsURL': 'http://www.cat1.org/ep1111/wms', 'name': 'Data Category 1: Data Set 1.1: Endpoint 1.1.1.1'},
            'endpoint:ep1112': {'wmsURL': 'http://www.cat1.org/ep1112/wms'},
            'endpoint:ep1121': {'wmsURL': 'http://www.cat1.org/ep1121/wms'},
            'endpoint:ep1122': {'wmsURL': 'http://www.cat1.org/ep1122/wms'},
            'endpoint:ep1131': {'wmsURL': 'http://www.cat1.org/ep1131/wms'},
            'endpoint:ep1132': {'wmsURL': 'http://www.cat1.org/ep1132/wms'},
            'endpoint:ep1211': {'wmsURL': 'http://www.cat1.org/ep1211/wms'},
            'endpoint:ep1212': {'wmsURL': 'http://www.cat1.org/ep1212/wms', 'name': 'Data Category 1: Data Set 2.1: Endpoint 1.2.1.2', 'newLayerNames': 'lay1:Layer 1\nlay2:Layer 2'},
            'endpoint:ep1221': {'wmsURL': 'http://www.cat1.org/ep1221/wms'},
            'endpoint:ep1222': {'wmsURL': 'http://www.cat1.org/ep1222/wms'},
            'endpoint:ep1231': {'wmsURL': 'http://www.cat1.org/ep1231/wms'},
            'endpoint:ep1232': {'wmsURL': 'http://www.cat1.org/ep1232/wms'},
            'endpoint:ep1311': {'wmsURL': 'http://www.cat1.org/ep1311/wms'},
            'endpoint:ep1312': {'wmsURL': 'http://www.cat1.org/ep1312/wms'},
            'endpoint:ep1321': {'wmsURL': 'http://www.cat1.org/ep1321/wms'},
            'endpoint:ep1322': {'wmsURL': 'http://www.cat1.org/ep1322/wms'},
            'endpoint:ep1331': {'wmsURL': 'http://www.cat1.org/ep1331/wms'},
            'endpoint:ep1332': {'wmsURL': 'http://www.cat1.org/ep1332/wms'},

            'dataset:set21': {'endpoints': 'ep211, ep212', 'title': 'Data Set 2.1', 'metadataLink': 'http://www.cat2.org/set21'},
            'dataset:set22': {'endpoints': 'ep211, ep222', 'title': 'Data Set 2.2', 'metadataLink': 'http://www.cat2.org/set22'},

            'endpoint:ep211': {'wmsURL': 'http://www.cat1.org/ep211/wms'},
            'endpoint:ep212': {'wmsURL': 'http://www.cat1.org/ep212/wms'},
            'endpoint:ep221': {'wmsURL': 'http://www.cat1.org/ep221/wms'},
            'endpoint:ep222': {'wmsURL': 'http://www.cat1.org/ep222/wms'}
            }

        self.parser.parsePage('page1')

        # Check the resulting map of IDs to node data.
        assert len(self.parser.idMap) == 39

        assert self.parser.idMap['ds:Data Category 1'].treeInfo['id'] == 'ds:Data Category 1'
        assert len(self.parser.idMap['ds:Data Category 1'].children) == 3
        assert self.parser.idMap['ds:Data Category 1'].treeInfo['id'] == 'ds:Data Category 1'
        assert self.parser.idMap['ds:Data Category 1'].treeInfo['text'] == 'Data Category 1'
        assert self.parser.idMap['ds:Data Category 1'].treeInfo['cls'] == 'folder'

        assert self.parser.idMap['ds:Data Category 2'].treeInfo['id'] == 'ds:Data Category 2'
        assert len(self.parser.idMap['ds:Data Category 2'].children) == 2
        assert self.parser.idMap['ds:Data Category 2'].treeInfo['id'] == 'ds:Data Category 2'
        assert self.parser.idMap['ds:Data Category 2'].treeInfo['text'] == 'Data Category 2'
        assert self.parser.idMap['ds:Data Category 2'].treeInfo['cls'] == 'folder'

        assert len(self.parser.idMap['ds:set11@ds:Data Category 1'].children) == 3
        assert len(self.parser.idMap['ds:set12@ds:Data Category 1'].children) == 3
        assert len(self.parser.idMap['ds:set13@ds:Data Category 1'].children) == 3
        assert len(self.parser.idMap['ds:set21@ds:Data Category 2'].children) == 2
        assert len(self.parser.idMap['ds:set22@ds:Data Category 2'].children) == 2

        assert self.parser.idMap['ds:set12@ds:Data Category 1'].id == 'ds:set12@ds:Data Category 1'
        assert self.parser.idMap['ds:set12@ds:Data Category 1'].entity['title'] == 'Data Set 1.2'
        assert self.parser.idMap['ds:set12@ds:Data Category 1'].entity['datasets'] == 'set121, set122, set123'
        assert self.parser.idMap['ds:set12@ds:Data Category 1'].entity['metadataLink'] == 'http://www.cat1.org/set12'
        assert self.parser.idMap['ds:set12@ds:Data Category 1'].treeInfo['id'] == 'ds:set12@ds:Data Category 1'
        assert self.parser.idMap['ds:set12@ds:Data Category 1'].treeInfo['text'] == 'Data Set 1.2'
        assert self.parser.idMap['ds:set12@ds:Data Category 1'].treeInfo['cls'] == 'folder'

        assert self.parser.idMap['ds:set122@ds:set12@ds:Data Category 1'].id == 'ds:set122@ds:set12@ds:Data Category 1'
        assert self.parser.idMap['ds:set122@ds:set12@ds:Data Category 1'].entity['title'] == 'Data Set 1.2.2'
        assert self.parser.idMap['ds:set122@ds:set12@ds:Data Category 1'].entity['endpoints'] == 'ep1221, ep1222'
        assert self.parser.idMap['ds:set122@ds:set12@ds:Data Category 1'].entity['metadataLink'] == 'http://www.cat1.org/set122'
        assert self.parser.idMap['ds:set122@ds:set12@ds:Data Category 1'].treeInfo['id'] == 'ds:set122@ds:set12@ds:Data Category 1'
        assert self.parser.idMap['ds:set122@ds:set12@ds:Data Category 1'].treeInfo['text'] == 'Data Set 1.2.2'
        assert self.parser.idMap['ds:set122@ds:set12@ds:Data Category 1'].treeInfo['cls'] == 'folder'

        assert self.parser.idMap['ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'].id == 'ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'
        assert self.parser.idMap['ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'].entity['name'] == 'Data Category 1: Data Set 2.1: Endpoint 1.2.1.2'
        assert self.parser.idMap['ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'].entity['wmsURL'] == 'http://www.cat1.org/ep1212/wms'
        assert self.parser.idMap['ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'].treeInfo['id'] == 'ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'
        assert self.parser.idMap['ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'].treeInfo['text'] == 'Data Category 1: Data Set 2.1: Endpoint 1.2.1.2'
        assert self.parser.idMap['ep:ep1212@ds:set121@ds:set12@ds:Data Category 1'].treeInfo['cls'] == 'folder'

    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_002_handlesCircularDatasetReferences(self, mockOsExists):
        """Tests handling of circular dataset references where a dataset references itself as a child.
        """

        mockOsExists.return_value = True

        self.config_data = {
            'page1': {'keys': 'Data Category 1'},
            'dataset:Data Category 1': {'datasets': 'set11'},
            'dataset:set11': {'datasets': 'set11', 'title': 'Data Set 1.1', 'metadataLink': 'http://www.cat1.org/set11'},
            }

        self.parser.parsePage('page1')

        assert len(self.parser.idMap['ds:Data Category 1'].children) == 1
        assert len(self.parser.idMap['ds:set11@ds:Data Category 1'].children) == 0

    @patch('ecomaps.lib.config_file_parser.os.path.exists')
    def test_003_handlesCircularDatasetReferences(self, mockOsExists):
        """Tests handling of circular dataset references where a dataset references its parent as a child.
        """

        mockOsExists.return_value = True

        self.config_data = {
            'page1': {'keys': 'Data Category 1'},
            'dataset:Data Category 1': {'datasets': 'set11'},
            'dataset:set11': {'datasets': 'set111', 'title': 'Data Set 1.1', 'metadataLink': 'http://www.cat1.org/set11'},
            'dataset:set111': {'datasets': 'set11', 'title': 'Data Set 1.1.1', 'metadataLink': 'http://www.cat1.org/set111'},
            }

        self.parser.parsePage('page1')

        assert len(self.parser.idMap['ds:Data Category 1'].children) == 1
        assert len(self.parser.idMap['ds:set11@ds:Data Category 1'].children) == 1
        assert len(self.parser.idMap['ds:set111@ds:set11@ds:Data Category 1'].children) == 0


if __name__ == '__main__':
    nose.runmodule()
