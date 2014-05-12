# python class to support methods on a WMC ... to conform with
# renderEntity etc ...
#
from ecomaps.lib.utilities import *
#from geoUtilities import *
#from ndgUtils.ETxmlView import loadET, nsdumb
#from ndgUtils.DocumentRetrieve import genericHTTP
import urllib

    
class WMC:
    ''' Simple representation of a WMC document  '''
    def __init__(self,url):
        
        self.url = url
        self.layers = []

        '''Initialise a python wmc, retrieving it from the specified URL '''
        #x=genericHTTP(proxyServer='http://wwwcache3.rl.ac.uk:8080/')  #TODO, store this in config
        x=genericHTTP()
        try:
            wmcDoc = x.get(url)
        except Exception, e:
            self.title = "Document could not be retrieved properly"
            return
        
        self.tree = loadET(wmcDoc) 
        
        # now try and interpret it 
        helper=nsdumb(self.tree)
        self.title=helper.getText(self.tree,'General/Title')

        #load up information about spatial bounding box 
        #self.bbox=Bounding(self.tree,helper,entity='WMC')
        
        layersTree = helper.find(self.tree, 'LayerList')
        if layersTree:
            # add each of the layer elements
            layerElements = layersTree.getchildren()
            for layer in layerElements:
                self.layers.append(WMCLayer(layer)) 
            
    def getAllLayers():
        layersData = []
        for child in self.layers:
            layersData.append(ET.tostring(child))
        return ''.join(layersData)


class WMCLayer:
    ''' Simple representation of a WMC layer '''
    def __init__(self, layerXML):
        
        self.xml = layerXML
        
        # Now extract the basic layer info - for easy retrieval in kid template
        helper=nsdumb(self.xml)
        self.name = helper.getText(self.xml, 'Name')
        # NB, there may be a better way of getting the href, but the nsdumb doesn't currently
        # support XPATH attribute functionality
        elem = helper.find(self.xml, 'Server/OnlineResource')
        for attribute in elem.attrib:
            if attribute.find('href') > -1:
                self.wmsURL = elem.attrib.get(attribute)
            


import unittest

class TestCase(unittest.TestCase):
    """
    """


if __name__=="__main__":
    unittest.main()

        
        