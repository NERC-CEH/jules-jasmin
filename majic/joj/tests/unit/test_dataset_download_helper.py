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
from mock import MagicMock
from sqlalchemy.orm.exc import NoResultFound

from joj.tests.base import BaseTest
from joj.utils.download.netcdf_dataset_download_helper import NetcdfDatasetDownloadHelper
from joj.model import User, ModelRun
from joj.model.output_variable import OutputVariable


class TestDatasetDownloadHelper(BaseTest):

    def setUp(self):
        model_run = ModelRun()
        model_run.name = "Model Run"
        model_run.user_id = 10

        output_var = OutputVariable()
        output_var.name = "gpp_gb"
        output_var.description = "Gridbox gross primary productivity"

        model_run_service = MagicMock()
        model_run_service.get_model_by_id = MagicMock(return_value=model_run)
        model_run_service.get_output_variable_by_id = MagicMock(return_value=output_var)

        self.download_helper = NetcdfDatasetDownloadHelper(model_run_service)
        self.user = User()
        self.user.name = 'User Name'
        self.user.id = 10

    def test_GIVEN_non_numeric_model_run_id_WHEN_validate_THEN_ValueError(self):
        params = {
            'model_run_id': u'../../12',
            'output': u'123',
            'period': u'Monthly'
        }
        with self.assertRaises(ValueError):
            self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_missing_model_run_id_WHEN_validate_THEN_ValueError(self):
        params = {
            'output': u'123',
            'period': u'Monthly'
        }
        with self.assertRaises(ValueError):
            self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_non_numeric_output_WHEN_validate_THEN_ValueError(self):
        params = {
            'model_run_id': u'12',
            'output': u'../../12',
            'period': u'Monthly'
        }
        with self.assertRaises(ValueError):
            self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_missing_output_WHEN_validate_THEN_ValueError(self):
        params = {
            'model_run_id': u'12',
            'period': u'Monthly'
        }
        with self.assertRaises(ValueError):
            self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_output_not_valid_WHEN_validate_THEN_ValueError(self):
        self.download_helper.model_run_service.get_model_by_id = MagicMock(side_effect=NoResultFound)
        params = {
            'model_run_id': u'12',
            'output': u'1234',
            'period': u'Daily',
            'year': u'1901'
        }
        with self.assertRaises(ValueError):
            model_run, output, period, year = self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_invalid_period_WHEN_validate_THEN_ValueError(self):
        params = {
            'model_run_id': u'12',
            'output': u'123',
            'period': u'../../Daily'
        }
        with self.assertRaises(ValueError):
            self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_non_numeric_year_WHEN_validate_THEN_ValueError(self):
        params = {
            'model_run_id': u'12',
            'output': u'123',
            'period': u'Daily',
            'year': '../../1901'
        }
        with self.assertRaises(ValueError):
            self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_missing_year_WHEN_validate_THEN_validates(self):
        params = {
            'model_run_id': u'12',
            'output': u'123',
            'period': u'Daily',
        }
        model_run, output, period, year = self.download_helper.validate_parameters(params, self.user)
        assert_that(model_run, is_(12))
        assert_that(output, is_('gpp_gb'))
        assert_that(period, is_('Daily'))
        assert_that(year, is_(None))

    def test_GIVEN_all_present_and_correct_WHEN_validate_THEN_validates(self):
        params = {
            'model_run_id': u'12',
            'output': u'123',
            'period': u'Daily',
            'year': u'1901'
        }
        model_run, output, period, year = self.download_helper.validate_parameters(params, self.user)
        assert_that(model_run, is_(12))
        assert_that(output, is_('gpp_gb'))
        assert_that(period, is_('Daily'))
        assert_that(year, is_(1901))

    def test_GIVEN_model_run_id_not_viewable_by_user_WHEN_validate_THEN_NoResultFound(self):
        self.download_helper.model_run_service.get_model_by_id = MagicMock(side_effect=NoResultFound)
        params = {
            'model_run_id': u'13',
            'output': u'123',
            'period': u'Daily',
            'year': u'1901'
        }
        with self.assertRaises(NoResultFound):
            self.download_helper.validate_parameters(params, self.user)

    def test_GIVEN_year_WHEN_generate_file_path_THEN_file_path_correctly_generated(self):
        path = self.download_helper.generate_output_file_path(12, 'gpp_gb', 'daily', 1901, False)
        assert_that(path, is_('run12/output/majic.gpp_gb_daily.1901.nc'))

    def test_GIVEN_year_but_not_needed_WHEN_generate_file_path_THEN_file_path_correctly_generated(self):
        path = self.download_helper.generate_output_file_path(12, 'gpp_gb', 'monthly', 1901, False)
        assert_that(path, is_('run12/output/majic.gpp_gb_monthly.nc'))

    def test_GIVEN_no_year_WHEN_generate_file_path_THEN_file_path_correctly_generated(self):
        path = self.download_helper.generate_output_file_path(12, 'gpp_gb', 'monthly', False)
        assert_that(path, is_('run12/output/majic.gpp_gb_monthly.nc'))