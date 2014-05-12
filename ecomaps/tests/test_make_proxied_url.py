'''
Created on 3 Apr 2012

@author: rwilkinson
'''
import unittest
import nose

from ecomaps.lib.wms_capability_reader import WmsCapabilityReader

class TestMakeProxiedUrl(unittest.TestCase):
    """Tests for WmsCapabilityReader.makeProxiedUrl
    """
    # No proxy URL defined
    def test01(self):
        reader = WmsCapabilityReader({'proxyUrl': None})
        self.assertEqual(reader.makeProxiedUrl('http://datahost.ac.uk'),
                         'http://datahost.ac.uk')

    def test02(self):
        reader = WmsCapabilityReader({})
        self.assertEqual(reader.makeProxiedUrl('http://datahost.ac.uk/'),
                         'http://datahost.ac.uk/')

    # Proxy URL defined
    def test03(self):
        reader = WmsCapabilityReader({'proxyUrl': 'http://proxyhost.ac.uk/proxy'})
        self.assertEqual(reader.makeProxiedUrl('http://datahost.ac.uk'),
                         'http://proxyhost.ac.uk/proxy/http/datahost.ac.uk/-/')

    def test04(self):
        reader = WmsCapabilityReader({'proxyUrl': 'http://proxyhost.ac.uk:8080/proxy/'})
        self.assertEqual(reader.makeProxiedUrl('http://datahost.ac.uk/'),
                         'http://proxyhost.ac.uk:8080/proxy/http/datahost.ac.uk/-/')

    def test05(self):
        reader = WmsCapabilityReader({'proxyUrl': 'http://proxyhost.ac.uk:8080/'})
        self.assertEqual(reader.makeProxiedUrl('https://datahost.ac.uk:8443/protected/data?find=abc&more=other#frag'),
                         'http://proxyhost.ac.uk:8080/https/datahost.ac.uk/8443/protected/data?find=abc&more=other#frag')

if __name__ == '__main__':
    nose.runmodule()
