"""
# Header
"""
import shlex
import itertools
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

    # Scientific configurations:
    #    [name,
    #    directory
    #    descriptions]
    _SCIENCE_CONFIGURATIONS = [
        ['Energy-Water-Photosynthesis',
         'namelists_e-w-p',
         'this configuration includes the full water and energy budgets, and also includes photosynthesis. '
         'However, it uses a fixed soil and vegetation carbon pools, so the carbon budgets are not closed. '
         'It includes a five year spin up. '],

        ['Full carbon cycle',
         'namelists_full-carbon',
         'this configuration includes updated soil and vegetation carbon budgets as well as the full water and energy '
         'budgets. It includes a 100 year spin up.']
    ]

    def _read_namelist(self, nml_fname, verbose=False):
        """Parse a Fortran 90 namelist file and store the contents in a ``dict``.
           Copied from f90nml and enhanced

        >>> data_nml = f90nml.read('data.nml')
        :param nml_fname: file name
        :param verbose: whether to write out debug
        """

        nml_file = open(nml_fname, 'r')

        f90lex = shlex.shlex(nml_file)
        f90lex.commenters = '!'
        f90lex.escapedquotes = '\'"'
        f90lex.wordchars += '.-+'      # Include floating point characters
        tokens = iter(f90lex)

        # Store groups in case-insensitive dictionary
        nmls = f90nml.NmlDict()

        for t in tokens:

            # Ignore tokens outside of namelist groups
            while t != '&':
                t, prior_t = next(tokens), t

            # Current token is now '&'

            # Create the next namelist
            g_name = next(tokens)
            g_vars = f90nml.NmlDict()

            v_name = None
            v_idx = None
            v_vals = []

            # Current token is either a variable name or finalizer (/, &)

            # Populate the namelist group
            while g_name:

                if not v_name:
                    t, prior_t = next(tokens), t

                    # Skip commas separating objects
                    if t == ',':
                        t, prior_t = next(tokens), t
                    # Parse the indices of the current variable
                else:
                    if t == '(':
                        v_name, v_indices, t = f90nml.parse_f90idx(tokens, t, prior_t)

                        # TODO: Multidimensional support
                        # TODO: End index support (currently ignored)
                        i_s = 1 if not v_indices[0][0] else v_indices[0][0]
                        i_r = 1 if not v_indices[0][2] else v_indices[0][2]
                        v_idx = itertools.count(i_s, i_r)

                # Diagnostic testing
                if verbose:
                    print('  tokens: {} {}'.format(prior_t, t))

                while v_name:

                    t, prior_t = next(tokens), t

                    if verbose:
                        print('    vstate: {} {} {}'.format(v_name, v_idx, v_vals))
                        print('    tokens: {} {}'.format(prior_t, t))

                    # Parse the prior token value
                    # TODO: Add '%' to first tuple
                    if (not t in ('(', '=') or prior_t == '=') \
                            and not (prior_t, t) == (',', '/'):
                        # Parse the variable string
                        if prior_t in ('=', ','):
                            if t in (',', '/', '&'):
                                next_value = None
                            else:
                                continue
                        else:
                            next_value, t = f90nml.parse_f90val(tokens, t, prior_t)

                        if v_idx:

                            v_i = next(v_idx)

                            if v_name in g_vars:
                                v_vals = g_vars[v_name]
                                if type(v_vals) != list:
                                    v_vals = [v_vals]

                            try:
                                # Default Fortran indexing starts at 1
                                v_vals[v_i - 1] = next_value
                            except IndexError:
                                # Expand list to accomodate out-of-range indices
                                size = len(v_vals)
                                v_vals.extend(None for i in range(size, v_i))
                                v_vals[v_i - 1] = next_value
                        else:
                            v_vals.append(next_value)

                    # Save then deactivate the current variable
                    # TODO: Add '%'
                    if t in ('(', '=', '/', '&'):

                        if len(v_vals) == 0:
                            v_vals = None
                        elif len(v_vals) == 1:
                            v_vals = v_vals[0]

                        g_vars[v_name] = v_vals

                        v_name = None
                        v_vals = []

                # Set the next active variable
                # TODO: Add '%' to the list
                if t in ('=', '('):
                    v_name = prior_t
                    v_idx = None

                # Finalise namelist group
                if t in ('/', '&'):
                    # Test for classic namelist finaliser
                    if t == '&':
                        t, prior_t = next(tokens), t
                        assert t.lower() == 'end'

                    # Append the grouplist to the namelist (including empty groups)
                    if g_name.lower() not in nmls:
                        nmls[g_name] = []
                    nmls[g_name].append(g_vars)
                    g_name, g_vars = None, None

        nml_file.close()

        return nmls

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
                nml_dict = self._read_namelist(filename)
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
        for namelist_dict_name, namelist_dicts in nml_dict.iteritems():
            for namelist_dict, group_id in zip(namelist_dicts, range(len(namelist_dicts))):
                if len(namelist_dicts) == 1:
                    group_id = None
                pvs = self._create_parameter_values_for_namelist_file(
                    namelist_dict,
                    namelist_dict_name,
                    namelist_file.namelists,
                    group_id)
                parameter_values.extend(pvs)
        return parameter_values

    def _create_parameter_values_for_namelist_file(self, namelist_dict, namelist_dict_name, namelists, group_id):
        """
        create parameter values for a namelist file
        :param namelist_dict: the namelist to set from
        :param namelist_dict_name: the name of the namelist
        :param namelists: the list of namelists
        :param group_id: group id
        :return: parameter values
        """
        for namelist in namelists:
            if namelist.name.lower() == namelist_dict_name.lower():
                return self._create_parameter_values_for_namelist(namelist, namelist_dict, group_id)

        log.critical("Can not find matching name list for %s" % namelist_dict_name)
        exit()

    def _create_parameter_values_for_namelist(self, namelist, namelist_dict, group_id):
        """
        Create parameter values for a namelist
        :param namelist: the name list
        :param namelist_dict: the namelist from the file
        :param group_id: group id
        :return: parameter values
        """
        log.info("    Namelist: %s" % namelist.name)
        parameter_values = []
        for parameter_dict_name, parameter_dict_value in namelist_dict.iteritems():
            pv = self._create_parameter_value_for_parameter(
                namelist.parameters,
                parameter_dict_name,
                python_to_f90_str(parameter_dict_value),
                group_id)
            parameter_values.append(pv)
            log.info("      {}: {} ({})".format(pv.parameter.name, pv.value, pv.group_id))
        return parameter_values

    def _create_parameter_value_for_parameter(self, parameters, parameter_dict_name, parameter_dict_value, group_id):
        """
        Create parameter value for a parameter
        :param parameters: the parameters list
        :param parameter_dict_name: the name of the parameter in the dictionary
        :param parameter_dict_value: the value in the dictionary
        :param group_id: group id
        :return: the parameter value
        """
        for parameter in parameters:
            if parameter_dict_name.lower() == parameter.name.lower():
                pv = ParameterValue()
                pv.parameter = parameter
                pv.group_id = group_id
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

    watch_model_run = jules_namelist_parser.parse_namelist_files_to_create_a_model_run(
        None,
        "Watch data run over the length of the data",
        "../configuration/Jules/watch",
        "Watch 100 Years Data",
        default_namelist_files,
        None,
        None)
