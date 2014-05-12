"""
Date/time utilities
"""
import re
import string

def iso2comptime(time, yearOverride=None):
    """Converts an ISO 8601 date/time string to a time component object. The only format accepted is:
    YYYY-MM-DDThh:mm:ss[Z] where the 'Z' UTC indicator is optional.
    """
    mo = re.match(r'(\d+)-(\d+)-(\d+)T(\d+):(\d+):([0-9.]+)Z?', time)
    if not mo:
        raise ValueError, 'Time %s not recognised' % time
    (year, month, day, hour, minute, second) = mo.groups()
    if yearOverride is not None:
        year = yearOverride
    return comptime(year, month, day, hour, minute, second)

class comptime:
    """Date/time component object
    @param year: an integer
    @param month: an integer in the range 1 .. 12
    @param day: an integer in the range 1 .. 31
    @param hour: an integer in the range 0 .. 59
    @param minute: an integer in the range 0 .. 59
    @param second: a floating point number in the range 0.0 ,, 60.0
    """
    MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    MONTH_SHORT_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self, year, month, day, hour, minute, second):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour = int(hour)
        self.minute = int(minute)
        self.second = float(second)

    def __format__(self, format_spec):
        """
        Returns a string value of a date/time component formatted according to the format
        specification. It is compatible with the standard library string.Formatter class.
        The specification is in the format:
        <component specifier>[:<offset>]
        where <component specifier> is one of
        b      Abbreviated month name.
        B      Full month name.
        d      Day of the month as a decimal number [01,31]
        H      Hour (24-hour clock) as a decimal number [00,23]
        I      Hour (12-hour clock) as a decimal number [01,12]
        m      Month as a decimal number [01,12]
        M      Minute as a decimal number [00,59]
        p      AM or PM
        S      Second as a decimal number [00,61]
        y      Year without century as a decimal number [00,99]
        Y      Year with century as a decimal number
        <offset> is a number which is added to the relevant component before formatting.
        Examples are:
        b
        Y:+10
        @param format_spec: format specifier
        """
        (field, sep, modifier) = format_spec.partition(':')
        value = {
                'b': self.month,
                'B': self.month,
                'd': self.day,
                'H': self.hour,
                'I': self.hour,
                'm': self.month,
                'M': self.minute,
                'p': self.hour,
                'S': self.second,
                'y': self.year,
                'Y': self.year
                }.get(field, 0)
        if modifier:
            cls = type(value)
            value += float(modifier)
            if cls is int:
                value = int(value)
        return {
                'b': lambda x : self.MONTH_SHORT_NAMES[x - 1] if x >= 1 and x <= 12 else x.__str__(),
                'B': lambda x : self.MONTH_NAMES[x - 1] if x >= 1 and x <= 12 else x.__str__(),
                'd': lambda x : '{0:02d}'.format(x),
                'H': lambda x : '{0:02d}'.format(x),
                'I': lambda x : '{0:02d}'.format((x - 1) % 12 + 1),
                'm': lambda x : '{0:02d}'.format(x),
                'M': lambda x : '{0:02d}'.format(x),
                'p': lambda x : 'PM' if x >= 12 and x < 24 else 'AM',
                'S': lambda x : '{0:02d}'.format(int(x)),
                'y': lambda x : '{0:02d}'.format(x % 100),
                'Y': lambda x : x.__str__()
            }.get(field, lambda x : '')(value)

    def compare(self, time):
        """Compares the date/time with another date/time.
        @param time: date/time to compare with
        @return a positive integer if this date/time has a later value than the one being compared
            with, a negative integer if the other date/time is later and zero if they are the same.
        """
        componentsSelf = [self.year, self.month, self.day, self.hour, self.minute, self.second]
        componentsTime = [time.year, time.month, time.day, time.hour, time.minute, time.second]
        for i in xrange(len(componentsSelf)):
            diff = cmp(componentsSelf[i], componentsTime[i])
            if diff != 0:
                break
        return diff

    def format(self, format_spec):
        """Returns a string value of the date/time formatted according to the format specification.
        It is used to format one or fields from a single comptime instance into one string. The
        specification is in the format of text containing occurrences of:
        {<component specifier>[:<offset>]}
        Each of these is replaced by a string value of a date/time component formatted according to
        the component specifier and offset. <component specifier> is one of:
        b      Abbreviated month name.
        B      Full month name.
        d      Day of the month as a decimal number [01,31]
        H      Hour (24-hour clock) as a decimal number [00,23]
        I      Hour (12-hour clock) as a decimal number [01,12]
        m      Month as a decimal number [01,12]
        M      Minute as a decimal number [00,59]
        p      AM or PM
        S      Second as a decimal number [00,61]
        y      Year without century as a decimal number [00,99]
        Y      Year with century as a decimal number
        <offset> is a number which is added to the relevant component before formatting.
        Examples are:
        {b}, {Y}
        {Y:-10}-{Y:+10}
        @param format_spec: format specifier
        """
        fmt = string.Formatter()
        segments = []
        for (literal_text, field_name, segment_format_spec, conversion) in fmt.parse(format_spec):
            if literal_text:
                segments.append(literal_text)
            if segment_format_spec:
                fmt = '%s:%s' % (field_name, segment_format_spec)
                segments.append(self.__format__(fmt))
            else:
                fmt = '%s' % field_name
                segments.append(self.__format__(fmt))
        return ''.join(segments)

    @staticmethod
    def startValue(format_spec):
        """Returns the expected starting value for a field with a simple specification.
        @return starting value or None if no appropriate value
        """
        return {
            '{b}': 'Jan',
            '{B}': 'January',
            '{d}': '01',
            '{H}': '00',
            '{I}': '01',
            '{m}': '01',
            '{M}': '00',
            '{p}': 'AM',
            '{S}': '00',
            '{y}': '00',
            '{Y}': None
            }.get(format_spec, None)

if __name__ == '__main__':
    t = comptime(2011, 6, 17, 13, 14, 15)
    print '{0:Y:-10}-{0:Y:+10}'.format(t)
    print '{0:Y} {0:y} {0:m} {0:b} {0:B} {0:d}   {0:H} {0:h} {0:M} {0:S} {0:p}'.format(t)
    print '{ct:Y:-10}-{ct:Y:+10}'.format(ct=t)

    comptime(2011, 6, 17, 13, 14, 15).format('{Y:-10}-{Y:+10}')
    fmt = '{Y} {y} {m} {b} {B} {d}   {H} {I} {M} {S} {p}'
    print comptime(2011, 6, 17, 12, 0, 0).format(fmt)
    print comptime(2011, 6, 17, 11, 59, 59.99).format(fmt)
    print comptime(2011, 6, 17, 23, 59, 59.99).format(fmt)
    print comptime(2011, 6, 17, 24, 0, 0).format(fmt)
    print comptime(21111, 6, 17, 13, 14, 15).format(fmt)
    print comptime(1, 6, 17, 13, 14, 15).format(fmt)
    print comptime(-1000, 6, 17, 13, 14, 15).format(fmt)
    print comptime(2011, 6, 17, 12, 0, 0).format('{b}, {Y:-9}-{Y:+10}')
