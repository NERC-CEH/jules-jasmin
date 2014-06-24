"""
# Header
"""
import os
import f90nml
import logging
from joj.model import ModelRun, ParameterValue
from joj.utils.f90_helper import python_to_f90_str
from websetup_jules_parameters import JulesParameterParser

log = logging.getLogger(__name__)


class JulesNamelistParser(object):
    """
    A parser to parse the Jules Name list into parameter value objects
    """

    # Scientific configurations, name, directory and descriptions
    _SCIENCE_CONFIGURATIONS = [
        ['EURO4', 'EURO4', 'This configuration replicates the science used in '
                           'the Met Office European 4km forecast model'],
        ['GL4.0', 'GL4.0', 'Global Land (GL) is a configuration of JULES that is developed over an annual release '
                           'cycle for use across weather and climate modelling timescales and systems. '
                           'Global Land is used in the Met Office Unified Model with the Global Atmosphere (GA) '
                           'configuration. More information can be found on the Met Office collaboration wikis '
                           'for GL and GA.'],
        ['UKV', 'UKV', 'This configuration replicates the science used in the '
                       'Met Office UK Variable resolution forecast model.'],
        ['Operational Forecast', 'operational_forecast', 'This configuration replicates the science used in the Met '
                                                         'Office global forecast model. It is designed to run as fast '
                                                         'as possible, and this is reflected in the selected science '
                                                         'options. This configuration uses the aggregate surface tile.']
    ]

    def parse_all(self, base_filename, namelist_files, user, code_version, status):
        """
        Parse all the know scientific configurations
        :param base_filename: the base filename where the configurations are stored
        :param namelist_files: the namelist file objects that are in the database
        :param user: the user who owns the runs
        :param code_version: the code version for these runs
        :param status: the status of the run
        :return: a list of model runs
        """

        model_runs = []

        for name, dir_name, description in self._SCIENCE_CONFIGURATIONS:
            config_dir = os.path.join(base_filename, dir_name)

            model_run = self.parse_namelist_files_to_create_a_model_run(
                code_version,
                description,
                config_dir,
                name,
                namelist_files,
                status,
                user)
            model_runs.append(model_run)

        return model_runs

    def parse_namelist_files_to_create_a_model_run(self, code_version, description, config_dir,
                                                   name, namelist_files, status, user):
        """
        Ceate a model run
        :param code_version: the code version object
        :param description: the description fo the model run
        :param config_dir: the configuration directory
        :param name: name of the model run
        :param namelist_files: namelist_files object
        :param status: status the model is to have
        :param user: the user creating the model run
        :return: a model run
        """
        model_run = ModelRun()
        model_run.name = name
        model_run.user = user
        model_run.code_version = code_version
        model_run.description = description
        model_run.status = status

        model_run.parameter_values = []
        log.info("Creating Model Run For: {0} ({1})".format(model_run.name, config_dir))
        for namelist_file in namelist_files:
            filename = os.path.join(config_dir, namelist_file.filename)
            if os.path.exists(filename):
                log.info("Parsing: %s" % filename)
                nml_dict = f90nml.read(filename)
                model_run.parameter_values.extend(self._create_parameter_values(namelist_file, nml_dict))
        return model_run

    def _create_parameter_values(self, namelist_file, nml_dict):
        """
        Create some parameter values for all he namelist files
        :param namelist_file: the namelist file
        :param nml_dict: the namelist dictionary
        :return: parameter values
        """
        parameter_values = []
        for namelist_dict_name, namelist_dict in nml_dict.iteritems():
            pvs = self._create_parameter_values_for_namelist_file(
                namelist_dict,
                namelist_dict_name,
                namelist_file.namelists)
            parameter_values.extend(pvs)
        return parameter_values

    def _create_parameter_values_for_namelist_file(self, namelist_dict, namelist_dict_name, namelists):
        """
        create parameter values for a namelist file
        :param namelist_dict: the namelist to set from
        :param namelist_dict_name: the name of the namelist
        :param namelists: the list of namelists
        :return: parameter values
        """
        for namelist in namelists:
            if namelist.name.lower() == namelist_dict_name.lower():
                return self._create_parameter_values_for_namelist(namelist, namelist_dict)

        log.critical("Can not find matching name list for %s" % namelist_dict_name)
        exit()

    def _create_parameter_values_for_namelist(self, namelist, namelist_dict):
        """
        Create parameter values for a namelist
        :param namelist: the name list
        :param namelist_dict: the namelist from the file
        :return: parameter values
        """
        log.info("    Namelist: %s" % namelist.name)
        parameter_values = []
        for parameter_dict_name, parameter_dict_value in namelist_dict.iteritems():
            pv = self._create_parameter_value_for_parameter(
                namelist.parameters,
                parameter_dict_name,
                python_to_f90_str(parameter_dict_value))
            parameter_values.append(pv)
            log.info("      {}: {}".format(pv.parameter.name, pv.value))
        return parameter_values

    def _create_parameter_value_for_parameter(self, parameters, parameter_dict_name, parameter_dict_value):
        """
        Create parameter value for a parameter
        :param parameters: the parameters list
        :param parameter_dict_name: the name of the parameter in the dictionary
        :param parameter_dict_value: the value in the dictionary
        :return: the parameter value
        """
        for parameter in parameters:
            if parameter_dict_name.lower() == parameter.name.lower():
                pv = ParameterValue()
                pv.parameter = parameter
                pv.value = parameter_dict_value
                return pv

        log.critical("Can not find matching parameter for %s" % parameter_dict_name)
        exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = JulesParameterParser()
    base = '../docs/Jules/user_guide/html/namelists/'
    default_namelist_files = parser.parse_all(base, None)

    jules_namelist_parser = JulesNamelistParser()
    jules_namelist_parser.parse_all('../configuration/Jules/scientific_configurations/',
                                    default_namelist_files, None, None, None)
