# header
from hamcrest import assert_that, is_, is_not
from joj.services.dataset import DatasetService
from tests import TestController


class DatasetServiceTest(TestController):
    """
    Test for the dataset service
    """

    def setUp(self):
        super(DatasetServiceTest, self).setUp()
        self.dataset_service = DatasetService()
        self.clean_database()

    def test_GIVEN_two_driving_datasets_WHEN_get_driving_datasets_THEN_two_driving_datasets_returned(self):
        self.create_two_driving_datasets()
        driving_datasets = self.dataset_service.get_driving_datasets()
        assert_that(len(driving_datasets), is_(2))
        assert_that(driving_datasets[0].name, is_("driving1"))
        assert_that(driving_datasets[1].description, is_("driving 2 description"))
