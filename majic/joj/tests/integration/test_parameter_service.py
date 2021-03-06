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