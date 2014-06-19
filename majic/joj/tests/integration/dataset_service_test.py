# header
from hamcrest import assert_that, is_, is_not
from model import Dataset, session_scope, Session, DrivingDataset
from services.dataset import DatasetService
from tests import TestController


class DatasetServiceTest(TestController):
    """
    Test for the dataset service
    """

    def setUp(self):
        super(DatasetServiceTest, self).setUp()
        self.dataset_service = DatasetService()
        self.clean_database()

    def _create_two_driving_datasets(self):
        with session_scope(Session) as session:
            ds1 = Dataset()
            ds1.name = "Driving dataset 1"
            ds1.netcdf_url = "url1"
            ds2 = Dataset()
            ds2.name = "Driving dataset 2"
            ds2.netcdf_url = "url2"
            session.add_all([ds1, ds2])

            driving1 = DrivingDataset()
            driving1.name = "driving1"
            driving1.description = "driving 1 description"
            driving1.dataset = ds1

            driving2 = DrivingDataset()
            driving2.name = "driving2"
            driving2.description = "driving 2 description"
            driving2.dataset = ds2
            session.add_all([driving1, driving2])

    def test_GIVEN_two_driving_datasets_WHEN_get_driving_datasets_THEN_two_driving_datasets_returned(self):
        self._create_two_driving_datasets()
        driving_datasets = self.dataset_service.get_driving_datasets()
        assert_that(len(driving_datasets), is_(2))
        assert_that(driving_datasets[0].name, is_("driving1"))
        assert_that(driving_datasets[1].description, is_("driving 2 description"))

    def test_GIVEN_driving_datasets_WHEN_get_driving_datasets_THEN_driving_datasets_have_datasets_loaded(self):
        self._create_two_driving_datasets()
        driving_dataset = self.dataset_service.get_driving_datasets()[0]
        dataset = driving_dataset.dataset
        assert_that(dataset, is_not(None))
        assert_that(dataset.name, is_("Driving dataset 1"))
        assert_that(dataset.netcdf_url, is_("url1"))