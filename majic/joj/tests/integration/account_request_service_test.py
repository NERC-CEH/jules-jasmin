# header
from hamcrest import *
from mock import Mock
from pylons import config
from joj.crowd.client import CrowdClient, ClientException
from joj.crowd.crowd_client_factory import CrowdClientFactory
from joj.tests import TestController
from joj.services.account_request_service import AccountRequestService
from joj.model.account_request import AccountRequest
from joj.model import session_scope, Session, User
from joj.services.email_service import EmailService
from joj.services.user import UserService


class AccountRequestServiceTest(TestController):

    def setUp(self):
        super(AccountRequestServiceTest, self).setUp()
        self.email_service = Mock(EmailService)
        self.crowd_client = Mock(CrowdClient)
        crowd_client_factory = CrowdClientFactory()
        crowd_client_factory.get_client = Mock(return_value=self.crowd_client)
        self.account_request_service = AccountRequestService(
            email_service=self.email_service,
            crowd_client_factory=crowd_client_factory)
        self.clean_database()

    def test_WHEN_account_request_submitted_THEN_account_request_ends_in_database(self):
        account_request = AccountRequest()
        account_request.first_name = "test first Name"
        account_request.last_name = "test last Name"
        account_request.email = "email@domain.com"
        account_request.institution = "CEH"
        account_request.usage = "usage text"

        self.account_request_service.add_account_request_with_email(account_request)

        with session_scope(Session) as session:
            account_requests = session.query(AccountRequest).all()
        assert_that(len(account_requests), is_(1))
        assert_that(account_requests[0].first_name, is_(account_request.first_name))

    def test_GIVEN_account_request_database_full_WHEN_account_request_submitted_THEN_account_request_not_added(self):
        with session_scope(Session) as session:
            for i in range(0, int(config['max_request_accounts'])):
                account_request = AccountRequest()
                account_request.name = "name"
                account_request.email = "email@domain.com"
                account_request.institution = "CEH"
                account_request.usage = "usage text"
                session.add(account_request)
        account_request = AccountRequest()
        account_request.name = "testName"
        account_request.email = "email@domain.com"
        account_request.institution = "CEH"
        account_request.usage = "usage text"

        self.account_request_service.add_account_request_with_email(account_request)

        with session_scope(Session) as session:
            account_requests_in_database = session.query(AccountRequest).count()
        assert_that(account_requests_in_database, is_(int(config['max_request_accounts'])))

    def test_GIVEN_account_request_WHEN_reject_THEN_request_deleted_email_sent(self):
        request_id = self.create_account_request()

        self.account_request_service.reject_account_request(request_id, "a fairly long reason")

        with session_scope() as session:
            assert_that(session.query(AccountRequest).filter(AccountRequest.id == request_id).count(), is_(0), "Request has been deleted")
            assert_that(session.query(User).count(), is_(1), "Only one user core in the users table")
        assert_that(self.email_service.send_email.called, is_(True), "Rejection email sent")

    def test_GIVEN_account_request_WHEN_accept_THEN_request_deleted_and_email_sent_and_crowd_account_created_and_user_created(self):
        request_id = self.create_account_request()

        self.account_request_service.accept_account_request(request_id)

        with session_scope() as session:
            assert_that(session.query(AccountRequest).filter(AccountRequest.id == request_id).count(), is_(0), "Request has been deleted")
            assert_that(session.query(User).count(), is_(2), "Total user count (should be core and new user)")
            user = session.query(User).filter(User.username == self.account_request.email).one()
            assert_that(user.forgotten_password_uuid, is_not(None), "forgotten password uuid set")
            assert_that(user.forgotten_password_expiry_date, is_not(None), "forgotten password expiry date set")

        assert_that(self.crowd_client.create_user.called, is_(True), "User was created in crowd")
        assert_that(self.email_service.send_email.called, is_(True), "Acceptance email sent")
        assert_that(self.email_service.send_email.call_args[0][3], contains_string(str(user.id)), "user id in link")
        assert_that(self.email_service.send_email.call_args[0][3], is_not(contains_string('t//')), "user id in link")


    def test_GIVEN_account_request_for_existing_account_WHEN_accept_THEN_request_deleted_and_email_sent_and_notcreate_crowd_account_and_set_forgotten_password_for_user(self):
        request_id = self.create_account_request()
        self.login(username=self.account_request.email)


        self.account_request_service.accept_account_request(request_id)

        with session_scope() as session:
            assert_that(session.query(AccountRequest).filter(AccountRequest.id == request_id).count(), is_(0), "Request has been deleted")
            assert_that(session.query(User).count(), is_(2), "Total user count (should be core and new user)")
            user = session.query(User).filter(User.username == self.account_request.email).one()
            assert_that(user.forgotten_password_uuid, is_not(None), "forgotten password uuid set")
            assert_that(user.forgotten_password_expiry_date, is_not(None), "forgotten password expiry date set")

        assert_that(self.crowd_client.create_user.called, is_(False), "User was not created in crowd")
        assert_that(self.email_service.send_email.called, is_(True), "Acceptance email sent")

    def test_GIVEN_account_request_WHEN_accept_and_exception_thrown_in_client_THEN_request_not_deleted_and_email_not_sent_and_user_account_not_created(self):
        request_id = self.create_account_request()
        self.crowd_client.create_user = Mock(side_effect=ClientException())

        with self.assertRaises(ClientException, msg="Should have thrown a ClientException exception"):
            self.account_request_service.accept_account_request(request_id)

        with session_scope() as session:
            assert_that(session.query(AccountRequest).filter(AccountRequest.id == request_id).count(), is_(1), "Request has not been deleted")
            assert_that(session.query(User).count(), is_(1), "Total user count (should be core)")

        assert_that(self.email_service.send_email.called, is_(False), "Acceptance email sent")
