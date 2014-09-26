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

from mock import MagicMock
from hamcrest import *

from joj.tests.base import BaseTest
from joj.model import User
from joj.services.model_run_service import ModelRunService


class ModelRunServiceTest(BaseTest):

    def setUp(self):

        super(ModelRunServiceTest, self).setUp()

        self._mock_session.query = MagicMock()
        self.model_run_service = ModelRunService(self._mock_session)

    def test_GIVEN_no_model_runs_WHEN_get_model_list_THEN_empty_list_returned(self):

        mock_query_result = MagicMock()
        mock_query_result.all = MagicMock(return_value=[])

        mock_query = MagicMock()
        mock_query.filter = MagicMock()
        mock_query.filter.return_value = mock_query_result
        self._mock_session.query.return_value = mock_query

        user = User()
        models = self.model_run_service.get_models_for_user(user)

        assert_that(len(models), is_(0), "There should be no model for the user")
