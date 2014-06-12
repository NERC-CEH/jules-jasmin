# Header
import sys
import logging
from lxml import html, etree
from joj.model import NamelistFile, Namelist, Parameter

log = logging.getLogger(__name__)


class Parser(object):
    """
    Parser for the Jules documentation
    Parses the html namelist parameters into the database objects
    """

    def run(self, namelist_documentation_file):
        """
        Run the parser on the file and return the name list file object
        :param namelist_documentation_file: filename for the name list file documentation
        :return: the NamelistFile object
        """
        log.info("Parsing %s" % namelist_documentation_file)

        tree = html.parse(namelist_documentation_file)

        namelist_file = NamelistFile()
        namelist_file.filename = tree.xpath('//h1/tt/span/text()')[0]

        log.info("Filename: %s" % namelist_file.filename)

        namelist_file.namelists = []

        for namelist_name in tree.xpath('//h2/tt/span/text()'):
            namelist = Namelist()
            namelist.name = namelist_name
            log.info("    Namelist: %s" % namelist.name)
            namelist_file.namelists.append(namelist)

            for parameter_names_elements in tree.xpath('//div[@id="namelist-{namelist_name}"]/dl'.format(namelist_name=namelist_name)):

                parameter_name = parameter_names_elements.xpath("dt")[0].attrib["id"].replace(namelist_name + '::', '')
                log.info("      Parameter: %s" % parameter_name)
                parameter = Parameter()
                parameter.name = parameter_name
                parameter.default_value = None

                parameter.description = etree.tostring(parameter_names_elements.xpath("dd/p")[0])
                log.info("          Description: %s" % parameter.description.strip())

                for paramety_property in parameter_names_elements.xpath("dd/table/tbody/tr"):
                    names = paramety_property.xpath("th/text()")
                    if len(names) == 1:
                        value = paramety_property.xpath("td/text()")[0]
                        if names[0] == 'Type :':
                            parameter.type = value
                            log.info("          Type: %s" % value)
                        elif names[0] == 'Default :':
                            if value == u'\u8220\u8221':
                                parameter.default_value = ''
                            else:
                                parameter.default_value = value
                            log.info("          Default: %s" % value)

                #parameters left to set
                # parameter.url_suffix
                # parameter.required
                # parameter.default_value
                # parameter.code_versions =
                namelist.parameters.append(parameter)




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    namelist_file = sys.argv[1]
    parser = Parser()
    parser.run(namelist_file)
