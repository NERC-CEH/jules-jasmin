"""
# header
"""
import logging
from lxml import html, etree
import re
from joj.model import NamelistFile, Namelist, Parameter

log = logging.getLogger(__name__)


class JulesParameterParser(object):
    """
    Parser for the Jules documentation
    Parses the html namelist parameters into the database objects
    """

    # regular expression for integers
    _RE_INTEGER = "([+\-]?\d+)"

    # list of namelist files
    _NAMELIST_FILES = [
        'logging.nml.html',
        'switches.nml.html',
        'model_levels.nml.html',
        'timesteps.nml.html',
        'model_grid.nml.html',
        'ancillaries.nml.html',
        'pft_params.nml.html',
        'nveg_params.nml.html',
        'triffid_params.nml.html',
        'snow_params.nml.html',
        'misc_params.nml.html',
        'urban.nml.html',
        'imogen.nml.html',
        'drive.nml.html',
        'prescribed_data.nml.html',
        'initial_conditions.nml.html',
        'output.nml.html']

    _EXTRA_PARAMETERS = \
        {
            'JULES_PFTPARM': [Parameter(name="dust_veg_scj_io", type="real(npft)")]
        }

    def _get_parameter_limits(self, parameter, value):
        """
        decode the limits on a parameter and set them on the parameter
        :param parameter: the parameter
        :param value: the limits
        :return: nothing
        """
        range_match = re.search("{int}-{int}".format(int=self._RE_INTEGER), value)
        if range_match:
            parameter.min = range_match.group(1)
            parameter.min_inclusive = True
            parameter.max = range_match.group(2)
            parameter.max_inclusive = True
            return

        range_match = re.search("> {int}".format(int=self._RE_INTEGER), value)
        if range_match:
            parameter.min = range_match.group(1)
            parameter.min_inclusive = False
            return

        range_match = re.search(">= {int}".format(int=self._RE_INTEGER), value)
        if range_match:
            parameter.min = range_match.group(1)
            parameter.min_inclusive = True
            return

        range_match = re.search("{int} or {int}".format(int=self._RE_INTEGER), value)
        if range_match:
            if int(range_match.group(1)) + 1 == int(range_match.group(2)):
                parameter.min = range_match.group(1)
                parameter.min_inclusive = True
                parameter.max = range_match.group(2)
                parameter.max_inclusive = True
                return

        range_match = re.search("{int}, {int} or {int}".format(int=self._RE_INTEGER), value)
        if range_match:
            if int(range_match.group(1)) + 1 == int(range_match.group(2)) and \
               int(range_match.group(2)) + 1 == int(range_match.group(3)):
                parameter.min = range_match.group(1)
                parameter.min_inclusive = True
                parameter.max = range_match.group(3)
                parameter.max_inclusive = True
                return

        range_match = re.search("{int} <= {name} <= {int}".format(name=parameter.name, int=self._RE_INTEGER), value)
        if range_match:
            if int(range_match.group(1)) + 1 == int(range_match.group(2)):
                parameter.min = range_match.group(1)
                parameter.min_inclusive = True
                parameter.max = range_match.group(2)
                parameter.max_inclusive = True
                return

        log.fatal("Unknown parameter limit '%s'" % value)
        exit()

    def _set_parameter_default(self, parameter, value):
        """
        Set the default value of a parameter
        :param parameter: the parameter
        :param value: the value for the default
        :return: nothing
        """

        if value == u"\u2018\u2019 (empty string)":
            parameter.default_value = ''
            return

        #remove smart quotes
        parameter.default_value = \
            value.replace(u"\u201C", '').replace(u"\u201D", '').replace(u"\u2018", '').replace(u"\u2019", '')

    def run(self, namelist_documentation_file, page_url, code_version):
        """
        Run the parser on the file and return the name list file object
        :param namelist_documentation_file: filename for the name list file documentation
        :param page_url: page url
        :param code_version: the CodeVersion to use for the code version
        :return: the NamelistFile object
        """
        log.info("Parsing %s" % namelist_documentation_file)

        tree = html.parse(namelist_documentation_file)

        namelist_file = NamelistFile()
        namelist_file.filename = str(tree.xpath('//h1/tt/span/text()')[0])

        log.info("Filename: %s" % namelist_file.filename)

        namelist_file.namelists = []

        for namelist_name in tree.xpath('//h2/tt/span/text()'):
            namelist = Namelist()
            namelist.name = str(namelist_name)
            log.info("    Namelist: %s" % namelist.name)
            namelist_file.namelists.append(namelist)

            if namelist.name.upper() in self._EXTRA_PARAMETERS:
                namelist.parameters.extend(self._EXTRA_PARAMETERS[namelist.name])

            #parameters at the bottom level
            parameters = tree.xpath('//div[@id="namelist-{namelist_name}"]/dl'.format(namelist_name=namelist_name))

            #parameters in optional sections
            parameters.extend(
                tree.xpath('//div[@id="namelist-{namelist_name}"]/div/dl'.format(namelist_name=namelist_name)))
            parameters.extend(
                tree.xpath('//div[@id="namelist-{namelist_name}"]/div/div/dl[@class="member"]'
                           .format(namelist_name=namelist_name)))
            parameters.extend(
                tree.xpath('//div[@id="namelist-{namelist_name}"]/div/div/dl[@class="last member"]'
                           .format(namelist_name=namelist_name)))
            for parameter_elements in parameters:

                parameter_name = str(parameter_elements.xpath("dt")[0].attrib["id"].replace(namelist_name + '::', ''))
                log.info("      Parameter: %s" % parameter_name)
                parameter = Parameter()
                parameter.name = parameter_name
                parameter.default_value = None
                parameter.code_versions = [code_version]
                parameter.url_suffix = page_url + parameter_elements.xpath("dt/a")[0].attrib["href"]
                log.info("          Web page suffix: %s" % parameter.url_suffix)

                possible_description = parameter_elements.xpath("dd/p")
                parameter.description = etree.tostring(possible_description[0]) if len(possible_description) > 0 else ""
                log.info("          Description: %s" % parameter.description.strip())

                for parameter_property in parameter_elements.xpath("dd/table/tbody/tr"):
                    names = parameter_property.xpath("th/text()")
                    if len(names) == 1:
                        td = parameter_property.xpath("td")[0]
                        value = "".join([x for x in td.itertext()])
                        if names[0] == 'Type :':
                            parameter.type = value
                            log.info("          Type: %s" % parameter.type)
                        elif names[0] == 'Default :':
                            self._set_parameter_default(parameter, value)
                            log.info("          Default: %s" % parameter.default_value)
                        elif names[0] == 'Permitted :':
                            self._get_parameter_limits(parameter, value)
                            log.info("          min: %s" % parameter.min)
                            log.info("          max: %s" % parameter.max)

                parameter.required = (parameter.default_value is None)

                namelist.parameters.append(parameter)
        return namelist_file

    def parse_all(self, root_path, code_version):
        """
        Parse all know name list files and return the namelist file objects
        :param root_path: the root path for the namelist files
        :param code_version: the code version object
        :return: namelist file objects
        """
        namelist_files = []
        namelist_file = ""
        try:
            for namelist_file in self._NAMELIST_FILES:
                namelist_files.append(self.run(root_path + namelist_file, namelist_file, code_version))
            return namelist_files
        except IOError, ex:
            log.critical("Can not read namelist file %s " % namelist_file)
            log.critical(ex)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = JulesParameterParser()
    base = '../docs/Jules/user_guide/html/namelists/'
    parser.parse_all(base, None)
