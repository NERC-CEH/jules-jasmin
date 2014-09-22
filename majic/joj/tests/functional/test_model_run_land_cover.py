"""
header
"""
from urlparse import urlparse
from hamcrest import is_, assert_that, contains_string, is_not, string_contains_in_order
from pylons import url
from joj.services.model_run_service import ModelRunService
from joj.tests import TestController
from joj.model import session_scope, LandCoverRegionCategory, ModelRun, LandCoverRegion, LandCoverAction, \
    DrivingDataset, Session, ParameterValue
from joj.services.dataset import DatasetService
from joj.services.land_cover_service import LandCoverService
from joj.utils.constants import *
# noinspection PyProtectedMember


class TestModelRunLandCover(TestController):
    def setUp(self):
        self.clean_database()
        self.user = self.login()
        self.create_two_driving_datasets()
        dds = DatasetService().get_driving_datasets(self.user)[0]
        with session_scope() as session:
            model_run = ModelRun()
            model_run.name = "model run"
            model_run.change_status(session, MODEL_RUN_STATUS_CREATED)
            model_run.user = self.user
            model_run.driving_dataset_id = dds.id
            session.add(model_run)
            session.commit()

            self.model_run_service = ModelRunService()
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)

            parameter_val = ParameterValue()
            parameter_val.parameter = self.model_run_service.get_parameter_by_constant(JULES_PARAM_LATLON_REGION)
            parameter_val.set_value_from_python(True)
            parameter_val.model_run_id = model_run.id
            session.add(parameter_val)

        self.add_land_cover_region(model_run)

    def test_GIVEN_land_cover_actions_WHEN_post_THEN_land_cover_action_saved_in_database(self):
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
            dds = model_run.driving_dataset
        categories = LandCoverService().get_land_cover_categories(dds.id)
        # Need to know the region IDs
        self.app.post(
            url(controller='model_run', action='land_cover'),
            params={
                'submit': u'Next',
                'action_1_region': str(categories[0].regions[0].id),
                'action_1_value': u'8',
                'action_1_order': u'1',
                'action_2_region': str(categories[0].regions[0].id),
                'action_2_value': u'7',
                'action_2_order': u'2'
            })
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)

        actions = model_run.land_cover_actions
        assert_that(len(actions), is_(2))
        for action in actions:
            if action.value_id == 8:
                assert_that(action.order, is_(1))
            elif action.value_id == 7:
                assert_that(action.order, is_(2))
            else:
                assert False

    def test_GIVEN_invalid_land_cover_actions_WHEN_post_THEN_error_shown_and_stay_on_page(self):
        # Add some regions to another driving dataset
        dds = DatasetService().get_driving_datasets(self.user)[1]
        with session_scope() as session:
            land_cat = LandCoverRegionCategory()
            land_cat.driving_dataset = dds
            land_cat.name = "Category2"

            land_region = LandCoverRegion()
            land_region.name = "Region1"
            land_region.category = land_cat
            session.add(land_region)

        response = self.app.post(
            url(controller='model_run', action='land_cover'),
            params={
                'submit': u'Next',
                'action_1_region': str(land_region.id),
                'action_1_value': u'8',
                'action_1_order': u'1'
            })
        assert_that(response.normal_body, contains_string("Land Cover"))  # Check still on page
        assert_that(response.normal_body, contains_string("Land Cover Region not valid for the chosen driving data"))

    def test_GIVEN_land_cover_values_and_regions_exist_WHEN_get_THEN_regions_and_categories_rendered(self):
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
            dds = model_run.driving_dataset
            session.add_all(self.generate_categories_with_regions(dds))

        response = self.app.get(url(controller='model_run', action='land_cover'))

        assert_that(response.normal_body, contains_string("Rivers"))
        assert_that(response.normal_body, contains_string("Thames"))
        assert_that(response.normal_body, contains_string("Itchen"))
        assert_that(response.normal_body, contains_string("Counties"))
        assert_that(response.normal_body, contains_string("Hampshire"))
        assert_that(response.normal_body, contains_string("Oxfordshire"))

    def test_GIVEN_nothing_WHEN_get_THEN_values_rendered(self):
        response = self.app.get(url(controller='model_run', action='land_cover'))

        values = LandCoverService().get_land_cover_values(None, return_ice=False)
        for value in values:
            assert_that(response.normal_body, contains_string(str(value.name)))

    def test_GIVEN_land_cover_action_already_saved_WHEN_get_THEN_action_rendered(self):
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
            dds = model_run.driving_dataset
            session.add_all(self.generate_categories_with_regions(dds))

            action = LandCoverAction()
            action.model_run = model_run
            action.region_id = 1  # Thames
            action.value_id = 5  # Shrub

        response = self.app.get(url(controller='model_run', action='land_cover'))
        assert_that(response.normal_body, contains_string("Change <b>Thames (Rivers)</b> to <b>Shrub</b>"))

    def test_GIVEN_invalid_land_cover_actions_already_saved_WHEN_get_THEN_errors_returned_no_actions_rendered(self):
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
            dds = model_run.driving_dataset
            session.add_all(self.generate_categories_with_regions(dds))

            action = LandCoverAction()
            action.model_run = model_run
            action.region_id = 1  # Thames
            action.value_id = 9  # Ice
            session.add(action)
            session.commit()

            # Set the model run to have a different driving dataset - this should result in an error
            model_run.driving_dataset = session.query(DrivingDataset).filter(DrivingDataset.name == "driving2").one()

        response = self.app.get(url(controller='model_run', action='land_cover'))
        assert_that(response.normal_body, contains_string("Your saved Land Cover edits are not valid for the "
                                                          "chosen driving data"))
        assert_that(response.normal_body, is_not(contains_string("Change <b>")))  # Actions start with this

    def test_GIVEN_multiple_land_cover_actions_saved_out_of_order_WHEN_get_THEN_order_rendered_correctly(self):
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
            dds = model_run.driving_dataset
            session.add_all(self.generate_categories_with_regions(dds))

            action = LandCoverAction()
            action.model_run = model_run
            action.region_id = 1  # Thames
            action.value_id = 5  # Shrub
            action.order = 5
            session.add(action)
            session.commit()

            action2 = LandCoverAction()
            action2.model_run = model_run
            action2.region_id = 2  # Itchen
            action2.value_id = 1  # Broad-leaved Tree
            action2.order = 1
            session.add(action2)
            session.commit()

            action3 = LandCoverAction()
            action3.model_run = model_run
            action3.region_id = 3  # Hampshire
            action3.value_id = 6  # Urban
            action3.order = 2
            session.add(action3)
            session.commit()

        response = self.app.get(url(controller='model_run', action='land_cover'))
        order1 = response.normal_body.index("Change <b>Itchen (Rivers)</b> to <b>Broad-leaved Tree</b>")
        order2 = response.normal_body.index("Change <b>Hampshire (Counties)</b> to <b>Urban</b>")
        order5 = response.normal_body.index("Change <b>Thames (Rivers)</b> to <b>Shrub</b>")
        assert (order1 < order2 < order5)

    def generate_categories_with_regions(self, driving_dataset):
        # Add categories
        cat1 = LandCoverRegionCategory()
        cat1.driving_dataset_id = driving_dataset.id
        cat1.name = "Rivers"
        cat1.id = 1

        region1 = LandCoverRegion()
        region1.id = 1
        region1.name = "Thames"
        region1.category_id = 1
        region1.category = cat1

        region2 = LandCoverRegion()
        region2.id = 2
        region2.name = "Itchen"
        region2.category_id = 1
        region2.category = cat1

        cat1.regions = [region1, region2]

        cat2 = LandCoverRegionCategory()
        cat2.driving_dataset_id = driving_dataset.id
        cat2.name = "Counties"
        cat2.id = 2

        region3 = LandCoverRegion()
        region3.id = 3
        region3.name = "Hampshire"
        region3.category_id = 2
        region3.category = cat2

        region4 = LandCoverRegion()
        region4.id = 4
        region4.name = "Oxfordshire"
        region4.category_id = 2
        region4.category = cat2

        cat2.regions = [region3, region4]

        return [cat1, cat2]


