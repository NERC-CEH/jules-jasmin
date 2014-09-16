"""
header
"""
from hamcrest import assert_that, is_
from joj.services.parameter_service import ParameterService
from joj.model import session_scope, ParameterValue, ModelRun
from joj.tests import TestController
from joj.utils import constants


class TestParameterService(TestController):

    def setUp(self):
        super(TestParameterService, self).setUp()
        self.parameter_service = ParameterService()
        self.clean_database()

    def test_GIVEN_valid_output_and_model_run_WHEN_get_output_variable_name_THEN_output_variable_returned_(self):
        with session_scope() as session:
            param_val_output = ParameterValue()
            param_val_output.set_value_from_python('gpp_gb')

            parameter_service = ParameterService()
            param_output = parameter_service.get_parameter_by_constant(constants.JULES_PARAM_OUTPUT_VAR, session)
            param_output.parameter_values = [param_val_output]

            model_run = ModelRun()
            model_run.parameter_values = [param_val_output]

            session.add(model_run)
            session.commit()

        var = self.parameter_service.get_output_variable_name(model_run.id, param_val_output.id)
        assert_that(var, is_('gpp_gb'))