import unittest

import ecomaps.lib.dimension_format as dimension_format
from ecomaps.lib.dimension_format import DimensionFormat
from ecomaps.lib.dimension_format import DimensionFieldFormat

class TestDimensionFormat(unittest.TestCase):
    """
    Tests for the dimension_format module
    """
    def test_001_one_dimension(self):
        s = "time:'time':'{b} {Y:-9}-{Y:+10}'"
        r = {'time': DimensionFormat('time', [DimensionFieldFormat('{b} {Y:-9}-{Y:+10}', None)])}
        TestDimensionFormat.checkString(s, r)

    def test_002_one_dimension_no_format(self):
        s = "time:'time'::'TIME'"
        r = {'time': DimensionFormat('time', [DimensionFieldFormat(None, 'TIME')])}
        TestDimensionFormat.checkString(s, r)

    def test_003_one_dimension_no_label(self):
        s = "'time'::'{b} {Y:-9}-{Y:+10}'"
        r = {'time': DimensionFormat(None, [DimensionFieldFormat('{b} {Y:-9}-{Y:+10}', None)])}
        TestDimensionFormat.checkString(s, r)

    def test_004_one_dimension_no_label_or_format(self):
        s = "time:"
        r = {'time': DimensionFormat(None, [DimensionFieldFormat(None, None)])}
        TestDimensionFormat.checkString(s, r)

    def test_005_two_dimensions(self):
        s = "time:'time':'{b} {Y:-9}-{Y:+10}':'period', depth:'Depth below sea level'::'depth'"
        r = {'time': DimensionFormat('time', [DimensionFieldFormat('{b} {Y:-9}-{Y:+10}', 'period')]),
             'depth': DimensionFormat('Depth below sea level', [DimensionFieldFormat(None, 'depth')])}
        TestDimensionFormat.checkString(s, r)

    def test_006_one_dimension_two_formats(self):
        s = "time:Month:'{b}':month;'{Y:-9}-{Y:+10}':'years'"
        r = {'time': DimensionFormat('Month', [DimensionFieldFormat('{b}', 'month'),
                                               DimensionFieldFormat('{Y:-9}-{Y:+10}', 'years')])}
        TestDimensionFormat.checkString(s, r)

    def test_007_one_dimension_two_formats_no_labels(self):
        s = "time::'{b}';'{Y:-9}-{Y:+10}'"
        r = {'time': DimensionFormat(None, [DimensionFieldFormat('{b}', None),
                                            DimensionFieldFormat('{Y:-9}-{Y:+10}', None)])}
        TestDimensionFormat.checkString(s, r)

    def test_008_one_dimension_two_formats_one_label(self):
        s = "time:Date:'{b}':Month;'{Y:-9}-{Y:+10}'"
        r = {'time': DimensionFormat('Date', [DimensionFieldFormat('{b}', 'Month'),
                                              DimensionFieldFormat('{Y:-9}-{Y:+10}', None)])}
        TestDimensionFormat.checkString(s, r)

    @staticmethod
    def checkString(s, r):
        m = dimension_format.parse_dimension_format_string(s)

        for k in r.iterkeys():
            sDf = m[k]
            rDf = r[k]
            print("Comparing '%s' with '%s'" % (sDf.label, rDf.label))
            assert (sDf.label is None and rDf.label is None) or (sDf.label == rDf.label)

            assert len(sDf.dimensionFieldFormats) == len(rDf.dimensionFieldFormats)
            for i in xrange(len(rDf.dimensionFieldFormats)):
                sDff = sDf.dimensionFieldFormats[i]
                rDff = rDf.dimensionFieldFormats[i]
                print("Comparing '%s' with '%s'" % (sDff.label, rDff.label))
                assert (sDff.label is None and rDff.label is None) or (sDff.label == rDff.label)
                print("Comparing '%s' with '%s'" % (sDff.formatString, rDff.formatString))
                assert (sDff.formatString is None and rDff.formatString is None) or (sDff.formatString == rDff.formatString)

def suite():
    suite = unittest.TestSuite()

    # Use all methods that start with 'test' to make the suite.
    suite.addTest(unittest.makeSuite(TestDimensionFormat))
    return suite
    
if __name__ == '__main__':
    import logging
    from ecomaps.tests import TEST_LOG_FORMAT_STRING
    logging.basicConfig(level=logging.DEBUG, format=TEST_LOG_FORMAT_STRING)

    s = suite()
    unittest.TextTestRunner(verbosity=1).run(s)
