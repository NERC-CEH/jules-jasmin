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
from hamcrest import assert_that, is_, is_not
from joj.services.dataset import DatasetService
from joj.tests import TestController
from joj.model import session_scope
from joj.utils import constants


class TestDatasetService(TestController):
    """
    Test for the dataset service
    """

    def setUp(self):
        super(TestDatasetService, self).setUp()
        self.dataset_service = DatasetService()
        self.clean_database()

    def test_GIVEN_two_driving_datasets_WHEN_get_driving_datasets_THEN_both_driving_datasets_returned(self):
        user = self.login()
        self.create_two_driving_datasets()
        driving_datasets = self.dataset_service.get_driving_datasets(user)
        assert_that(len(driving_datasets), is_(2 + 1))  # Have to also count the 'user upload driving dataset'
        assert_that(driving_datasets[0].name, is_("driving1"))
        assert_that(driving_datasets[1].description, is_("driving 2 description"))

    def test_GIVEN_two_driving_datasets_WHEN_get_spatial_extent_THEN_correct_spatial_extent_returned(self):
        user = self.login()
        self.create_two_driving_datasets()
        driving_datasets = self.dataset_service.get_driving_datasets(user)
        id = driving_datasets[0].id
        spatial_extent = self.dataset_service.get_spatial_extent(id)
        assert_that(spatial_extent._bound_lat_n, is_(50))
        assert_that(spatial_extent._bound_lat_s, is_(-10))
        assert_that(spatial_extent._bound_lon_w, is_(-15))
        assert_that(spatial_extent._bound_lon_e, is_(30))

    def test_GIVEN_driving_dataset_with_parameter_values_THEN_when_get_driving_dataset_by_id_THEN_namelist_parameters_loaded(self):
        user = self.login()
        self.create_two_driving_datasets()
        driving_datasets = self.dataset_service.get_driving_datasets(user)
        id = driving_datasets[0].id
        dataset = self.dataset_service.get_driving_dataset_by_id(id)
        parameter_values = dataset.parameter_values
        for param_val in parameter_values:
            parameter = param_val.parameter
            namelist = parameter.namelist

    def test_GIVEN_driving_dataset_THEN_when_view_by_non_admin_THEN_not_shown(self):
        user = self.login()
        self.clean_database()
        with session_scope() as session:
            self.create_driving_dataset(session, is_restricted_to_admins=True)

        driving_datasets = self.dataset_service.get_driving_datasets(user)

        assert_that(len(driving_datasets), is_(1), "Driving dataset count (just the single cell one)")

    def test_GIVEN_driving_dataset_THEN_when_view_by_admin_THEN_shown(self):
        user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        self.clean_database()
        with session_scope() as session:
            self.create_driving_dataset(session, is_restricted_to_admins=True)

        driving_datasets = self.dataset_service.get_driving_datasets(user)

        assert_that(len(driving_datasets), is_(2), "Driving dataset count")
