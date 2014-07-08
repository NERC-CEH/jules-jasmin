"""
# header
"""
from hamcrest import *
from joj.model import Parameter, ModelRun, CodeVersion, ParameterValue, NamelistFile, Namelist
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from tests import TestController


class TestJobRunnerClient(TestController):
    def test_GIVEN_valid_model_WHEN_convert_to_dictionary_THEN_dictionary_is_correct(self):

        job_runner_client = JobRunnerClient()

        parameter = Parameter(name='param1')
        expected_parameter_value = '12'
        expected_index = 3
        #There is only one parameter value per run:
        parameter.parameter_values = [ParameterValue(value=expected_parameter_value)]

        namelist = Namelist(name='NAME_LIST')
        namelist_file = NamelistFile(filename='filename')

        namelist.parameters = [parameter]
        namelist.namelist_file = namelist_file
        namelist.index_in_file = expected_index

        model_run = ModelRun()
        model_run.id = 101
        code_version = CodeVersion(name='Jules v3.4.1')

        model_run.code_version = code_version
        code_version.parameters = [parameter]

        result = job_runner_client.convert_model_to_dictionary(model_run)

        assert_that(result[constants.JSON_MODEL_RUN_ID], is_(model_run.id), "value is correct")
        assert_that(result[constants.JSON_MODEL_CODE_VERSION], is_(model_run.code_version.name), "value is correct")
        namelist_file_result = result[constants.JSON_MODEL_NAMELIST_FILES][0]
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELIST_FILE_FILENAME],
                    is_(namelist_file.filename), "value is correct")
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_NAMELIST_NAME],
                    is_(namelist.name), "namelist name")
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_NAMELIST_INDEX],
                    is_(namelist.index_in_file), "namelist index")
        parameters_result = namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_PARAMETERS]
        assert_that(parameters_result, is_({parameter.name: expected_parameter_value}), "value is correct")

    def test_GIVEN_model_contains_repeated_namelists_WHEN_convert_to_dictionary_THEN_namelists_grouped_correctly(self):
        job_runner_client = JobRunnerClient()

        # Set the namelists here:
        nml_output = Namelist(name=constants.JULES_NML_OUTPUT)
        nml_output_profile = Namelist(name=constants.JULES_NML_OUTPUT_PROFILE)
        nml_output.namelist_file = nml_output_profile.namelist_file = NamelistFile(filename="output.nml")

        # Set the parameters here:
        param_nprofiles = Parameter(name=constants.JULES_PARAM_OUTPUT_NPROFILES[1])
        param_profile_name = Parameter(name=constants.JULES_PARAM_PROFILE_NAME[1])
        param_var = Parameter(name=constants.JULES_PARAM_OUTPUT_VAR[1])

        # Set the parameter values
        param_nprofiles.parameter_values = [ParameterValue(value=2)]
        param_profile_name.parameter_values = [ParameterValue(value="monthly", group_id=0),
                                               ParameterValue(value="yearly", group_id=1)]

        param_var.parameter_values = [ParameterValue(value='"emis_gb", "ftl_gb"', group_id=0),
                                      ParameterValue(value='"snow_mass_gb", "tstar_gb"', group_id=1)]

        # Assign the parameters to namelists
        nml_output.parameters = [param_nprofiles]
        nml_output_profile.parameters = [param_profile_name, param_var]

        model_run = ModelRun()
        model_run.id = 101
        code_version = CodeVersion(name='Jules v3.4.1')

        model_run.code_version = code_version
        code_version.parameters = [param_profile_name, param_var, param_nprofiles]

        result = job_runner_client.convert_model_to_dictionary(model_run)

        # Check the result dictionary has the correct run ID and code version
        assert_that(result[constants.JSON_MODEL_RUN_ID], is_(model_run.id), "value is correct")
        assert_that(result[constants.JSON_MODEL_CODE_VERSION], is_(model_run.code_version.name), "value is correct")

        # Check that the namelist_files has the correct namelist file
        namelist_file_result = result[constants.JSON_MODEL_NAMELIST_FILES][0]
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELIST_FILE_FILENAME],
                    is_("output.nml"), "value is correct")

        # Check that the namelist file contains the three namelists
        namelists = namelist_file_result[constants.JSON_MODEL_NAMELISTS]
        assert_that(len(namelists), is_(3))

        # Check the dictionaries are as expected
        profiles_dict1 = {constants.JSON_MODEL_NAMELIST_GROUP_ID: 0,
                          constants.JSON_MODEL_NAMELIST_INDEX: None,
                          constants.JSON_MODEL_NAMELIST_NAME: constants.JULES_NML_OUTPUT_PROFILE,
                          constants.JSON_MODEL_PARAMETERS: {
                              constants.JULES_PARAM_OUTPUT_VAR[1]: '"emis_gb", "ftl_gb"',
                              constants.JULES_PARAM_PROFILE_NAME[1]: "monthly"
                          }}
        profiles_dict2 = {constants.JSON_MODEL_NAMELIST_GROUP_ID: 1,
                          constants.JSON_MODEL_NAMELIST_INDEX: None,
                          constants.JSON_MODEL_NAMELIST_NAME: constants.JULES_NML_OUTPUT_PROFILE,
                          constants.JSON_MODEL_PARAMETERS: {
                              constants.JULES_PARAM_OUTPUT_VAR[1]: '"snow_mass_gb", "tstar_gb"',
                              constants.JULES_PARAM_PROFILE_NAME[1]: "yearly"
                          }}
        output_dict = {constants.JSON_MODEL_NAMELIST_GROUP_ID: None,
                       constants.JSON_MODEL_NAMELIST_INDEX: None,
                       constants.JSON_MODEL_NAMELIST_NAME: constants.JULES_NML_OUTPUT,
                       constants.JSON_MODEL_PARAMETERS: {
                           constants.JULES_PARAM_OUTPUT_NPROFILES[1]: 2
                       }}
        assert_that(namelists, contains_inanyorder(profiles_dict1, profiles_dict2, output_dict))

    def test_GIVEN_valid_model_WHEN_convert_to_dictionary_THEN_namelist_with_no_representation_are_present(self):

        job_runner_client = JobRunnerClient()

        parameter = Parameter(name='param1')
        expected_parameter_value = '12'
        #There is no parameter value:
        parameter.parameter_values = []

        namelist = Namelist(name='NAME_LIST')
        namelist_file = NamelistFile(filename='filename')

        namelist.parameters = [parameter]
        namelist.namelist_file = namelist_file

        model_run = ModelRun()
        model_run.id = 101
        code_version = CodeVersion(name='Jules v3.4.1')

        model_run.code_version = code_version
        code_version.parameters = [parameter]

        result = job_runner_client.convert_model_to_dictionary(model_run)

        namelist_file_result = result[constants.JSON_MODEL_NAMELIST_FILES][0]
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELIST_FILE_FILENAME],
                    is_(namelist_file.filename), "value is correct")
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_NAMELIST_NAME],
                    is_(namelist.name), "value is correct")

        parameters_result = namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_PARAMETERS]
        assert_that(parameters_result, is_({}), "there are no values")
