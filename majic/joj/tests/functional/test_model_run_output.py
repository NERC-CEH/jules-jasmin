"""
header
"""
from urlparse import urlparse
from hamcrest import assert_that, is_, contains_string, is_not, contains_inanyorder
from lxml import html
from pylons import url
from joj.services.model_run_service import ModelRunService
from joj.tests import TestController
from joj.utils.constants import *
from model import ModelRun, session_scope, Session


class TestModelRunOutput(TestController):
    def setUp(self):
        super(TestModelRunOutput, self).setUp()
        self.clean_database()
        self.user = self.login()
        self.valid_params = {
            'submit': u'Next',
            'ov_select_1': 1,
            'ov_yearly_1': 1,
            'ov_monthly_1': 1,
            'ov_select_2': 1,
            'ov_timestep_2': 1,
            'ov_daily_2': 1,
            'ov_select_3': 1,
            'ov_monthly_3': 1
        }
        self.model_run_service = ModelRunService()
        with session_scope(Session) as session:
            self.model_run = self.model_run_service._create_new_model_run(session, self.user)
            self.model_run.name = "MR1"
            session.add(self.model_run)

    def test_GIVEN_no_model_being_created_WHEN_page_get_THEN_redirect_to_create_model_run(self):
        self.clean_database()
        self.user = self.login()
        response = self.app.get(
            url(controller='model_run', action='output'))
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_model_run_created_WHEN_page_get_THEN_page_loaded(self):
        response = self.app.get(
            url(controller='model_run', action='output'))
        assert_that(response.normal_body, contains_string("Select Output Variables"))

    def test_GIVEN_output_parameters_already_chosen_WHEN_page_get_THEN_parameters_rendered(self):
        self.app.post(
            url(controller='model_run', action='output'),
            params=self.valid_params)
        response = self.app.get(url(controller='model_run', action='output'))
        doc = html.fromstring(response.normal_body)
        
        # Check that the first output variable is displayed, selected and the yearly and monthly period boxes selected:
        output_row_1 = doc.xpath('//div[@id="output_row_1"]/@style')
        assert_that(output_row_1, is_not(contains_string('display:none')))
        ov_select_1 = doc.xpath('//input[@name="ov_select_1"]/@checked')
        ov_yearly_1 = doc.xpath('//input[@name="ov_yearly_1"]/@checked')
        ov_monthly_1 = doc.xpath('//input[@name="ov_monthly_1"]/@checked')
        ov_daily_1 = doc.xpath('//input[@name="ov_daily_1"]/@checked')
        ov_timestep_1 = doc.xpath('//input[@name="ov_timestep_1"]/@checked')
        assert_that(len(ov_select_1), is_(1))
        assert_that(len(ov_yearly_1), is_(1))
        assert_that(len(ov_monthly_1), is_(1))
        assert_that(len(ov_daily_1), is_(0))
        assert_that(len(ov_timestep_1), is_(0))
        
        # For the second we expect the same but with the custom period box selected
        output_row_2 = doc.xpath('//div[@id="output_row_2"]/@style')
        assert_that(output_row_2, is_not(contains_string('display:none')))
        ov_select_2 = doc.xpath('//input[@name="ov_select_2"]/@checked')
        ov_yearly_2 = doc.xpath('//input[@name="ov_yearly_2"]/@checked')
        ov_monthly_2 = doc.xpath('//input[@name="ov_monthly_2"]/@checked')
        ov_daily_2 = doc.xpath('//input[@name="ov_daily_2"]/@checked')
        ov_timestep_2 = doc.xpath('//input[@name="ov_timestep_2"]/@checked')
        assert_that(len(ov_select_2), is_(1))
        assert_that(len(ov_yearly_2), is_(0))
        assert_that(len(ov_monthly_2), is_(0))
        assert_that(len(ov_daily_2), is_(1))
        assert_that(len(ov_timestep_2), is_(1))
        
        # For the third we expect the monthly box selected
        output_row_3 = doc.xpath('//div[@id="output_row_3"]/@style')
        assert_that(output_row_3, is_not(contains_string('display:none')))
        ov_select_3 = doc.xpath('//input[@name="ov_select_3"]/@checked')
        ov_yearly_3 = doc.xpath('//input[@name="ov_yearly_3"]/@checked')
        ov_monthly_3 = doc.xpath('//input[@name="ov_monthly_3"]/@checked')
        ov_daily_3 = doc.xpath('//input[@name="ov_daily_3"]/@checked')
        ov_timestep_3 = doc.xpath('//input[@name="ov_timestep_3"]/@checked')
        assert_that(len(ov_select_3), is_(1))
        assert_that(len(ov_yearly_3), is_(0))
        assert_that(len(ov_monthly_3), is_(1))
        assert_that(len(ov_daily_3), is_(0))
        assert_that(len(ov_timestep_3), is_(0))
        
        # Finally we check that no other output parameters are selected or visible
        ov_selects = doc.xpath('//input[contains(@name, "ov_select_") and not(@checked)]')
        n_output_params = len(self.model_run_service.get_output_variables(include_depends_on_nsmax=False))
        assert_that(len(ov_selects), is_(n_output_params - 3))

        invisible_rows = doc.xpath('//div[contains(@id, "output_row_") and contains(@style, "display:none")]')
        assert_that(len(invisible_rows), is_(n_output_params - 3))

    def test_GIVEN_selected_outputs_WHEN_post_THEN_redirected_to_next_page(self):
        response = self.app.post(
            url(controller='model_run', action='output'),
            params=self.valid_params)
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='parameters')), "url")

    def test_GIVEN_selected_outputs_WHEN_post_THEN_params_stored_in_database(self):
        self.app.post(
            url(controller='model_run', action='output'),
            params=self.valid_params)

        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        # Check we have the right number of profiles
        n_expected = 5
        p_output_nprofiles = model_run.get_parameter_values(JULES_PARAM_OUTPUT_NPROFILES)[0].get_value_as_python()
        assert_that(p_output_nprofiles, is_(n_expected))

        pv_var = model_run.get_parameter_values(JULES_PARAM_OUTPUT_VAR)
        pv_nvars = model_run.get_parameter_values(JULES_PARAM_OUTPUT_NVARS)
        pv_profile_name = model_run.get_parameter_values(JULES_PARAM_OUTPUT_PROFILE_NAME)
        pv_output_main_run = model_run.get_parameter_values(JULES_PARAM_OUTPUT_MAIN_RUN)
        pv_output_period = model_run.get_parameter_values(JULES_PARAM_OUTPUT_PERIOD)
        pv_output_types = model_run.get_parameter_values(JULES_PARAM_OUTPUT_TYPE)

        # Check they are all 5
        assert_that(len(pv_var), is_(n_expected))
        assert_that(len(pv_nvars), is_(n_expected))
        assert_that(len(pv_profile_name), is_(n_expected))
        assert_that(len(pv_output_main_run), is_(n_expected))
        assert_that(len(pv_output_period), is_(n_expected))
        assert_that(len(pv_output_types), is_(n_expected))

        # Create list of values so we can check they are correct (easier than checking ParameterValue objects)
        var_vals = [pv.get_value_as_python() for pv in pv_var]
        nvars_vals = [pv.get_value_as_python() for pv in pv_nvars]
        profile_name_vals = [pv.get_value_as_python() for pv in pv_profile_name]
        output_main_run_vals = [pv.get_value_as_python() for pv in pv_output_main_run]
        output_period_vals = [pv.get_value_as_python() for pv in pv_output_period]
        output_types = [pv.get_value_as_python() for pv in pv_output_types]

        # Check that we got the correct values
        # The order is assured consistent by the sort in model_run.get_parameter_values()
        output_var_1 = self.model_run_service.get_output_variable_by_id(1)
        output_var_2 = self.model_run_service.get_output_variable_by_id(2)
        output_var_3 = self.model_run_service.get_output_variable_by_id(3)
        assert_that(var_vals, is_([output_var_1.name, output_var_1.name, output_var_2.name,
                                   output_var_2.name, output_var_3.name]))
        assert_that(nvars_vals, is_([1, 1, 1, 1, 1]))
        assert_that(profile_name_vals, is_([output_var_1.name + '_yearly', output_var_1.name + '_monthly',
                                            output_var_2.name + '_daily', output_var_2.name + '_timestep',
                                            output_var_3.name + '_monthly']))
        assert_that(output_main_run_vals, is_([True, True, True, True, True]))
        assert_that(output_period_vals, is_([-2, -1, 24 * 60 * 60, TIMESTEP_LEN, -1]))
        assert_that(output_types, is_(['M', 'M', 'M', 'M', 'M']))

    def test_GIVEN_selected_outputs_WHEN_go_back_THEN_previous_paged_rendered(self):
        params = self.valid_params
        params['submit'] = u'Back'
        response = self.app.post(
            url(controller='model_run', action='output'),
            params=params)
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='extents')), "url")

    def test_GIVEN_nsmax_set_zero_WHEN_page_get_THEN_nsmax_parameters_not_available_on_page(self):
        self.model_run_service.save_parameter(JULES_PARAM_NSMAX, 0, self.user)
        response = self.app.get(
            url(controller='model_run', action='output'))
        for output_name in DEPENDS_ON_NSMAX:
            assert_that(response.normal_body, is_not(contains_string(output_name)))

    def test_GIVEN_nsmax_set_three_WHEN_page_get_THEN_nsmax_parameters_shown_on_page(self):
        self.model_run_service.save_parameter(JULES_PARAM_NSMAX, 3, self.user)
        response = self.app.get(
            url(controller='model_run', action='output'))
        output_variables = self.model_run_service.get_output_variables(include_depends_on_nsmax=True)
        for output_variable in output_variables:
            if output_variable.depends_on_nsmax:
                assert_that(response.normal_body, contains_string(str(output_variable.name)))

    def test_GIVEN_page_already_run_once_WHEN_page_post_THEN_new_parameters_overwrite_old_parameters(self):
        self.app.post(
            url(controller='model_run', action='output'),
            params=self.valid_params)
        new_params = {
            'submit': u'Next',
            'ov_select_1': 1,
            'ov_timestep_1': 1,
            'ov_select_10': 1,
            'ov_yearly_10': 1,
            'ov_monthly_10': 1
        }
        self.app.post(
            url(controller='model_run', action='output'),
            params=new_params)

        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        # Check we have the right number of profiles
        n_expected = 3
        p_output_nprofiles = model_run.get_parameter_values(JULES_PARAM_OUTPUT_NPROFILES)[0].get_value_as_python()
        assert_that(p_output_nprofiles, is_(n_expected))

        pv_var = model_run.get_parameter_values(JULES_PARAM_OUTPUT_VAR)
        pv_nvars = model_run.get_parameter_values(JULES_PARAM_OUTPUT_NVARS)
        pv_profile_name = model_run.get_parameter_values(JULES_PARAM_OUTPUT_PROFILE_NAME)
        pv_output_main_run = model_run.get_parameter_values(JULES_PARAM_OUTPUT_MAIN_RUN)
        pv_output_period = model_run.get_parameter_values(JULES_PARAM_OUTPUT_PERIOD)
        pv_output_types = model_run.get_parameter_values(JULES_PARAM_OUTPUT_TYPE)

        # Check they are all 3 (not 4 anymore)
        assert_that(len(pv_var), is_(n_expected))
        assert_that(len(pv_nvars), is_(n_expected))
        assert_that(len(pv_profile_name), is_(n_expected))
        assert_that(len(pv_output_main_run), is_(n_expected))
        assert_that(len(pv_output_period), is_(n_expected))
        assert_that(len(pv_output_types), is_(n_expected))

        # Create list of values so we can check they are correct (easier than checking ParameterValue objects)
        var_vals = [pv.get_value_as_python() for pv in pv_var]
        nvars_vals = [pv.get_value_as_python() for pv in pv_nvars]
        profile_name_vals = [pv.get_value_as_python() for pv in pv_profile_name]
        output_main_run_vals = [pv.get_value_as_python() for pv in pv_output_main_run]
        output_period_vals = [pv.get_value_as_python() for pv in pv_output_period]
        output_types = [pv.get_value_as_python() for pv in pv_output_types]

        # Check that we got the correct values
        # The order is assured consistent by the sort in model_run.get_parameter_values()
        output_var_1 = self.model_run_service.get_output_variable_by_id(1)
        output_var_10 = self.model_run_service.get_output_variable_by_id(10)
        assert_that(var_vals, is_([output_var_10.name, output_var_10.name, output_var_1.name]))
        assert_that(nvars_vals, is_([1, 1, 1]))
        assert_that(profile_name_vals, is_([output_var_10.name + '_yearly', output_var_10.name + '_monthly',
                                            output_var_1.name + '_timestep']))
        assert_that(output_main_run_vals, is_([True, True, True]))
        assert_that(output_period_vals, is_([-2, -1, TIMESTEP_LEN]))
        assert_that(output_types, is_(['M', 'M', 'M']))
