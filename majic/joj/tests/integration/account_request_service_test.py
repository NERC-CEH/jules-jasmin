# header
from hamcrest import *
from mock import Mock
from pylons import config
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
        self.account_request_service = AccountRequestService(email_service=self.email_service)
        self.clean_database()

    def test_WHEN_account_request_submitted_THEN_account_request_ends_in_database(self):
        account_request = AccountRequest()
        account_request.name = "testName"
        account_request.email = "email@domain.com"
        account_request.institution = "CEH"
        account_request.usage = "usage text"

        self.account_request_service.add_account_request_with_email(account_request)

        with session_scope(Session) as session:
            account_requests = session.query(AccountRequest).all()
        assert_that(len(account_requests), is_(1))
        assert_that(account_requests[0].name, is_("testName"))

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



