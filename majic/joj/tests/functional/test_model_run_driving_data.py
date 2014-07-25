"""
#header
"""
from urlparse import urlparse
from hamcrest import assert_that, contains_string, is_
from pylons import url
from joj.tests import TestController
from joj.services.dataset import DatasetService
from joj.services.model_run_service import ModelRunService
from joj.utils import constants


class TestModelRunDrivingData(TestController):
    def setUp(self):
        super(TestModelRunDrivingData, self).setUp()
        self.clean_database()
        self.user = self.login()
        self.sample_file_contents = "# solar   long  rain  snow    temp   wind     press      humid\n" \
                                    "# sw_down   lw_down  tot_rain  tot_snow    t   wind     pstar      q\n" \
                                    "# i   i  i  i    i   i     i      i\n" \
                                    "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n" \
                                    "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n" \
                                    "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n" \
                                    "# ----- data for later times ----"

    def upload_valid_user_driving_data(self):
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        return self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Upload',
                'lat': u'55',
                'lon': u'45',
                'dt_start': u'2000-01-01 00:00',
                'dt_end': u'2000-01-01 02:00'},
            upload_files=[('driving-file', 'file.txt', self.sample_file_contents)]
        )

    def check_valid_user_driving_data_params_stored(self):
        model_run_service = ModelRunService()
        model_run = model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        data_start = model_run.get_parameter_values(constants.JULES_PARAM_DRIVE_DATA_START)[0].value
        data_end = model_run.get_parameter_values(constants.JULES_PARAM_DRIVE_DATA_END)[0].value
        data_period = model_run.get_parameter_values(constants.JULES_PARAM_DRIVE_DATA_PERIOD)[0].value
        file = model_run.get_parameter_values(constants.JULES_PARAM_DRIVE_FILE)[0].value
        nvars = model_run.get_parameter_values(constants.JULES_PARAM_DRIVE_NVARS)[0].value
        var = model_run.get_parameter_values(constants.JULES_PARAM_DRIVE_VAR)[0].value
        interp = model_run.get_parameter_values(constants.JULES_PARAM_DRIVE_INTERP)[0].value
        assert_that(model_run.driving_data_lat, is_(55))
        assert_that(model_run.driving_data_lon, is_(45))
        assert_that(data_start, is_("'2000-01-01 00:00:00'"))
        assert_that(data_end, is_("'2000-01-01 02:00:00'"))
        assert_that(data_period, is_("3600"))
        assert_that(file, is_("'" + constants.USER_UPLOAD_FILE_NAME + "'"))
        assert_that(nvars, is_("8"))
        assert_that(var, is_("'sw_down', 'lw_down', 'tot_rain', 'tot_snow', 't', 'wind', 'pstar', 'q'"))
        assert_that(interp, is_("'i', 'i', 'i', 'i', 'i', 'i', 'i', 'i'"))

    def _add_model_run_being_created(self):
        model_run_service = ModelRunService()
        model_run_service.update_model_run(self.user, "test", 1)

    def test_GIVEN_no_model_being_created_WHEN_page_get_THEN_redirect_to_create_model_run(self):
        response = self.app.get(
            url(controller='model_run', action='driving_data'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_two_driving_datasets_WHEN_get_THEN_select_driving_data_page_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        response = self.app.get(
            url(controller='model_run', action='driving_data'))
        assert_that(response.normal_body, contains_string("Select Driving Data"))
        self.assert_model_run_creation_action(self.user, 'driving_data')

    def test_GIVEN_two_driving_datasets_WHEN_get_THEN_driving_datasets_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        response = self.app.get(
            url(controller='model_run', action='driving_data'))
        assert_that(response.normal_body, contains_string("driving1"))
        assert_that(response.normal_body, contains_string("driving2"))

    def test_GIVEN_driving_dataset_for_user_upload_WHEN_get_THEN_driving_dataset_rendered(self):
        self._add_model_run_being_created()

        response = self.app.get(
            url(controller='model_run', action='driving_data'))
        assert_that(response.normal_body, contains_string(constants.USER_UPLOAD_DRIVING_DATASET_NAME))

    def test_GIVEN_invalid_driving_data_chosen_WHEN_post_THEN_error_returned(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': -100,
                'submit': u'Next'
            })

        assert_that(response.normal_body, contains_string("Driving data not recognised"))

    def test_GIVEN_valid_driving_data_chosen_WHEN_post_THEN_next_page_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next'
            })

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='extents')), "url")

    def test_GIVEN_user_quota_exceeded_WHEN_navigate_post_to_driving_data_THEN_navigate_to_error_page(self):
        """
        On a post of data the quota should not be checked, the data should just be saved as normal
        """
        user = self.login()
        self.create_run_model(storage_in_mb=user.storage_quota_in_gb * 1024 + 1, name="big_run", user=user)

        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next'
            })

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='index')), "url")

    def test_GIVEN_valid_driving_data_chosen_WHEN_go_back_THEN_create_page_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Back'
            })

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_valid_driving_data_chosen_WHEN_post_THEN_driving_data_stored_against_model_run(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next'
            })

        model_run_service = ModelRunService()
        model_run = model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        param_val = model_run.get_python_parameter_value(constants.JULES_PARAM_DRIVE_FILE)
        assert_that(param_val, is_('testFileName'))

    def test_GIVEN_user_driving_data_but_invalid_dates_WHEN_upload_data_THEN_errors_returned(self):
        self._add_model_run_being_created()
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Upload',
                'lat': u'45',
                'lon': u'55',
                'dt_start': u'2017-02-02 11:00',
                'dt_end': u'this-is-not-a-date'},
            upload_files=[('driving-file', 'file.txt', self.sample_file_contents)]
        )
        assert_that(response.normal_body, contains_string('Please enter a date in the format YYYY-MM-DD HH:MM'))

    def test_GIVEN_user_driving_data_but_invalid_lat_lon_WHEN_upload_data_THEN_errors_returned(self):
        self._add_model_run_being_created()
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Upload',
                'lat': u'1800',
                'lon': u'-181',
                'dt_start': u'2011-02-02 11:00',
                'dt_end': u'2017-02-02 11:00'},
            upload_files=[('driving-file', 'file.txt', self.sample_file_contents)]
        )
        assert_that(response.normal_body, contains_string('Latitude must be between -90 and 90'))
        assert_that(response.normal_body, contains_string('Longitude must be between -180 and 180'))

    def test_GIVEN_no_user_driving_data_uploaded_WHEN_upload_THEN_errors_shown(self):
        self._add_model_run_being_created()
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Upload',
                'lat': u'1800',
                'lon': u'-181',
                'dt_start': u'2011-02-02 11:00',
                'dt_end': u'2017-02-02 11:00',
                'driving-file': u''
            })
        assert_that(response.normal_body, contains_string('You must select a driving data file'))

    def test_GIVEN_valid_user_driving_data_WHEN_upload_data_THEN_data_stored_against_model_run(self):
        self._add_model_run_being_created()
        self.upload_valid_user_driving_data()
        self.check_valid_user_driving_data_params_stored()

    def test_GIVEN_user_driving_data_previously_selected_WHEN_get_THEN_user_driving_data_rendered(self):
        self._add_model_run_being_created()
        self.upload_valid_user_driving_data()
        response = self.app.get(
            url(controller='model_run', action='driving_data'))
        assert_that(response.normal_body, contains_string('55'))
        assert_that(response.normal_body, contains_string('45'))
        assert_that(response.normal_body, contains_string('2000-01-01 00:00'))
        assert_that(response.normal_body, contains_string('2000-01-01 02:00'))
        assert_that(response.normal_body, contains_string('3 rows of driving data successfully uploaded'))

    def test_GIVEN_valid_user_driving_data_selected_WHEN_page_submit_THEN_proceeds_to_next_page(self):
        self._add_model_run_being_created()
        self.upload_valid_user_driving_data()
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next',
                'lat': u'55',
                'lon': u'45',
                'dt_start': u'2000-01-01 00:00',
                'dt_end': u'2000-01-01 03:00'},
            upload_files=[('driving-file', 'file.txt', self.sample_file_contents)]
        )
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='extents')), "url")

    def test_GIVEN_user_driving_data_previously_selected_then_changed_on_page_WHEN_page_submit_THEN_data_not_changed(
            self):
        # This is understood to be the correct action - unless the 'upload' button is clicked, the user
        # driving data does not get processed.
        self._add_model_run_being_created()
        self.upload_valid_user_driving_data()

        self.app.get(
            url(controller='model_run', action='driving_data'))
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next',
                'lat': u'12',
                'lon': u'17',
                'dt_start': u'1990-01-01 00:00',
                'dt_end': u'1990-01-01 03:00'},
            upload_files=[('driving-file', 'file2.txt', self.sample_file_contents)]
        )
        self.check_valid_user_driving_data_params_stored()

    def test_GIVEN_user_uploaded_driving_data_previously_WHEN_page_submit_THEN_moved_to_next_page(self):
        # 1. User visits driving data page and chooses 'upload'
        # 2. They upload their data
        # 3. They click submit (the driving data is now stored).
        # 4. They return to the driving data page and submit again without changing anything
        # This is acceptable, they should be moved on. In fact no database saves need to occur.
        self._add_model_run_being_created()

        self.upload_valid_user_driving_data()
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next',
                'lat': u'1800',
                'lon': u'-181',
                'dt_start': u'2011-02-02 11:00',
                'dt_end': u'2017-02-02 11:00',
                'driving-file': u''
            })
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='extents')), "url")

    def test_GIVEN_upload_dataset_chosen_but_no_uploaded_dataset_WHEN_page_submit_THEN_error_shown(self):
        # 1. User visits driving data page
        # 2. User chooses upload data but doesn't actually upload anything
        # 3. User clicks submit
        # This is bad and an error should appear
        self._add_model_run_being_created()
        data_service = DatasetService()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next',
                'lat': u'1800',
                'lon': u'-181',
                'dt_start': u'2011-02-02 11:00',
                'dt_end': u'2017-02-02 11:00',
                'driving-file': u''
            })
        assert_that(response.normal_body, contains_string('You must upload a driving data file'))
