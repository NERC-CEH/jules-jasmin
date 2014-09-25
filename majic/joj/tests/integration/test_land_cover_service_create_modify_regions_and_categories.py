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
from hamcrest import *
from mock import Mock
from pylons import config

from joj.model import session_scope, LandCoverRegionCategory, LandCoverRegion, DrivingDataset
from joj.services.land_cover_service import LandCoverService
from joj.services.dataset import DatasetService
from joj.services.model_run_service import ModelRunService
from joj.services.dap_client.dap_client import DapClientException
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.utils import constants
from joj.services.general import ServiceException
from joj.tests import TestController


class TestLandCoverServiceForCreateAndModifyCategoriesAndRegions(TestController):
    def setUp(self):
        dap_client_factory =Mock(DapClientFactory)
        self.land_cover_service = LandCoverService(dap_client_factory=dap_client_factory)
        self.model_run_service = ModelRunService()
        self.dataset_service = DatasetService()
        self.clean_database()
        self.user = self.login()


    def create_values(self, expected_categories, expected_names, expected_paths, expected_ids):
        values = []
        for name, category, path, id in zip(expected_names, expected_categories, expected_paths, expected_ids):
            values.append({
                'id': id,
                'name': name,
                'category': category,
                'path': path})
        return values

    def assert_regions_are_correct(self, driving_dataset, expected_categories, expected_names, expected_paths, values):
        with session_scope() as session:
            regions = LandCoverService().get_land_cover_regions(driving_dataset.id)
        assert_that(len(regions), is_(len(values)), "number of regions")
        for name, category, path, region in zip(expected_names, expected_categories, expected_paths, regions):
            assert_that(region.name, is_(name), "name")
            assert_that(region.category.name, is_(category), "category")
            assert_that(region.mask_file, is_(path), "path")
        return regions

    def test_GIVEN_no_values_WHEN_add_to_new_dataset_THEN_nothing_changes(self):
        with session_scope() as session:
            driving_dataset = self.create_driving_dataset(session)

            #WHEN
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, [])

        with session_scope() as session:
            regions = LandCoverService().get_land_cover_regions(driving_dataset.id)
        assert_that(len(regions), is_(0), "number of regions")

    def test_GIVEN_one_values_WHEN_add_to_new_dataset_THEN_value_is_added(self):
        expected_names = ["name"]
        expected_categories = ["category"]
        expected_paths = ["expected_paths"]
        expected_ids = [""]
        values = self.create_values(expected_categories, expected_names, expected_paths, expected_ids)

        with session_scope() as session:
            driving_dataset = self.create_driving_dataset(session)

            #WHEN
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, values)

        self.assert_regions_are_correct(driving_dataset, expected_categories, expected_names, expected_paths, values)

    def test_GIVEN_two_values_with_different_categories_WHEN_add_to_new_dataset_THEN_values_are_added(self):
        expected_names = ["name", "name2"]
        expected_categories = ["category", "category2"]
        expected_paths = ["expected_paths", "expected_path2"]
        expected_ids = [""]
        values = self.create_values(expected_categories, expected_names, expected_paths, expected_ids)

        with session_scope() as session:
            driving_dataset = self.create_driving_dataset(session)

            #WHEN
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, values)

        self.assert_regions_are_correct(driving_dataset, expected_categories, expected_names, expected_paths, values)

    def test_GIVEN_two_values_with_same_categories_WHEN_add_to_new_dataset_THEN_values_are_added_only_one_category(self):
        expected_names = ["name", "name2"]
        expected_categories = ["category", "category"]
        expected_paths = ["expected_paths", "expected_path2"]
        expected_ids = ["", ""]
        values = self.create_values(expected_categories, expected_names, expected_paths, expected_ids)

        with session_scope() as session:
            driving_dataset = self.create_driving_dataset(session)

            #WHEN
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, values)

        regions = self.assert_regions_are_correct(driving_dataset, expected_categories, expected_names, expected_paths, values)
        assert_that(regions[0].category, same_instance(regions[1].category), "categories are the same")

    def test_GIVEN_one_value_WHEN_add_to_existing_empty_dataset_THEN_value_is_added(self):
        expected_names = ["name"]
        expected_categories = ["category"]
        expected_paths = ["expected_paths"]
        expected_ids = [""]
        values = self.create_values(expected_categories, expected_names, expected_paths, expected_ids)

        with session_scope() as session:
            driving_dataset = self.create_driving_dataset(session)

        with session_scope() as session:
            driving_dataset = session.query(DrivingDataset).get(driving_dataset.id)
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, values)

        self.assert_regions_are_correct(driving_dataset, expected_categories, expected_names, expected_paths, values)

    def test_GIVEN_one_value_WHEN_add_to_existing_dataset_with_mask_in_already_THEN_value_is_modified(self):

        with session_scope() as session:
            driving_dataset = DrivingDataset()
            original = self.create_values(["orig"], ["category"], ["orig"], [""])
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, original)
            session.add(driving_dataset)
        regions = self.land_cover_service.get_land_cover_regions(driving_dataset.id)
        expected_ids = [regions[0].id]
        expected_names = ["name"]
        expected_categories = ["category"]
        expected_paths = ["expected_paths"]
        values = self.create_values(expected_categories, expected_names, expected_paths, expected_ids)

        with session_scope() as session:
            driving_dataset = session.query(DrivingDataset).get(driving_dataset.id)
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, values)

        self.assert_regions_are_correct(driving_dataset, expected_categories, expected_names, expected_paths, values)

    def test_GIVEN_one_value_WHEN_add_to_existing_dataset_with_mask_in_already_in_different_category_THEN_value_is_modified_and_only_one_category(self):

        with session_scope() as session:
            driving_dataset = DrivingDataset()
            original = self.create_values(["orig"], ["orig"], ["orig"], [""])
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, original)
            session.add(driving_dataset)
        regions = self.land_cover_service.get_land_cover_regions(driving_dataset.id)
        expected_ids = [regions[0].id]
        expected_names = ["name"]
        expected_categories = ["category"]
        expected_paths = ["expected_paths"]
        values = self.create_values(expected_categories, expected_names, expected_paths, expected_ids)

        with session_scope() as session:
            driving_dataset = session.query(DrivingDataset).get(driving_dataset.id)
            self.land_cover_service.update_regions_and_categories_in_session(session, driving_dataset, values)

        self.assert_regions_are_correct(driving_dataset, expected_categories, expected_names, expected_paths, values)

        categories = self.land_cover_service.get_land_cover_categories(driving_dataset.id)
        assert_that(len(categories), is_(1), "number of categories")
