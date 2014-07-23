"""
# Header
"""
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from joj.utils import constants
from joj.model import session_scope, Session, ModelRun


class TestModelRunCatalogue(TestController):

    def setUp(self):
        super(TestModelRunCatalogue, self).setUp()

    def test_GIVEN_non_existant_model_run_WHEN_delete_THEN_nothing_happens_redirect_to_index(self):

        user = self.login()

        response = self.app.post(
            url(controller='model_run', action='delete', id='-900'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")

    def test_GIVEN_non_integer_id_WHEN_delete_THEN_nothing_happens_redirect_to_index(self):

        user = self.login()

        response = self.app.post(
            url(controller='model_run', action='delete', id='nan'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")


    def test_GIVEN_get_WHEN_delete_THEN_nothing_happens_redirect_to_index(self):

        user = self.login()
        model = self.create_run_model(0, "test", user)

        response = self.app.get(
            url(controller='model_run', action='delete', id=str(model.id)))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")

    def test_GIVEN_model_that_does_not_belong_to_you_and_not_admin_WHEN_delete_THEN_nothing_happens_redirect_to_index(self):

        user = self.login('users_model')
        logged_in_user = self.login()
        model = self.create_run_model(0, "test", user)

        response = self.app.post(
            url(controller='model_run', action='delete', id=str(model.id)))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")
        with session_scope(Session) as session:
            count = session.query(ModelRun).filter(ModelRun.id == model.id).count()

        assert_that(count, is_(1), 'Model should exist')

    def test_GIVEN_model_that_does_belongs_non_admin_user_and_is_published_WHEN_delete_THEN_model_published_exception(self):

        user = self.login('')
        model = self.create_run_model(0, "test", user, constants.MODEL_RUN_STATUS_PUBLISHED)

        response = self.app.post(
            url(controller='model_run', action='delete', id=str(model.id)),
            params={})

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")
        with session_scope(Session) as session:
            count = session.query(ModelRun).filter(ModelRun.id == model.id).count()

        assert_that(count, is_(1), 'Count(Model)')

