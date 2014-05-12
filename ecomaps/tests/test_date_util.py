import unittest

from ecomaps.lib.date_util import comptime

class TestDateUtil(unittest.TestCase):
    """
    Tests for the comptime formatting methods
    """
    # Tests for comptime.__format__
    def test_001_comptime___format___year_range(self):
        t = comptime(2011, 6, 17, 13, 14, 15)
        f = '{0:Y:-10}-{0:Y:+10}'.format(t)
        assert f == '2001-2021'

    def test_002_comptime___format___all_fields(self):
        t = comptime(2011, 6, 17, 13, 14, 15)
        f = '{0:Y} {0:y} {0:m} {0:b} {0:B} {0:d}   {0:H} {0:I} {0:M} {0:S} {0:p}'.format(t)
        assert f == '2011 11 06 Jun June 17   13 01 14 15 PM'

    def test_003_comptime___format___all_fields_keyword(self):
        t = comptime(2011, 6, 17, 13, 14, 15)
        f = '{ct:Y} {ct:y} {ct:m} {ct:b} {ct:B} {ct:d}   {ct:H} {ct:I} {ct:M} {ct:S} {ct:p}'.format(ct=t)
        assert f == '2011 11 06 Jun June 17   13 01 14 15 PM'

    # Tests for comptime.format
    def test_004_comptime_format_all_fields(self):
        ct = comptime(2011, 6, 17, 13, 14, 15)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '2011 11 06 Jun June 17   13 01 14 15 PM'

    def test_005_comptime_format_midday(self):
        ct = comptime(2011, 6, 17, 12, 0, 0)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '2011 11 06 Jun June 17   12 12 00 00 PM'

    def test_006_comptime_format_hundredth_sec_to_midday(self):
        ct = comptime(2011, 6, 17, 11, 59, 59.99)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '2011 11 06 Jun June 17   11 11 59 59 AM'

    def test_007_comptime_format_hundredth_sec_to_midnight(self):
        ct = comptime(2011, 6, 17, 23, 59, 59.99)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '2011 11 06 Jun June 17   23 11 59 59 PM'

    def test_008_comptime_format_midnight(self):
        ct = comptime(2011, 6, 17, 24, 0, 0)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '2011 11 06 Jun June 17   24 12 00 00 AM'

    def test_009_comptime_format_large_year(self):
        ct = comptime(12345, 6, 17, 13, 14, 15)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '12345 45 06 Jun June 17   13 01 14 15 PM'

    def test_010_comptime_format_small_year(self):
        ct = comptime(1, 6, 17, 13, 14, 15)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '1 01 06 Jun June 17   13 01 14 15 PM'

    def test_011_comptime_format_negative_year(self):
        ct = comptime(-1234, 6, 17, 13, 14, 15)
        fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
        f = ct.format(fmt)
        assert f == '-1234 66 06 Jun June 17   13 01 14 15 PM'

    def test_012_comptime_format_year_range(self):
        ct = comptime(2011, 6, 17, 13, 14, 15)
        fmt = '{Y:-10}-{Y:+10}'
        f = ct.format(fmt)
        assert f == '2001-2021'

    def test_013_comptime_format_month_year_range(self):
        ct = comptime(2010, 6, 17, 12, 0, 0)
        fmt = '{b}, {Y:-9}-{Y:+10}'
        f = ct.format(fmt)
        assert f == 'Jun, 2001-2020'


    # Tests for comptime.compare
    def test_014_comptime_compare_equal(self):
        ct1 = comptime(2010, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2010, 6, 17, 12, 13, 14.15)
        assert ct1.compare(ct2) == 0

    def test_015_comptime_compare_different_year(self):
        ct1 = comptime(2010, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2011, 6, 17, 12, 13, 14.15)
        assert ct1.compare(ct2) < 0
        assert ct2.compare(ct1) > 0

    def test_016_comptime_compare_different_month(self):
        ct1 = comptime(2011, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2011, 7, 17, 12, 13, 14.15)
        assert ct1.compare(ct2) < 0
        assert ct2.compare(ct1) > 0

    def test_017_comptime_compare_different_day(self):
        ct1 = comptime(2011, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2011, 6, 18, 12, 13, 14.15)
        assert ct1.compare(ct2) < 0
        assert ct2.compare(ct1) > 0

    def test_018_comptime_compare_different_hour(self):
        ct1 = comptime(2011, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2011, 6, 17, 13, 13, 14.15)
        assert ct1.compare(ct2) < 0
        assert ct2.compare(ct1) > 0

    def test_019_comptime_compare_different_minute(self):
        ct1 = comptime(2011, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2011, 6, 17, 12, 14, 14.15)
        assert ct1.compare(ct2) < 0
        assert ct2.compare(ct1) > 0

    def test_020_comptime_compare_different_second(self):
        ct1 = comptime(2011, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2011, 6, 17, 12, 13, 15.15)
        assert ct1.compare(ct2) < 0
        assert ct2.compare(ct1) > 0

    def test_021_comptime_compare_different_second_fraction(self):
        ct1 = comptime(2011, 6, 17, 12, 13, 14.15)
        ct2 = comptime(2011, 6, 17, 12, 13, 14.16)
        assert ct1.compare(ct2) < 0
        assert ct2.compare(ct1) > 0

def suite():
    suite = unittest.TestSuite()

    # Use all methods that start with 'test' to make the suite.
    suite.addTest(unittest.makeSuite(TestDateUtil))
    return suite
    
if __name__ == '__main__':
    import logging
    from ecomaps.tests import TEST_LOG_FORMAT_STRING
    logging.basicConfig(level=logging.DEBUG, format=TEST_LOG_FORMAT_STRING)

    s = suite()
    unittest.TextTestRunner(verbosity=1).run(s)
