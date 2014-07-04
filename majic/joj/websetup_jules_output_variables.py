"""
# header
"""
import logging
from lxml import html, etree
import re
from joj.model import NamelistFile, Namelist, Parameter
from joj.model.output_variable import OutputVariable
from joj.utils import constants

log = logging.getLogger(__name__)


class JulesOutputVariableParser(object):
    """
    Parser for the Jules documentation
    Parses the html output variables into the database objects
    """

    # Some variables depend on the value of nsmax - keep a record of those names here:
    _DEPENDS_ON_NSMAX = ['snow_ice_gb', 'snow_liq_gb', 'snow_ice_tile', 'snow_liq_tile',
                         'rgrainl', 'snow_ds', 'snow_ice', 'snow_liq', 'tsnow']

    def parse(self, file_path):
        """
        Run the parser on the output variables file and return a list of OutputVariables
        :param file_path: path of output-variables.html
        :return: list of OutputVariables
        """
        log.info("Parsing %s" % file_path)
        tree = html.parse(file_path)
        output_variables = []
        output_table_rows = tree.xpath(
            '//div[@id="variables-that-have-a-single-value-at-each-land-gridpoint"]/table/tbody/tr[@class="row-even"] '
            '| //div[@id="variables-that-have-a-single-value-at-each-land-gridpoint"]/table/tbody/tr[@class="row-odd"]')
        for output_row in output_table_rows:
            output_variable = OutputVariable()
            output_variable.name = str(output_row.xpath('td/tt/span[@class="pre"]/text()')[0])
            # Need to reconstruct the description because of <sup> tags
            desc_texts = output_row.xpath('td[2]/text() | td[2]/p[1]/text()')
            desc_tags = output_row.xpath('td[2]/sup/text() | td[2]/p[1]/sup/text() | td[2]/tt/span/text() '
                                         '| td[2]/a/tt/span/text()')
            output_variable.description = unicode(desc_texts[0])
            for i in range(len(desc_tags)):
                output_variable.description += desc_tags[i]
                output_variable.description += desc_texts[i+1]
            output_variable.depends_on_nsmax = output_variable.name in constants.DEPENDS_ON_NSMAX
            output_variables.append(output_variable)

        return output_variables

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = JulesOutputVariableParser()
    file_path = '../docs/Jules/user_guide/html/output-variables.html'
    parser.parse(file_path)
