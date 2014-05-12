import re
import logging

log = logging.getLogger(__name__)

class DateTimeOptionsBuilder(object):
    
    format = '%(years)s-%(months)s-%(days)sT%(times)s'
    isoDateTimePattern = re.compile("(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2}.\d)")

    
    def __init__(self, dateTimeVals):
        self.dateTimeVals = dateTimeVals
        
    def buildOptions(self):
        ret = self._buildOptions()
        
        #if the options couldn't be reduced then return the input list
        if ret == False:
            ret = self.dateTimeVals
                            
        return ret
        
    def _buildOptions(self):
        
        #check all times are unique
        
        if not isListUnique(self.dateTimeVals):
            return False
        
        #get all the time/days/months/years
        d = {'years':[], 'months':[], 'days':[], 'times':[]}
        
        for dt in self.dateTimeVals:
            match = DateTimeOptionsBuilder.isoDateTimePattern.match(dt)
            
            if match == None:
                return False
                       
            d['years'].append(match.group(1))
            d['months'].append(match.group(2))
            d['days'].append(match.group(3))
            d['times'].append(match.group(4))

        # find only the unique time/days/months/years
        for k,v in d.items():
            d[k] = getUniqueList(v)
        
        #check that all possible combinations are made, 
#        log.debug("d = %s" % (d,))
        
        lengths = [len(d[k]) for k in d.keys()]
        x = reduce(lambda x, y: x*y, lengths)
#        log.debug("lengths = %s" % (lengths,))
#        log.debug("x = %s" % (x,))
#        log.debug("len(self.dateTimeVals) = %s" % (len(self.dateTimeVals),))
        
        if x != len(self.dateTimeVals):
            return False
        
        d['_fmt'] = DateTimeOptionsBuilder.format
        
        return d
 
def isListUnique(items):
    seen = {}
    
    for item in items:
        if item in seen:
            return False
        
        seen[item] = 1
        
    return True           
 
def getUniqueList(items):
    seen = {}
    l = []
    for item in items:
        if item in seen:
            continue
        
        seen[item] = 1
        l.append(item)
        
    return l
                
if __name__ == '__main__':
    import unittest
    from ecomaps.tests.test_date_time_options_builder import suite
    
    from ecomaps.tests import TEST_LOG_FORMAT_STRING
    logging.basicConfig(level=logging.DEBUG, format=TEST_LOG_FORMAT_STRING)
    
    unittest.TextTestRunner(verbosity=2).run(suite())
