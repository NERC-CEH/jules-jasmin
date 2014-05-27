# Header

from hamcrest import *
from joj.tests import *
from model import User
from joj.model import Session
from services.general import DatabaseService
from services.user import UserService


class TestModelRunController(TestController):


    def test_GIVEN_nothing_WHEN_navigate_to_create_run_THEN_create_run_page_shown(self):

        username = 'test'
        user_service = UserService()
        user = user_service.get_user_by_username(username)
        if user is None:
            user = user_service.create(username,'test', 'testerson', 'test@ceh.ac.uk', '')

        response = self.app.get(
            url(controller='model_run', action='create'),
            extra_environ={'REMOTE_USER': str(user.username)})
        assert_that(response.normal_body, contains_string("Create Model Run"))
