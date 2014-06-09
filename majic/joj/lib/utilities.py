from collections import deque # python 2.4
try: #python 2.5
    from xml.etree import ElementTree as ET
except ImportError:
    try:
        # if you've installed it yourself it comes this way
        import ElementTree as ET
    except ImportError:
        # if you've egged it this is the way it comes
        from elementtree import ElementTree as ET
#from ndgUtils.ETxmlView import *

import ConfigParser, os, re, urllib, logging

log = logging.getLogger(__name__)

class myConfig:
    
    """
    Handle missing sections and variables in a config file a bit gracefully. 
    Also instantiates a logger if necessary
    """
   
    def __init__(self,configfile,logName='NDGLOG'):
        self.config=ConfigParser.ConfigParser()
        if not os.path.exists(configfile): 
            raise ValueError("Config file [%s] doesn't exist in [%s]"%(configfile,os.getcwd()))
        self.config.read(configfile)
        logfile=self.get('logging','debugLog',None)
        # move to a wsgi logger ... safer I think in a multithread environment
        # 
        #self.logfile=None #deprecated
        self.logger=None
        self.logfile=logfile
        #
        if logfile is not None:
            #logger=logging.getLogger(logName)
            #handler=logging.FileHandler(logfile)
            #formatter=logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            #handler.setFormatter(formatter)
            #logger.addHandler(handler)
            #logger.setLevel(logging.INFO)
            #self.logger=logger
            self.logger=None

    def get(self,section,key,default=None):
        ''' Return a config file value for key frm section '''
        
        try:
            return self.config.get(section,key)
        except:
            return default

    def log(self,string):
        ''' Log some debug information '''
        
        if self.logger is None: return
        
        if string is not None:
            self.logger.info(string)
        else:
            self.logger.info('empty log entry')
          
    def getLog(self):
        return self.logger

class RingBuffer(deque):
    #deque is a python 2.4 class!
    #credit http://www.onlamp.com/pub/a/python/excerpt/pythonckbk_chap1/index1.html
    def __init__(self, size_max):
        deque.__init__(self)
        self.size_max = size_max
    def append(self, datum):
        deque.append(self, datum)
        if len(self) > self.size_max:
            self.popleft( )
    def tolist(self):
        return list(self)
    def remove(self,value):
        try: # python 2.5
            deque.remove(self,value)
        except: # python 2.4
            #yuck, two copies ...
            x=self.tolist()
            x.remove(value)
            self.clear()
            for i in x:self.append(i)
            

def wrapGetText(element,xpathExpression,multiple=0):
    ''' Wraps a call to ET to get a text object in an error handler '''
    
    def none2txt(i):
        if i is None: return ''
        return i
    
    if element is None:
        if multiple:
            return ['',]
        else: 
            return ''
        
    if multiple:
        r=element.findall(xpathExpression)
    else:
        r=[element.find(xpathExpression),]
    
    try:
        rr=[i.text for i in r]
    except:
        rr=['',]
        rr=map(none2txt,rr)
         
    if multiple: 
        return rr
    else: 
        return rr[0] 

def getURLdict(cgiFieldStorage):
    ''' takes a cgi field storage object and converts it to a dictionary '''
    result={}
    for item in cgiFieldStorage:
            result[item]=cgiFieldStorage[item].value
    return result
##
### convert the followign two methods into one class that can handle
## xml directly too if necessary
##
def DIFid2NDGid(string):
    ''' takes a dif thing parses it and produces an ET ndg element id ...
    and use this in dif ... '''
    s=string.split(':')
    try:
        r='''<DIFid><schemeIdentifier>%s</schemeIdentifier>
         <repositoryIdentifier>%s</repositoryIdentifier>
         <localIdentifier>%s</localIdentifier></DIFid>'''%(s[1],s[0],s[2])
        return ET.fromstring(r)
    except:
        r='''<DIFid><schemeIdentifier>DIF</schemeIdentifier>
        <repositoryIdentifier>Unknown</repositoryIdentifier>
        <localIdentifier>%s</localIdentifier></DIFid>'''%string
        return ET.fromstring(r)

def EnumerateString(string):
    """ Takes a string, and if it's got a number on the end, increments it,
    otherwise adds a number on the end, used to differentiate strings which
    would otherwise be identical """
    def addNum(matchObj):
        s=matchObj.group()
        return str(int(s)+1)
    r=re.sub('\d+$',addNum,string)
    if r==string: r=r+'1'
    return r

def dateParse(string,instruction):
    ''' Simple date manipulations on a string, if it is understood ... 
       if instruction = YYYY, return the year '''
    s=string.split('-')
    if instruction=='YYYY':
        if len(s)==3: # expecting year,mon,day or day,mon,year ... 
            if int(s[0])>int(s[2]): 
                return s[0]
            else:
                return s[2]
        else:
            return string # unknown format as yet ...
    else:
        return 'unknown instruction to dateParse %s'%instruction

def idget(xml,dataType='DIF'):
    ''' Given an xml document (string), parse it using ElementTree and 
    find the identifier within it. Supports dataTypes of 'DIF' ...
    (actually only DIF for now).
    '''
    et=loadET(xml)
    helper=nsdumb(et)
    if dataType=='DIF':
        return helper.getText(et,'Entry_ID')
    else:
        raise TypeError,'idget does not support datatype [%s]'%dataType
    

def recreateListFromUnicode(string):
    ''' Parse a list that has been passed as unicode over http and
    recreate it in its list form
    '''
    if not string:
        return
    
    newList = []
    element = []
    for c in string:
        if c == '[' or c == ' ' or c == ']' or c == '\'':
            continue
        elif c == ',':
            if (len(element) > 0):
                newList.append(''.join(element))
                element = []
            continue
        element.append(c)

    # don't forget the last element
    if (len(element) > 0):
        newList.append(''.join(element))
        
    return newList

def isTabRequired(pageTabs, string):
    for tab in pageTabs:
        if tab[0] == string:
            return False
    
    return True
        

def urlListEncode(urlList):
    """
    Encode a list of URLs so that they can be embedded in another URL
    """
    return '|'.join(urllib.quote(x, '%') for x in urlList)

def urlListDecode(string):
    """
    Decode an encoded list of URLs.
    """
    return [urllib.unquote(x) for x in string.split('|')]

    
        
import unittest

class TestCase(unittest.TestCase):
    """ Tests as required """

    configFile='examples/example.config'
    difFile='examples/neodc.eg1.dif'
    
    def setUp(self):
        # If pkg_resources is available assume the module is eggified and
        # get a stream to the input data from the egg.
        #try:
        #    import pkg_resources
        #    f = pkg_resources.resource_stream(__name__, self.configFile)
        #except ImportError:
            # Else take the input file from __file__
            #import os
        self.config=myConfig(self.configFile)
        f=file(self.difFile,'r')
        self.difxml=f.read()
            #f=file(os.path.join(os.path.basepath(__file__), self.configFile))

        #self.config=myConfig(f)

    def testConfig(self):
        print 'Discovery Icon [%s]'%self.config.get('DISCOVERY','icon')
        
    def testidget(self):
        self.assertEqual(idget(self.difxml),'NOCSDAT192')


if __name__=="__main__":
    unittest.main()



