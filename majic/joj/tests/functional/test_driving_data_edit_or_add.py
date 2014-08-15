"""
# header
"""
from hamcrest import *
from joj.tests import *
from joj.utils import constants, utils
from joj.model import session_scope, LandCoverRegion, LandCoverRegionCategory
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams


class TestDrivingDataEditOrAdd(TestController):

    def setUp(self):
        super(TestDrivingDataEditOrAdd, self).setUp()
        self.clean_database()
        self.extra_parameter = "extra_parameter"
        self.driving_dataset_jules_params = DrivingDatasetJulesParams(
            dataperiod=1800,
            drive_file="jules_param_drive_file",
            drive_var=['drive var 1', 'drive var 2'],
            var_names=['name1', 'name2'],
            var_templates=['template1', 'template2'],
            var_interps=['interp1', 'interp2'],
            nx='jules_param_nx',
            ny='jules_param_ny',
            x_dim_name='jules_param_x_dim_name',
            y_dim_name='jules_param_y_dim_name',
            time_dim_name='jules_param_time_dim_name',
            latlon_file='latlon_file',
            latlon_lat_name='latlon_lat_name',
            latlon_lon_name='latlon_lon_name',
            land_frac_file='land_frac_file',
            land_frac_frac_name='land_frac_frac_name',
            frac_file='frac_file_file_name',
            frac_frac_dim_name='frac_frac_dim_name',
            frac_type_dim_name='frac_type_dim_name',
            soil_props_file='soil_props_file',
            extra_parameters={1: self.extra_parameter})

        with session_scope() as session:
            self.driving_dataset = self.create_driving_dataset(
                session,
                self.driving_dataset_jules_params)

    def test_GIVEN_not_logged_in_WHEN_edit_THEN_redirects(self):
        response = self.app.get(
            url=url(controller='driving_data', action='edit', id=self.driving_dataset.id),
            expect_errors=True
        )
        assert_that(response.status_code, is_(302), "Response is redirect")

    def test_GIVEN_non_admin_WHEN_edit_THEN_returns_error(self):
        self.login()
        response = self.app.get(
            url=url(controller='driving_data', action='edit', id=self.driving_dataset.id),
            expect_errors=True
        )
        assert_that(response.normal_body, contains_string("Not found"))

    def test_GIVEN_one_data_set_WHEN_list_THEN_returns_data_set(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        response = self.app.get(
            url=url(controller='driving_data', action='edit', id=self.driving_dataset.id),
            expect_errors=True
        )

        # driving data
        assert_that(response.normal_body, contains_string(self.driving_dataset.name))
        assert_that(response.normal_body, contains_string(str(self.driving_dataset_jules_params.values['driving_data_period'])))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['drive_file']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['drive_nx']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['drive_ny']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['drive_x_dim_name']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['drive_y_dim_name']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['drive_time_dim_name']))
        for drive_var in self.driving_dataset_jules_params.values['drive_vars']:
            assert_that(response.normal_body, contains_string(drive_var))
        for drive_var_name in self.driving_dataset_jules_params.values['drive_var_names']:
            assert_that(response.normal_body, contains_string(drive_var_name))
        for drive_var_template in self.driving_dataset_jules_params.values['drive_var_templates']:
            assert_that(response.normal_body, contains_string(drive_var_template))
        for drive_var_interp in self.driving_dataset_jules_params.values['drive_var_interps']:
            assert_that(response.normal_body, contains_string(drive_var_interp))

        #ancilary parameters
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['latlon_file']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['latlon_lat_name']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['latlon_lon_name']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['land_frac_file']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['land_frac_frac_name']))

        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['frac_file']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['frac_frac_name']))
        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['frac_type_dim_name']))

        assert_that(response.normal_body, contains_string(self.driving_dataset_jules_params.values['soil_props_file']))

        assert_that(response.normal_body, contains_string(self.extra_parameter))

    def test_GIVEN_no_data_set_WHEN_list_THEN_returns_empty_data_set(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        response = self.app.get(
            url=url(controller='driving_data', action='edit'),
            expect_errors=True
        )

        assert_that(response.normal_body, contains_string('New Driving Data Set'))

    def test_GIVEN_data_set_with_a_region_WHEN_list_THEN_returns_mask(self):

        with session_scope() as session:
            category = LandCoverRegionCategory()
            category.driving_dataset = self.driving_dataset
            category.name = "mycategory"

            region = LandCoverRegion()
            region.name = "myregion"
            region.category = category
            region.mask_file = "data/file_path"
            session.add(category)


        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        response = self.app.get(
            url=url(controller='driving_data', action='edit', id=self.driving_dataset.id),
            expect_errors=True
        )

        assert_that(response.normal_body, contains_string(category.name))
        assert_that(response.normal_body, contains_string(region.name))
        assert_that(response.normal_body, contains_string(region.mask_file))