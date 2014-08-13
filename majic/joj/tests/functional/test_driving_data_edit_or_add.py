"""
# header
"""
from hamcrest import *
from joj.tests import *
from joj.utils import constants, utils
from joj.model import session_scope


class TestDrivingDataEditOrAdd(TestController):

    def setUp(self):
        super(TestDrivingDataEditOrAdd, self).setUp()
        self.clean_database()
        with session_scope() as session:
            self.driving_dataset = self.create_driving_dataset(session)

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

        assert_that(response.normal_body, contains_string(self.driving_dataset.name))

