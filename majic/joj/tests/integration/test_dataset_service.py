# header
from hamcrest import assert_that, is_, is_not
from services.dataset import DatasetService
from tests import TestController


class TestDatasetService(TestController):
    """
    Test for the dataset service
    """

    def setUp(self):
        super(TestDatasetService, self).setUp()
        self.dataset_service = DatasetService()
        self.clean_database()

    def test_GIVEN_two_driving_datasets_WHEN_get_driving_datasets_THEN_two_driving_datasets_returned(self):
        self.create_two_driving_datasets()
        driving_datasets = self.dataset_service.get_driving_datasets()
        assert_that(len(driving_datasets), is_(2))
        assert_that(driving_datasets[0].name, is_("driving1"))
        assert_that(driving_datasets[1].description, is_("driving 2 description"))

    def test_GIVEN_two_driving_datasets_WHEN_get_spatial_extent_THEN_correct_spatial_extent_returned(self):
        self.create_two_driving_datasets()
        driving_datasets = self.dataset_service.get_driving_datasets()
        id = driving_datasets[0].id
        spatial_extent = self.dataset_service.get_spatial_extent(id)
        assert_that(spatial_extent._bound_lat_n, is_(50))
        assert_that(spatial_extent._bound_lat_s, is_(-10))
        assert_that(spatial_extent._bound_lon_w, is_(-15))
        assert_that(spatial_extent._bound_lon_e, is_(30))
