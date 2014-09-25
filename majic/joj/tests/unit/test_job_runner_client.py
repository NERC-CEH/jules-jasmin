"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import datetime
from hamcrest import *
from joj.model import Parameter, ModelRun, CodeVersion, ParameterValue, NamelistFile, Namelist, User, LandCoverAction, \
    LandCoverRegion
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from joj.tests import TestController
from pylons import config
from joj.utils import utils


class TestJobRunnerClient(TestController):
    def test_GIVEN_valid_model_WHEN_convert_to_dictionary_THEN_dictionary_is_correct(self):

        job_runner_client = JobRunnerClient(config)

        parameter = Parameter(name=constants.JULES_PARAM_POINTS_FILE[1])
        expected_parameter_value = '51 0.5'
        expected_index = 3
        #There is only one parameter value per run:
        parameter.parameter_values = [ParameterValue(value=expected_parameter_value)]

        namelist = Namelist(name=constants.JULES_PARAM_POINTS_FILE[0])
        namelist_file = NamelistFile(filename='filename')

        namelist.parameters = [parameter]
        namelist.namelist_file = namelist_file
        namelist.index_in_file = expected_index

        model_run = ModelRun()
        model_run.id = 101
        model_run.land_cover_frac = "1 2 3 4 5 6 7 8 9"
        code_version = CodeVersion(name='Jules v3.4.1')

        model_run.code_version = code_version
        code_version.parameters = [parameter]

        user = User()
        user.id = 1
        user.email = "email"
        user.username = "username"
        model_run.user = user

        result = job_runner_client.convert_model_to_dictionary(model_run, code_version.parameters, [])

        assert_that(result[constants.JSON_MODEL_RUN_ID], is_(model_run.id), "value is correct")
        assert_that(result[constants.JSON_MODEL_CODE_VERSION], is_(model_run.code_version.name), "value is correct")
        assert_that(result[constants.JSON_USER_ID], is_(user.id), "user id")
        assert_that(result[constants.JSON_USER_NAME], is_(user.username), "user name")
        assert_that(result[constants.JSON_USER_EMAIL], is_(user.email), "user email")
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
        job_runner_client = JobRunnerClient(config)

        # Set the namelists here:
        nml_output = Namelist(name=constants.JULES_NML_OUTPUT)
        nml_output_profile = Namelist(name=constants.JULES_NML_OUTPUT_PROFILE)
        nml_output.namelist_file = nml_output_profile.namelist_file = NamelistFile(filename="output.nml")

        nml_model_grid = Namelist(name=constants.JULES_PARAM_LATLON_REGION[0])
        nml_model_grid.namelist_file = NamelistFile(filename="model_grid.nml")

        # Set the parameters here:
        param_nprofiles = Parameter(name=constants.JULES_PARAM_OUTPUT_NPROFILES[1])
        param_profile_name = Parameter(name=constants.JULES_PARAM_OUTPUT_PROFILE_NAME[1])
        param_var = Parameter(name=constants.JULES_PARAM_OUTPUT_VAR[1])
        param_latlon_region = Parameter(name=constants.JULES_PARAM_LATLON_REGION[1])

        # Set the parameter values
        param_nprofiles.parameter_values = [ParameterValue(value=2)]
        param_profile_name.parameter_values = [ParameterValue(value="monthly", group_id=0),
                                               ParameterValue(value="yearly", group_id=1)]

        param_var.parameter_values = [ParameterValue(value='"emis_gb", "ftl_gb"', group_id=0),
                                      ParameterValue(value='"snow_mass_gb", "tstar_gb"', group_id=1)]
        param_latlon_region.parameter_values = [ParameterValue(value=".true.")]

        # Assign the parameters to namelists
        nml_output.parameters = [param_nprofiles]
        nml_output_profile.parameters = [param_profile_name, param_var]
        nml_model_grid.parameters = [param_latlon_region]

        model_run = ModelRun()
        model_run.id = 101
        code_version = CodeVersion(name='Jules v3.4.1')

        user = User()
        user.id = 1
        user.email = "email"
        user.username = "username"
        model_run.user = user

        model_run.code_version = code_version
        code_version.parameters = [param_profile_name, param_var, param_nprofiles, param_latlon_region]

        result = job_runner_client.convert_model_to_dictionary(model_run, code_version.parameters, [])

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
                              constants.JULES_PARAM_OUTPUT_PROFILE_NAME[1]: "monthly"
                          }}
        profiles_dict2 = {constants.JSON_MODEL_NAMELIST_GROUP_ID: 1,
                          constants.JSON_MODEL_NAMELIST_INDEX: None,
                          constants.JSON_MODEL_NAMELIST_NAME: constants.JULES_NML_OUTPUT_PROFILE,
                          constants.JSON_MODEL_PARAMETERS: {
                              constants.JULES_PARAM_OUTPUT_VAR[1]: '"snow_mass_gb", "tstar_gb"',
                              constants.JULES_PARAM_OUTPUT_PROFILE_NAME[1]: "yearly"
                          }}
        output_dict = {constants.JSON_MODEL_NAMELIST_GROUP_ID: None,
                       constants.JSON_MODEL_NAMELIST_INDEX: None,
                       constants.JSON_MODEL_NAMELIST_NAME: constants.JULES_NML_OUTPUT,
                       constants.JSON_MODEL_PARAMETERS: {
                           constants.JULES_PARAM_OUTPUT_NPROFILES[1]: 2
                       }}
        assert_that(namelists, contains_inanyorder(profiles_dict1, profiles_dict2, output_dict))

    def test_GIVEN_valid_model_WHEN_convert_to_dictionary_THEN_namelist_with_no_representation_are_present(self):

        job_runner_client = JobRunnerClient(config)

        parameter = Parameter(name='param1')
        expected_parameter_value = '12'
        #There is no parameter value:
        parameter.parameter_values = []

        namelist = Namelist(name='NAME_LIST')
        namelist_file = NamelistFile(filename='filename')

        # Need this to run
        parameter2 = Parameter(name=constants.JULES_PARAM_LATLON_REGION[1])
        parameter2.parameter_values = [ParameterValue(value='.true.')]
        namelist2 = Namelist(name=constants.JULES_PARAM_LATLON_REGION[0])
        namelist_file = NamelistFile(filename='filename')
        namelist2.parameters = [parameter2]
        namelist2.namelist_file = namelist_file

        namelist.parameters = [parameter]
        namelist.namelist_file = namelist_file

        model_run = ModelRun()
        model_run.id = 101
        code_version = CodeVersion(name='Jules v3.4.1')

        user = User()
        user.id = 1
        user.email = "email"
        user.username = "username"
        model_run.user = user

        model_run.code_version = code_version
        code_version.parameters = [parameter, parameter2]

        result = job_runner_client.convert_model_to_dictionary(model_run, code_version.parameters, [])

        namelist_file_result = result[constants.JSON_MODEL_NAMELIST_FILES][0]
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELIST_FILE_FILENAME],
                    is_(namelist_file.filename), "value is correct")
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_NAMELIST_NAME],
                    is_(namelist.name), "value is correct")

        parameters_result = namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_PARAMETERS]
        assert_that(parameters_result, is_({}), "there are no values")

        assert_that(len(result[constants.JSON_LAND_COVER]), is_(0))

    def test_GIVEN_model_with_land_cover_actions_WHEN_convert_to_dictionary_THEN_land_cover_actions_present(self):

        job_runner_client = JobRunnerClient(config)

        parameter = Parameter(name='file')
        expected_parameter_value = "'base_frac_file.nc'"
        parameter.parameter_values = [ParameterValue(value=expected_parameter_value)]

        parameter2 = Parameter(name='frac_name')
        expected_parameter_value2 = "'frac'"
        parameter2.parameter_values = [ParameterValue(value=expected_parameter_value2)]

        parameter3 = Parameter(name='latlon_region')
        expected_parameter_value3 = ".true."
        parameter3.parameter_values = [ParameterValue(value=expected_parameter_value3)]

        namelist = Namelist(name='JULES_FRAC')
        namelist_file = NamelistFile(filename='filename')
        expected_index = 3

        namelist.parameters = [parameter, parameter2]
        namelist.namelist_file = namelist_file
        namelist.index_in_file = expected_index

        namelist2 = Namelist(name='JULES_MODEL_GRID')
        namelist_file = NamelistFile(filename='filename')
        expected_index = 3

        namelist2.parameters = [parameter3]
        namelist2.namelist_file = namelist_file
        namelist2.index_in_file = expected_index

        model_run = ModelRun()
        model_run.id = 101
        code_version = CodeVersion(name='Jules v3.4.1')

        model_run.code_version = code_version
        code_version.parameters = [parameter, parameter2, parameter3]

        user = User()
        user.id = 1
        user.email = "email"
        user.username = "username"
        model_run.user = user

        lcr1 = LandCoverRegion()
        lcr1.mask_file = "region1.nc"
        lca1 = LandCoverAction()
        lca1.value_id = 9
        lca1.order = 1
        lca1.region = lcr1

        lcr2 = LandCoverRegion()
        lcr2.mask_file = "region2.nc"
        lca2 = LandCoverAction()
        lca2.value_id = 5
        lca2.order = 2
        lca2.region = lcr2

        land_cover_actions = [lca1, lca2]

        result = job_runner_client.convert_model_to_dictionary(model_run, code_version.parameters, land_cover_actions)
        result_lc = result[constants.JSON_LAND_COVER]

        assert_that(result_lc[constants.JSON_LAND_COVER_BASE_FILE], is_("base_frac_file.nc"))
        assert_that(result_lc[constants.JSON_LAND_COVER_BASE_KEY], is_("frac"))
        assert_that(result_lc[constants.JSON_LAND_COVER_ICE_INDEX], is_(9))
        result_lc_actions = result_lc[constants.JSON_LAND_COVER_ACTIONS]

        assert_that(len(result_lc_actions), is_(2))
        action1 = result_lc_actions[0]
        assert_that(action1[constants.JSON_LAND_COVER_MASK_FILE], is_("region1.nc"))
        assert_that(action1[constants.JSON_LAND_COVER_ORDER], is_(1))
        assert_that(action1[constants.JSON_LAND_COVER_VALUE], is_(9))

        action2 = result_lc_actions[1]
        assert_that(action2[constants.JSON_LAND_COVER_MASK_FILE], is_("region2.nc"))
        assert_that(action2[constants.JSON_LAND_COVER_ORDER], is_(2))
        assert_that(action2[constants.JSON_LAND_COVER_VALUE], is_(5))

        namelist_file_result = result[constants.JSON_MODEL_NAMELIST_FILES][0]
        parameters_result = namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_PARAMETERS]
        assert_that(parameters_result['file'], is_("'" + constants.USER_EDITED_FRACTIONAL_FILENAME + "'"))
        assert_that(parameters_result['frac_name'], is_("'frac'"))

    def test_GIVEN_spinup_start_in_middle_of_driving_data_WHEN_alter_driving_data_start_THEN_driving_data_start_moved(self):
        job_runner_client = JobRunnerClient(config)

        param1 = Parameter(name='data_start')
        param1.namelist = Namelist(name='JULES_DRIVE')
        param1_val = "'1901-01-01 00:00:00'"
        param1.parameter_values = [ParameterValue(value=param1_val)]

        param2 = Parameter(name='spinup_start')
        param2.namelist = Namelist(name='JULES_SPINUP')
        param2_val = "'1950-01-01 00:00:00'"
        param2.parameter_values = [ParameterValue(value=param2_val)]

        parameters = [param1, param2]
        parameters = job_runner_client.alter_driving_data_start(parameters)

        dd_start = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                       constants.JULES_PARAM_DRIVE_DATA_START)
        assert_that(dd_start, is_(datetime.datetime(1940, 1, 1)))

    def test_GIVEN_spinup_start_at_beginning_of_driving_data_WHEN_alter_driving_data_start_THEN_driving_data_start_unmoved(self):
        job_runner_client = JobRunnerClient(config)

        param1 = Parameter(name='data_start')
        param1.namelist = Namelist(name='JULES_DRIVE')
        param1_val = "'1901-01-01 00:00:00'"
        param1.parameter_values = [ParameterValue(value=param1_val)]

        param2 = Parameter(name='spinup_start')
        param2.namelist = Namelist(name='JULES_SPINUP')
        param2_val = "'1901-01-01 00:00:00'"
        param2.parameter_values = [ParameterValue(value=param2_val)]

        parameters = [param1, param2]
        parameters = job_runner_client.alter_driving_data_start(parameters)

        dd_start = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                       constants.JULES_PARAM_DRIVE_DATA_START)
        assert_that(dd_start, is_(datetime.datetime(1901, 1, 1)))
        
    def test_GIVEN_yearly_output_but_run_starts_in_feb_WHEN_alter_output_profiles_THEN_output_start_added(self):
        job_runner_client = JobRunnerClient(config)

        param1 = Parameter(name='main_run_start')
        param1.namelist = Namelist(name='JULES_TIME')
        param1_val = "'1901-02-01 00:00:00'"
        param1.parameter_values = [ParameterValue(value=param1_val)]

        param2 = Parameter(name='main_run_end')
        param2.namelist = Namelist(name='JULES_TIME')
        param2_val = "'1903-02-01 00:00:00'"
        param2.parameter_values = [ParameterValue(value=param2_val)]
        
        param3 = Parameter(name='output_period')
        param3.namelist = Namelist(name='JULES_OUTPUT_PROFILE')
        param3_val = "%s" % constants.JULES_YEARLY_PERIOD
        param3.parameter_values = [ParameterValue(value=param3_val, group_id=1)]

        param4 = Parameter(name='output_start')
        param4.namelist = Namelist(name='JULES_OUTPUT_PROFILE')
        param4.parameter_values = []

        parameters = [param1, param2, param3, param4]
        parameters = job_runner_client.alter_yearly_monthly_output_profiles(parameters)

        output_start = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                           constants.JULES_PARAM_OUTPUT_START,
                                                                           group_id=1)
        assert_that(output_start, is_(datetime.datetime(1902, 1, 1)))

    def test_GIVEN_monthly_output_but_run_starts_mid_month_WHEN_alter_output_profiles_THEN_output_start_added(self):
        job_runner_client = JobRunnerClient(config)

        param1 = Parameter(name='main_run_start')
        param1.namelist = Namelist(name='JULES_TIME')
        param1_val = "'1901-6-25 12:00:00'"
        param1.parameter_values = [ParameterValue(value=param1_val)]

        param2 = Parameter(name='main_run_end')
        param2.namelist = Namelist(name='JULES_TIME')
        param2_val = "'1904-02-01 00:00:00'"
        param2.parameter_values = [ParameterValue(value=param2_val)]

        param3 = Parameter(name='output_period')
        param3.namelist = Namelist(name='JULES_OUTPUT_PROFILE')
        param3_val = "%s" % constants.JULES_MONTHLY_PERIOD
        param3.parameter_values = [ParameterValue(value=param3_val, group_id=1)]

        param4 = Parameter(name='output_start')
        param4.namelist = Namelist(name='JULES_OUTPUT_PROFILE')
        param4.parameter_values = []

        parameters = [param1, param2, param3, param4]
        parameters = job_runner_client.alter_yearly_monthly_output_profiles(parameters)

        output_start = utils.get_first_parameter_value_from_parameter_list(parameters,
                                                                           constants.JULES_PARAM_OUTPUT_START,
                                                                           group_id=1)
        assert_that(output_start, is_(datetime.datetime(1901, 7, 1)))