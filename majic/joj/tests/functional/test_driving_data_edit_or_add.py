"""
# header
"""
import datetime
from hamcrest import *
from joj.tests import *
from joj.utils import constants, utils
from joj.model import session_scope, LandCoverRegion, LandCoverRegionCategory, DrivingDataset, Session, \
    DrivingDatasetParameterValue
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams
from joj.services.dataset import DatasetService
from joj.services.land_cover_service import LandCoverService
from joj.services.model_run_service import ModelRunService


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
        for drive_var in self.driving_dataset_jules_params.values['drive_var_vars']:
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

        self.new_driving_dataset.view_order_index = 1
        self.new_driving_dataset.usage_order_index = 1

        self.new_driving_dataset.is_restricted_to_admins = True

        self.new_driving_dataset.time_start = datetime.datetime(2010, 1, 1, 10, 00)
        self.new_driving_dataset.time_end = datetime.datetime(2010, 2, 1, 10, 00)

        self.drive_var = ['drive var 1', 'drive var 2']
        jules_params = DrivingDatasetJulesParams(
            driving_dateset=self.new_driving_dataset,
            data_start="2010-01-01 10:00",
            data_end="2010-02-01 10:00",
            dataperiod=1800,
            drive_file="jules_param_drive_file",
            drive_var=self.drive_var,
            var_names=['name1', 'name2'],
            var_templates=['template1', 'template2'],
            var_interps=['interp1', 'interp2'],
            nx=10,
            ny=20,
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
            extra_parameters={1: self.extra_parameter}
            )
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

        assert_that(response.status_code, is_(302), "no redirect after successful post got %s" % response.normal_body)

        with session_scope() as session:
            driving_dataset_id = session\
                .query(DrivingDataset)\
                .filter(DrivingDataset.name == self.new_driving_dataset.name)\
                .one().id
            driving_dataset = DatasetService().get_driving_dataset_by_id(driving_dataset_id)

        assert_that(driving_dataset.name, is_(self.new_driving_dataset.name), "name")
        assert_that(driving_dataset.description, is_(self.new_driving_dataset.description), "description")
        assert_that(driving_dataset.geographic_region, is_(self.new_driving_dataset.geographic_region), "geographic_region")
        assert_that(driving_dataset.spatial_resolution, is_(self.new_driving_dataset.spatial_resolution), "spatial_resolution")
        assert_that(driving_dataset.temporal_resolution, is_(self.new_driving_dataset.temporal_resolution), "temporal_resolution")
        assert_that(driving_dataset.boundary_lat_north, is_(self.new_driving_dataset.boundary_lat_north), "boundary_lat_north")
        assert_that(driving_dataset.boundary_lat_south, is_(self.new_driving_dataset.boundary_lat_south), "boundary_lat_south")
        assert_that(driving_dataset.boundary_lon_east, is_(self.new_driving_dataset.boundary_lon_east), "boundary_lon_east")
        assert_that(driving_dataset.boundary_lon_west, is_(self.new_driving_dataset.boundary_lon_west), "boundary_lon_west")
        assert_that(driving_dataset.view_order_index, is_(self.new_driving_dataset.view_order_index), "view_order_index")
        assert_that(driving_dataset.usage_order_index, is_(self.new_driving_dataset.usage_order_index), "usage_order_index")
        assert_that(driving_dataset.time_start, is_(self.new_driving_dataset.time_start), "start time")
        assert_that(driving_dataset.time_end, is_(self.new_driving_dataset.time_end), "end time")

        assert_that(driving_dataset.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_START),
                    is_(self.new_driving_dataset.time_start), "start time")
        assert_that(driving_dataset.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_END),
                    is_(self.new_driving_dataset.time_end), "end time")
        assert_that(driving_dataset.get_python_parameter_value(constants.JULES_PARAM_INPUT_GRID_NX),
                    is_(valid_params["drive_nx"]), "nx")
        assert_that(driving_dataset.get_python_parameter_value(constants.JULES_PARAM_DRIVE_NVARS),
                    is_(valid_params["drive_nvars"]), "drive_nvars")
        assert_that(driving_dataset.get_python_parameter_value(constants.JULES_PARAM_DRIVE_VAR),
                    is_(self.drive_var), "vars")
        assert_that(len(driving_dataset.locations), is_(4), "number of locations (2 ancils 2 driving datasets)")

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
                ["driving_data_end", "n.a.t.", "Enter date as YYYY-MM-DD HH:MM"],
                ["view_order_index", "", "enter a value"],
                ["usage_order_index", "nan", "Please enter an integer value"]
            ]

        for name, const in DrivingDatasetJulesParams()._names_constant_dict.iteritems():
            if name not in ['driving_data_start', 'driving_data_end', 'drive_nvars', 'drive_var_interps', 'drive_var_names', 'drive_var_templates', 'drive_var_vars']:
                invalid_values.append([name, "", "enter a value"])

        for invalid_key, invalid_value, invalid_error in invalid_values:

            valid_params = self.create_valid_post_values()
            valid_params[invalid_key] = invalid_value

            response = self.app.post(
                url=url(controller='driving_data', action='edit'),
                params=valid_params,
                expect_errors=True
            )

            assert_that(response.status_code, is_(200), "status code for page '%s'" % invalid_key)
            assert_that(response.normal_body, contains_string(invalid_error), "In '%s'" % invalid_key)

    def test_GIVEN_invalid_region_data_WHEN_create_new_THEN_error(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        invalid_values = ["region-0.name", "region-0.category", "region-0.path"]

        for invalid_key in invalid_values:

            valid_params = self.create_valid_post_values()
            valid_params["mask_count"] = 1
            valid_params["region-0.name"] = "a value"
            valid_params["region-0.category"] = "a value"
            valid_params["region-0.path"] = "a value"
            valid_params["region-0.id"] = ""
            valid_params[invalid_key] = ""


            response = self.app.post(
                url=url(controller='driving_data', action='edit'),
                params=valid_params,
                expect_errors=True
            )

            assert_that(response.status_code, is_(200), "status code for page '%s'" % invalid_key)
            assert_that(response.normal_body, contains_string("Please correct"), "error message for '%s'" % invalid_key)

    def test_GIVEN_valid_data_with_masks_WHEN_create_new_THEN_masks_are_created(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        valid_params = self.create_valid_post_values()
        valid_params["mask_count"] = 1
        valid_params["region-0.id"] = ""
        valid_params["region-0.name"] = "name0"
        valid_params["region-0.category"] = "category0"
        valid_params["region-0.path"] = "path0"

        response = self.app.post(
            url=url(controller='driving_data', action='edit'),
            params=valid_params,
            expect_errors=True
        )

        assert_that(response.status_code, is_(302), "no redirect after successful post got %s" % response.normal_body)

        with session_scope() as session:
            driving_dataset_id = session\
                .query(DrivingDataset)\
                .filter(DrivingDataset.name == self.new_driving_dataset.name)\
                .one().id
            regions = LandCoverService().get_land_cover_regions(driving_dataset_id)

        assert_that(len(regions), is_(1), "number of regions")
        assert_that(regions[0].name, is_(valid_params["region-0.name"]), "name of region")
        assert_that(regions[0].category.name, is_(valid_params["region-0.category"]), "category of region")
        assert_that(regions[0].mask_file, is_(valid_params["region-0.path"]), "path of region")

    def test_GIVEN_invalid_extra_parameter_data_WHEN_create_new_THEN_error(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        valid_params = self.create_valid_post_values()
        valid_params["params_count"] = 1
        valid_params["param-0.id"] = "23"
        valid_params["param-0.value"] = ""

        response = self.app.post(
            url=url(controller='driving_data', action='edit'),
            params=valid_params,
            expect_errors=True
        )

        assert_that(response.status_code, is_(200), "status code for page")
        assert_that(response.normal_body, contains_string("Please correct"), "error message for ")

    def test_GIVEN_valid_data_with_extra_parameters_WHEN_create_new_THEN_extra_parameters_are_created(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        valid_params = self.create_valid_post_values()
        valid_params["params_count"] = 1
        parameter_id = 23
        valid_params["param-0.id"] = str(parameter_id)
        valid_params["param-0.value"] = "value"

        response = self.app.post(
            url=url(controller='driving_data', action='edit'),
            params=valid_params,
            expect_errors=True
        )

        assert_that(response.status_code, is_(302), "no redirect after successful post got %s" % response.normal_body)

        with session_scope(Session) as session:
            driving_dataset_id = session\
                .query(DrivingDataset)\
                .filter(DrivingDataset.name == self.new_driving_dataset.name)\
                .one().id
            driving_dataset = DatasetService().get_driving_dataset_by_id(driving_dataset_id)

        value = [parameter_value for parameter_value in driving_dataset.parameter_values if parameter_value.parameter_id == parameter_id]
        assert_that(len(value), is_(1), "number of parameter values")
        assert_that(value[0].value, is_(valid_params["param-0.value"]), "parameter value")

    def test_GIVEN_valid_data_with_extra_parameters_where_one_has_been_deleted_WHEN_create_new_THEN_error(self):

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        valid_params = self.create_valid_post_values()
        count = int(valid_params["params_count"]) + 2
        valid_params["params_count"] = count
        parameter_id = 23
        valid_params["param-{}.id".format(count)] = str(parameter_id)
        valid_params["param-{}.value".format(count)] = ""

        response = self.app.post(
            url=url(controller='driving_data', action='edit'),
            params=valid_params,
            expect_errors=True
        )

        assert_that(response.status_code, is_(200), "status code for page")

    def test_GIVEN_valid_data_with_extra_parameters_WHEN_update_THEN_parameters_are_updated(self):

        with session_scope(Session) as session:
            original_count = session\
                .query(DrivingDataset).count()

            parameter_value = DrivingDatasetParameterValue(ModelRunService(), self.driving_dataset, 23, "old value")
            param_id_to_delete = 1
            parameter_value = DrivingDatasetParameterValue(ModelRunService(), self.driving_dataset, param_id_to_delete,
                                                           "to be deleted")

        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        valid_params = self.create_valid_post_values()
        valid_params["params_count"] = 1
        parameter_id = 23
        valid_params["param-0.id"] = str(parameter_id)
        valid_params["param-0.value"] = "expected extra parameter value"

        valid_params["mask_count"] = 1
        valid_params["region-0.name"] = "a value"
        valid_params["region-0.category"] = "a value"
        valid_params["region-0.path"] = "a value"
        valid_params["region-0.id"] = ""

        expected_nvars = len(self.drive_var) + 1
        last_index = len(self.drive_var) + 4
        valid_params["drive_nvars"] = last_index + 1
        valid_params["drive_var_-{}.vars".format(last_index)] = 'blah'
        valid_params["drive_var_-{}.names".format(last_index)] = 'blah'
        valid_params["drive_var_-{}.templates".format(last_index)] = 'blah'
        valid_params["drive_var_-{}.interps".format(last_index)] = 'blah'

        response = self.app.post(
            url=url(controller='driving_data', action='edit', id=str(self.driving_dataset.id)),
            params=valid_params,
            expect_errors=True
        )

        assert_that(response.status_code, is_(302), "status code for page")

        with session_scope(Session) as session:
            final_count = session\
                .query(DrivingDataset).count()

        assert_that(final_count, is_(original_count), "number of driving datasets (before and after update)")

        with session_scope(Session) as session:
            driving_dataset = DatasetService().get_driving_dataset_by_id(self.driving_dataset.id)
        regions = LandCoverService().get_land_cover_regions(self.driving_dataset.id)

        assert_that(driving_dataset.name, is_(self.new_driving_dataset.name), "name has changed")
        value = [parameter_value for parameter_value in driving_dataset.parameter_values if parameter_value.parameter_id == parameter_id]
        assert_that(len(value), is_(1), "number of parameter values")
        assert_that(value[0].value, is_(valid_params["param-0.value"]), "parameter value")


        assert_that(driving_dataset.get_python_parameter_value(constants.JULES_PARAM_DRIVE_NVARS), is_(expected_nvars), "nvars")

        for parameter_value in driving_dataset.parameter_values:
            if parameter_value.parameter_id == param_id_to_delete:
                self.fail("Parameter should have been deleted but wasn't")


        assert_that(len(regions), is_(1), "number of regions")
        assert_that(regions[0].name, is_(valid_params["region-0.name"]), "name of region")
        assert_that(regions[0].category.name, is_(valid_params["region-0.category"]), "category of region")
        assert_that(regions[0].mask_file, is_(valid_params["region-0.path"]), "path of region")

        assert_that(len(driving_dataset.locations), is_(expected_nvars + 2), 'driving dataset locations (+ 2 ancils)l')