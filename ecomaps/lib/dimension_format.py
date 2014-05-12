import logging
import shlex

import ecomaps.lib.date_util as date_util

log = logging.getLogger(__name__)

class DimensionFormat:
    """Dimension format information: holds display label and format.
    @param label: field format display label
    @param dimensionFieldFormats: list of DimensionFieldFormat
    """
    def __init__(self, label, dimensionFieldFormats):
        self.label = label
        self.dimensionFieldFormats = dimensionFieldFormats

class DimensionFieldFormat:
    """Dimension field format information: holds display label and format for one field in a
    dimension format.
    @param label: dimension display label
    @param format: dimension value display format
    """
    def __init__(self, formatString, label):
        self.formatString = formatString
        self.label = label

    def applyFormat(self, name, dimensionValues):
        """Applies a dimension format to a list of values, returning the list formatted values or
        None if no formatting is possible.
        @param name: name of dimension
        @param dimensionValues: list of dimension values
        @return list of formatted values or None if there is no applicable format
        """
        log.debug('Formatting %s in format "%s"' % (name, self.formatString))
        if (name == 'time') and (self.formatString):
            displayValues = []
            for val in dimensionValues:
                comptime = date_util.iso2comptime(val)
                displayValues.append(comptime.format(self.formatString))
        else:
            displayValues = None
        return displayValues

    def getStartValue(self, name, reverse):
        if (name == 'time') and (self.formatString):
            startValue = date_util.comptime.startValue(self.formatString)
            return("%s%s" % (("-" if reverse else "+"), startValue))

def parse_dimension_format_string(fmt):
    """
    Parses a dimension format specification string. The expected format is
    <dimension name>:[<dimension label>][:<format string>[:<format label>]][;<format string>[:<format label>]][;...]
    More than one dimension format specification of the above form may be present, each separated by
    a comma. Examples are:
    time:Date
    time:Date:'{Y} {b} {d}',depth:Depth
    time:'Date':'{Y}':'Year';'{b}':'Month'
    If the more than one format string is present for a dimension, all format strings must be
    non-empty.
    @param specification string
    @return map of name to array of DimensionFormat object
    """
    formatMap = {}

    dimension = None
    label = None
    field = 0
    formats = []
    entry = [None, None]

    sl = shlex.shlex(fmt)
    tok = sl.get_token()
    while tok:
        if _isFieldSeparator(tok):
            field += 1
        elif _isFormatSeparator(tok):
            formats.append(DimensionFieldFormat(entry[0], entry[1]))
            field = 2
            entry = [None, None]
        elif _isDimensionSeparator(tok):
            if dimension:
                formats.append(DimensionFieldFormat(entry[0], entry[1]))
                formatMap[dimension] = DimensionFormat(label, formats)
            dimension = None
            label = None
            field = 0
            formats = []
            entry = [None, None]
        else:
            if field == 0:
                dimension = _stripQuotes(tok)
            elif field == 1:
                label = _stripQuotes(tok)
            else:
                entry[field - 2] = _stripQuotes(tok)
        # Get next token.
        tok = sl.get_token()
    if dimension:
        formats.append(DimensionFieldFormat(entry[0], entry[1]))
        formatMap[dimension] = DimensionFormat(label, formats)

    return formatMap

def _isFieldSeparator(tok):
    """
    @param tok: token from parsing
    @return True if token is the separator that separates fields for the
            specification for one dimension
    """
    return tok.strip() == ':'

def _isFormatSeparator(tok):
    """
    @param tok: token from parsing
    @return True if token is the separator that separates the specification for different parts of
            format for a dimension.
    """
    return tok.strip() == ';'

def _isDimensionSeparator(tok):
    """
    @param tok: token from parsing
    @return True if token is the separator that separates specifications for different dimensions
    """
    return tok.strip() == ','

def _stripQuotes(tok):
    """
    @param tok: token from parsing
    @return token with any matching quote characters in the first and last positions removed
    """
    if (tok[:1] == "'" and tok[-1:] == "'") or (tok[:1] == '"' and tok[-1:] == '"'):
        return tok[1:-1]
    return tok

def testString(s):
    print s
    m = parse_dimension_format_string(s)
    for k, v in m.iteritems():
        print k, v.label
        for n in v.dimensionFieldFormats:
            print("    '%s' '%s'" % (n.label, n.formatString))
    print ""

if __name__ == '__main__':
    testString("time:'time':'{b} {Y:-9}-{Y:+10}'")
    testString("time:'Time':'{b} {Y:-9}-{Y:+10}':'Month/year period'")
    testString("time:'time'")
    testString("time::'{b} {Y:-9}-{Y:+10}'")
    testString("time::'{b} {Y:-9}-{Y:+10}':'Month/year period'")
    testString("time:")
    testString("time:'time':'{b} {Y:-9}-{Y:+10}', depth:'depth below sea level'")
    testString("time:'Date':'{b}':'month';'{Y:-9}-{Y:+10}':'year range'")
    testString("time:'Date':'{b}':'month';'{Y:-9}-{Y:+10}':'year range', depth:'depth below sea level'")
    testString("depth:'depth below sea level', time:'Date':'{b}':'month';'{Y:-9}-{Y:+10}':'year range'")
