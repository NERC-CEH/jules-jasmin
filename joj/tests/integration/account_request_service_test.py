# header
from hamcrest import *
from pylons import config
from joj.tests import TestController
from joj.services.account_request_service import AccountRequestService
from joj.model.account_request import AccountRequest
from joj.model import session_scope, Session


class AccountRequestServiceTest(TestController):

    def setUp(self):
        super(AccountRequestServiceTest, self).setUp()
        self.account_request_service = AccountRequestService()
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
        account_request.name = "new request"
        account_request.email = "email@domain.com"
        account_request.institution = "CEH"
        account_request.usage = "usage text"
        self.account_request_service.add_account_request_with_email(account_request)
        with session_scope(Session) as session:
            account_requests_in_database = session.query(AccountRequest).count()
        assert_that(account_requests_in_database, is_(int(config['max_request_accounts'])))





