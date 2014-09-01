"""
# header
"""
import datetime
from hamcrest import *
from joj.tests import *
from joj.utils import constants, utils
from joj.model import session_scope, LandCoverRegion, LandCoverRegionCategory, DrivingDataset, Session
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams


class TestDrivingDataEditOrAdd(TestController):

    def setUp(self):
        super(TestDrivingDataEditOrAdd, self).setUp()
        self.clean_database()
        self.extra_parameter = "an extra parameter value"
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

        assert_that(response.normal_body, contains_string('Restricted to Admins'))

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

    def create_valid_post_values(self):
        self.new_driving_dataset = DrivingDataset()
        self.new_driving_dataset.name = "new_driving_dataset"
        self.new_driving_dataset.description = "description"
        self.new_driving_dataset.geographic_region = "geographic_region"
        self.new_driving_dataset.spatial_resolution = "spatial_resolution"
        self.new_driving_dataset.temporal_resolution = "temporal_resolution"
        self.new_driving_dataset.boundary_lat_north = 30
        self.new_driving_dataset.boundary_lat_south = -30
        self.new_driving_dataset.boundary_lon_east = 30
        self.new_driving_dataset.boundary_lon_west = -30

        self.new_driving_dataset.is_restricted_to_admins = True

        jules_params = DrivingDatasetJulesParams(
            data_start=str(datetime.datetime(2013, 1, 1, 0, 0, 0)),
            data_end=str(datetime.datetime(2013, 2, 1, 0, 0, 0)))
        jules_params.set_from(self.new_driving_dataset, [])
        valid_params = jules_params.create_values_dict({})
        return valid_params

    def test_GIVEN_valid_data_WHEN_create_new_THEN_new_set_created(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        valid_params = self.create_valid_post_values()

        response = self.app.post(
            url=url(controller='driving_data', action='edit'),
            params=valid_params,
            expect_errors=True
        )

        with session_scope(Session) as session:
            driving_dataset = session\
                .query(DrivingDataset)\
                .filter(DrivingDataset.name == self.new_driving_dataset.name)\
                .one()

        assert_that(response.status_code, is_(302), "redirect after successful post")
        assert_that(driving_dataset.name, is_(self.new_driving_dataset.name), "name")

    def test_GIVEN_invalid_data_WHEN_create_new_THEN_error(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        invalid_values = \
            [
                ["name", "", "enter a value"],
                ["description", "", "enter a value"],
                ["geographic_region", "", "enter a value"],
                ["spatial_resolution", "", "enter a value"],
                ["temporal_resolution", "", "enter a value"],
                ["boundary_lat_north", "nan", "enter a number"],
                ["boundary_lat_south", "1000", "enter a number that is 90 or smaller"],
                ["boundary_lon_east", "-800", "enter a number that is -180 or greater"],
                ["boundary_lon_west", "", "enter a value"],
                ["driving_data_start", "", "Please enter a date"],
                ["driving_data_end", "n.a.t.", "Enter date as YYYY-MM-DD HH:MM"]
            ]

        for invalid_key, invalid_value, invalid_error in invalid_values:

            valid_params = self.create_valid_post_values()
            valid_params[invalid_key] = invalid_value

            response = self.app.post(
                url=url(controller='driving_data', action='edit'),
                params=valid_params,
                expect_errors=True
            )

            assert_that(response.status_code, is_(200), "no redirect after error for key '%s'" % invalid_key)
            assert_that(response.normal_body, contains_string(invalid_error), "In '%s'" % invalid_key)
