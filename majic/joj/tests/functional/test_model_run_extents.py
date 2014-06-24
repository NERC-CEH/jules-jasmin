#header
from urlparse import urlparse
from hamcrest import assert_that, is_
from pylons import url
from tests import TestController


class TestModelRunExtents(TestController):

    def setUp(self):
        super(TestModelRunExtents, self).setUp()
        self.clean_database()
        self.user = self.login()

    def test_GIVEN_no_model_being_created_WHEN_page_get_THEN_redirect_to_choose_driving_data(self):
        response = self.app.get(
            url(controller='model_run', action='extents'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='driving_data')), "url")

    def test_GIVEN_nothing_WHEN_page_get_THEN_extents_page_rendered(self):
        pass

    def test_GIVEN_driving_data_extents_WHEN_page_get_THEN_driving_data_extents_rendered(self):
        pass

    def test_GIVEN_extents_already_chosen_WHEN_page_get_THEN_existing_extents_rendered(self):
        pass
