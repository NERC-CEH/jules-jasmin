"""
# header
"""
import logging
from lxml import html
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

    #variable which should appear in the output list (must be lower case)
    _VARIABLES_THAT_SHOULD_BE_USED = \
        ['fqw_gb',
         'ecan_gb',
         'esoil_gb',
         'ei_gb',
         'ftl_gb',
         'cs_gb',
         'cv',
         'gpp_gb',
         'lit_c_mean',
         'npp_gb',
         'resp_p_gb',
         'resp_s_gb',
         'runoff',
         'surf_roff',
         'sub_surf_roff',
         'swet_tot',
         'swet_liq_tot',
         'snow_depth_gb',
         'snow_frac',
         'snow_mass_gb',
         'tstar_gb',
         'smc_tot',
         'rad_net',
         'lw_down',
         'sw_down',
         'wind',
         'tl1',
         'qw1',
         'pstar',
         'precip']

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
            '| //div[@id="variables-that-have-a-single-value-at-each-land-gridpoint"]/table/tbody/tr[@class="row-odd"]'
            '| //div[@id="variables-that-have-a-single-value-at-each-gridpoint-land-and-sea"]/table/tbody/tr[@class="row-even"] '
            '| //div[@id="variables-that-have-a-single-value-at-each-gridpoint-land-and-sea"]/table/tbody/tr[@class="row-odd"]')

        for output_row in output_table_rows:
            output_variable = OutputVariable()
            name = str(output_row.xpath('td/tt/span[@class="pre"]/text()')[0])
            if name.lower() in self._VARIABLES_THAT_SHOULD_BE_USED:
                output_variable.name = name
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

        if (len(output_variables) != len(self._VARIABLES_THAT_SHOULD_BE_USED)):
            log.error("'Output variables' length, %s, if different to 'variables to use' length, %s "
                      % (len(output_variables), len(self._VARIABLES_THAT_SHOULD_BE_USED)))
            exit(-1)
        return output_variables

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = JulesOutputVariableParser()
    file_path = '../docs/Jules/user_guide/html/output-variables.html'
    parser.parse(file_path)
