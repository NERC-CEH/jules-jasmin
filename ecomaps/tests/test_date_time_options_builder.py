import unittest

from ecomaps.model.date_time_options import DateTimeOptionsBuilder

class TestDateTimeOptionsBuilder(unittest.TestCase):

    def setUp(self):
        self.years  = ['1990','1991','1992','1993', '1994', '1995']
        self.months = ["%02i"%x for x in range(1,13)]
        self.days   = ["%02i"%x for x in range(1,31)]
        self.times  = ["09:30:00.0", "12:00:00.0", "15:45:00.0"]
        
        self.timeList = self.buildTimes(self.years, self.months, self.days, self.times)
        self.builder = DateTimeOptionsBuilder(self.timeList)        
        
    def tearDown(self):
        pass

    def buildTimes(self, years, months, days, times, format="%(year)s-%(month)s-%(day)sT%(time)s"):
        
        tList = []
        
        for y in years:
            for m in months:
                for d in days:
                    for t in times:
                        tList.append(format % {'year':y, 'month':m, 'day':d, 'time':t})
                        
        return tList
                        
    def test_001_regexPatternMatchesValid(self):
        timeList = self.buildTimes(self.years, self.months, self.days, self.times)
        
        for ti in timeList:
            assert DateTimeOptionsBuilder.isoDateTimePattern.match(ti) != None
        
    def test_002_rexexPatternNotMatchesInvalid(self):
        l = ['1995-12-30 09:30:00.0','1995-12-30','1995-dec-30T15:45:00.0']
        
        for ti in l:
            assert DateTimeOptionsBuilder.isoDateTimePattern.match(ti) == None

    def test_003_repeatedAll(self):
        
        resTimeOpts = self.builder.buildOptions()
        
        assert resTimeOpts.__class__ == dict
        
        assert resTimeOpts['years'] == self.years
        assert resTimeOpts['months'] == self.months
        assert resTimeOpts['days'] == self.days
        assert resTimeOpts['times'] == self.times

    def test_004_notAllOptions(self):
        
        #check it spots not all combinations used
        timeList = ['2001-05-10T12:00:00.0',
                    '2002-06-10T12:00:00.0',
                    '2003-05-10T12:00:00.0',
                    '2004-06-11T12:00:00.0',
                    '2005-05-11T12:00:00.0',
                    '2006-06-11T12:00:00.0',
                    '2001-05-12T12:00:00.0',
                    '2002-06-12T12:00:00.0',
                    '2003-05-12T12:00:00.0',
                    '2004-06-13T12:00:00.0',
                    '2005-05-13T12:00:00.0',
                    '2006-06-13T12:00:00.0', ]
        
        builder = DateTimeOptionsBuilder(timeList)
        
        assert builder.buildOptions() == timeList

    def test_005_notAllTimesUnique(self):
        
        timeList = self.timeList
        timeList.append(self.timeList[0])
        
        builder = DateTimeOptionsBuilder(timeList)
        
        assert builder.buildOptions() == timeList
        

def suite():
    suite = unittest.TestSuite()

    #use all methods that start with 'test' to make the suite
    suite.addTest(unittest.makeSuite(TestDateTimeOptionsBuilder))

    #suite.addTest(TestDateTimeOptionsBuilder("test_003_repeatedAll"))

    return suite
    
if __name__ == '__main__':
    import logging
    from ecomaps.tests import TEST_LOG_FORMAT_STRING
    logging.basicConfig(level=logging.DEBUG, format=TEST_LOG_FORMAT_STRING)
    
    s = suite()
    unittest.TextTestRunner(verbosity=1).run(s)