class TestModelRunLandCoverSingleCell(TestController):
    def setUp(self):
        self.model_run_service = ModelRunService()
        self.land_cover_service = LandCoverService()

    def set_up_single_cell_model_run(self):
        self.clean_database()
        self.user = self.login()
        self.create_two_driving_datasets()
        user_upload_id = DatasetService().get_id_for_user_upload_driving_dataset()
        with session_scope(Session) as session:
            self.model_run = ModelRun()
            self.model_run.name = "MR1"
            self.model_run.status = self._status(MODEL_RUN_STATUS_CREATED)
            self.model_run.driving_dataset_id = user_upload_id
            self.model_run.user = self.user
            self.model_run.driving_data_lat = 51.75
            self.model_run.driving_data_lon = -0.25
            self.model_run.driving_data_rows = 248

            param1 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_INTERP)
            pv1 = ParameterValue()
            pv1.parameter_id = param1.id
            pv1.set_value_from_python(8 * ['nf'])

            param2 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_DATA_PERIOD)
            pv2 = ParameterValue()
            pv2.parameter_id = param2.id
            pv2.set_value_from_python(60 * 60)

            param3 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_DATA_START)
            pv3 = ParameterValue()
            pv3.parameter_id = param3.id
            pv3.value = "'1901-01-01 00:00:00'"

            param4 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_DATA_END)
            pv4 = ParameterValue()
            pv4.parameter_id = param4.id
            pv4.value = "'1901-01-31 21:00:00'"

            param5 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_LATLON_REGION)
            pv5 = ParameterValue()
            pv5.parameter_id = param5.id
            pv5.value = ".false."

            param6 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_POINTS_FILE)
            pv6 = ParameterValue()
            pv6.parameter_id = param6.id
            pv6.value = "51.75 -0.25"

            self.model_run.parameter_values = [pv1, pv2, pv3, pv4, pv5, pv6]
            session.add(self.model_run)

    def test_GIVEN_single_cell_run_WHEN_page_get_THEN_fractional_cover_page_shown(self):
        self.set_up_single_cell_model_run()
        response = self.app.get(url(controller='model_run', action='land_cover'))
        assert_that(response.normal_body, contains_string("Fractional Land Cover"))

    def test_GIVEN_land_cover_values_WHEN_page_get_THEN_land_cover_type_names_rendered(self):
        self.set_up_single_cell_model_run()
        response = self.app.get(url(controller='model_run', action='land_cover'))
        lc_vals = self.land_cover_service.get_land_cover_values(None)
        del lc_vals[-1]  # Remove the ice
        names = [str(val.name) for val in lc_vals]
        assert_that(response.normal_body, string_contains_in_order(*names))

    def test_GIVEN_available_driving_datasets_WHEN_page_get_THEN_default_fractional_cover_rendered(self):
        self.set_up_single_cell_model_run()
        response = self.app.get(url(controller='model_run', action='land_cover'))
        lc_vals = self.land_cover_service.get_land_cover_values(None)
        del lc_vals[-1]  # Remove the ice
        string_names_values = []
        for val in lc_vals:
            string_names_values.append(str(val.name))
            string_names_values.append('12.5')
        assert_that(response.normal_body, string_contains_in_order(*string_names_values))

    def test_GIVEN_saved_land_cover_frac_WHEN_page_get_THEN_saved_values_rendered(self):
        self.set_up_single_cell_model_run()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        frac_string = "0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.72 0.0"
        self.land_cover_service.save_fractional_land_cover_for_model(model_run, frac_string)

        response = self.app.get(url(controller='model_run', action='land_cover'))

        lc_vals = self.land_cover_service.get_land_cover_values(None)
        del lc_vals[-1]  # Remove the ice

        string_names_values = []
        for i in range(len(lc_vals)):
            string_names_values.append(str(lc_vals[i].name))
            string_names_values.append(str(100 * float(frac_string.split()[i])))
        assert_that(response.normal_body, string_contains_in_order(*string_names_values))

    def test_GIVEN_saved_land_cover_with_too_few_types_WHEN_page_get_THEN_available_values_rendered(self):
        self.set_up_single_cell_model_run()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        frac_string = "0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.72"
        self.land_cover_service.save_fractional_land_cover_for_model(model_run, frac_string)

        response = self.app.get(url(controller='model_run', action='land_cover'))

        lc_vals = self.land_cover_service.get_land_cover_values(None)
        del lc_vals[-1]  # Remove the ice

        string_names_values = []
        for i in range(len(lc_vals)):
            string_names_values.append(str(lc_vals[i].name))
            string_names_values.append(str(100 * float(frac_string.split()[i])))
        assert_that(response.normal_body, string_contains_in_order(*string_names_values))

    def test_GIVEN_saved_land_cover_with_too_many_types_WHEN_page_get_THEN_some_values_rendered(self):
        self.set_up_single_cell_model_run()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        frac_string = "0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.72 0.0 0.0"
        self.land_cover_service.save_fractional_land_cover_for_model(model_run, frac_string)

        response = self.app.get(url(controller='model_run', action='land_cover'))

        lc_vals = self.land_cover_service.get_land_cover_values(None)
        del lc_vals[-1]  # Remove the ice

        string_names_values = []
        for i in range(len(lc_vals)):
            string_names_values.append(str(lc_vals[i].name))
            string_names_values.append(str(100 * float(frac_string.split()[i])))
        assert_that(response.normal_body, string_contains_in_order(*string_names_values))

    def test_GIVEN_valid_fractional_cover_WHEN_post_THEN_values_saved(self):
        self.set_up_single_cell_model_run()
        self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'submit': u'Next',
                    'fractional_cover': u'1',
                    'land_cover_value_1': u'20',
                    'land_cover_value_2': u'25',
                    'land_cover_value_3': u'5',
                    'land_cover_value_4': u'10',
                    'land_cover_value_5': u'10',
                    'land_cover_value_6': u'5',
                    'land_cover_value_7': u'10',
                    'land_cover_value_8': u'15'})
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        assert_that(model_run.land_cover_frac, is_("0.2\t0.25\t0.05\t0.1\t0.1\t0.05\t0.1\t0.15\t0"))

    def test_GIVEN_valid_fractional_cover_WHEN_post_THEN_default_soil_props_saved(self):
        self.set_up_single_cell_model_run()
        self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'submit': u'Next',
                    'fractional_cover': u'1',
                    'land_cover_value_1': u'20',
                    'land_cover_value_2': u'25',
                    'land_cover_value_3': u'5',
                    'land_cover_value_4': u'10',
                    'land_cover_value_5': u'10',
                    'land_cover_value_6': u'5',
                    'land_cover_value_7': u'10',
                    'land_cover_value_8': u'15'})
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        soil_props = model_run.get_python_parameter_value(JULES_PARAM_SOIL_PROPS_CONST_VAL, is_list=True)
        assert_that(soil_props, is_([0.9, 0.0, 0.0, 50.0, 275.0, 300.0, 10.0, 0.0, 0.5]))

    def test_GIVEN_ice_fractional_cover_WHEN_post_THEN_values_saved(self):
        self.set_up_single_cell_model_run()
        self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'submit': u'Next',
                    'fractional_cover': u'1',
                    'land_cover_ice': u'1'})
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        assert_that(model_run.land_cover_frac, is_("0\t0\t0\t0\t0\t0\t0\t0\t1"))

    def test_GIVEN_valid_fractional_cover_WHEN_post_THEN_moved_to_next_page(self):
        self.set_up_single_cell_model_run()
        response = self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'submit': u'Next',
                    'fractional_cover': u'1',
                    'land_cover_value_1': u'20',
                    'land_cover_value_2': u'25',
                    'land_cover_value_3': u'5',
                    'land_cover_value_4': u'10',
                    'land_cover_value_5': u'10',
                    'land_cover_value_6': u'5',
                    'land_cover_value_7': u'10',
                    'land_cover_value_8': u'15'})
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='output')), "url")

    def test_GIVEN_fractional_cover_saved_WHEN_reset_THEN_cover_reset(self):
        self.set_up_single_cell_model_run()
        self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'submit': u'Next',
                    'fractional_cover': u'1',
                    'land_cover_value_1': u'20',
                    'land_cover_value_2': u'25',
                    'land_cover_value_3': u'5',
                    'land_cover_value_4': u'10',
                    'land_cover_value_5': u'10',
                    'land_cover_value_6': u'5',
                    'land_cover_value_7': u'10',
                    'land_cover_value_8': u'15'})
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        initial_cover = model_run.land_cover_frac
        assert initial_cover is not None
        response = self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'reset_fractional_cover': u'1'})
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='land_cover')), "url")
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        final_cover = model_run.land_cover_frac
        assert_that(final_cover, is_(None))

    def test_GIVEN_values_dont_add_up_WHEN_post_THEN_errors_returned_and_values_not_saved(self):
        self.set_up_single_cell_model_run()
        response = self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'submit': u'Next',
                    'fractional_cover': u'1',
                    'land_cover_value_1': u'40',
                    'land_cover_value_2': u'25',
                    'land_cover_value_3': u'5',
                    'land_cover_value_4': u'10',
                    'land_cover_value_5': u'10',
                    'land_cover_value_6': u'5',
                    'land_cover_value_7': u'10',
                    'land_cover_value_8': u'15'})
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        assert_that(model_run.land_cover_frac, is_(None))
        assert_that(response.normal_body, contains_string("The sum of all the land cover fractions must be 100%"))
        assert_that(response.normal_body, contains_string("Fractional Land Cover"))

    def test_GIVEN_values_dont_add_up_WHEN_post_THEN_values_still_present_on_page(self):
        self.set_up_single_cell_model_run()
        response = self.app.post(
            url(controller='model_run', action='land_cover'),
            params={'submit': u'Next',
                    'fractional_cover': u'1',
                    'land_cover_value_1': u'40',
                    'land_cover_value_2': u'25',
                    'land_cover_value_3': u'5',
                    'land_cover_value_4': u'10',
                    'land_cover_value_5': u'10',
                    'land_cover_value_6': u'5',
                    'land_cover_value_7': u'10',
                    'land_cover_value_8': u'15'})

        lc_vals = self.land_cover_service.get_land_cover_values(None)
        del lc_vals[-1]  # Remove the ice
        frac_vals = ['40', '25', '5', '10', '10', '5', '10', '15']
        string_names_values = []
        for i in range(len(lc_vals)):
            string_names_values.append(str(lc_vals[i].name))
            string_names_values.append(str(frac_vals[i]))
        assert_that(response.normal_body, string_contains_in_order(*string_names_values))

    def test_GIVEN_no_extents_selected_WHEN_page_get_THEN_redirect(self):
        self.set_up_single_cell_model_run()
        param = self.model_run_service.get_parameter_by_constant(JULES_PARAM_POINTS_FILE)
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        with session_scope() as session:
            session.query(ParameterValue) \
                .filter(ParameterValue.parameter_id == param.id) \
                .filter(ParameterValue.model_run_id == model_run.id) \
                .delete()

        response = self.app.get(url(controller='model_run', action='land_cover'))
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='extents')), "url")
