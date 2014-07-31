"""
# header
"""
from pylons import config
import logging
from joj.model import AccountRequest, Session
from joj.services.general import DatabaseService
from joj.services.email_service import EmailService
from joj.utils import email_messages
from joj.services.user import UserService
from joj.utils import constants

log = logging.getLogger(__name__)


class AccountRequestService(DatabaseService):
    """
    Service for persistence and retrieval of AccountRequests
    """

    def __init__(self, session=Session, email_service=EmailService(), user_service=UserService()):
        """

        :param session: session to use
        :param email_service: the email service to use
        :return:nothing
        """
        super(AccountRequestService, self).__init__(session)
        self._email_service = email_service
        self._user_service = user_service

    def _add_account_request(self, account_request):
        """
        Adds an account request to the database
        :param account_request: Account request to add to database
        :return: void
        """
        with self.transaction_scope() as session:
            session.add(account_request)

    def add_account_request_with_email(self, account_request):
        """
        Adds an account request to the database and emails the admin
        informing them of a new request.
        Also emails the user confirming their account request.
        :param account_request: Account request to add to database
        :return: void
        """

        if self._is_database_full():
            # Email the person who requested the account
            msg = email_messages.ACCOUNT_REQUEST_FULL % account_request.first_name
            self._email_service.send_email(config['email.from_address'], account_request.email,
                                           "Unable to process account request", msg)
            return

        self._add_account_request(account_request)
        # Email the person who requested the account
        msg = email_messages.ACCOUNT_REQUESTED_USER % account_request.first_name
        self._email_service.send_email(
            config['email.from_address'],
            account_request.email,
            "Majic Account Requested",
            msg)

        # Then email the admin to approve
        msg = email_messages.ACCOUNT_REQUESTED_ADMIN % (
            account_request.first_name,
            account_request.last_name,
            account_request.email,
            account_request.institution,
            account_request.usage)
        self._email_service.send_email(
            config['email.from_address'],
            config['email.admin_address'],
            "Majic Account Requested",
            msg)

    def _is_database_full(self):
        """
        Check if the number of account requests in the database has reached a preset limit
        :return: True if database has reached limit, False otherwise
        """
        with self.readonly_scope() as session:
            account_requests_in_database = session.query(AccountRequest).count()
        return account_requests_in_database >= int(config['max_request_accounts'])

    def get_account_requests(self):
        """
        Get all the account requests
        :return: account requests
        """
        with self.readonly_scope() as session:
            return session.query(AccountRequest).all()

    def reject_account_request(self, id, reason):
        """
        Reject the account request
        :param reason: reason for account rejection
        :param id: id of account request to reject
        :return:nothing
        """

        with self.transaction_scope() as session:
            account_request = session.\
                query(AccountRequest)\
                .filter(AccountRequest.id == id)\
                .one()

            msg = email_messages.ACCOUNT_REQUEST_REJECTED_MESSAGE.format(
                first_name=account_request.first_name,
                last_name=account_request.last_name,
                reason=reason
            )
            self._email_service.send_email(
                config['email.from_address'],
                account_request.email,
                email_messages.ACCOUNT_REQUEST_REJECTED_SUBJECT,
                msg)

            session.delete(account_request)

    def accept_account_request(self, id):
        with self.transaction_scope() as session:
            account_request = session.\
                query(AccountRequest)\
                .filter(AccountRequest.id == id)\
                .one()

            self._user_service.create(
                account_request.email,
                account_request.first_name,
                account_request.last_name,
                account_request.email,
                constants.USER_ACCESS_LEVEL_EXTERNAL,
                account_request.institution)

            #msg = email_messages.ACCOUNT_REQUEST_ACCEPTED_MESSAGE.format(
            #    name=account_request.name,
            #    reason=reason
            #)
            #self._email_service.send_email(
            #    config['email.from_address'],
            #    account_request.email,
            #    email_messages.ACCOUNT_REQUEST_REJECTED_SUBJECT,
            #    msg)

            session.delete(account_request)