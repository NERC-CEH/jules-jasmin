# header
from pylons import config
from joj.model import AccountRequest
from joj.services.general import DatabaseService
from joj.utils.emailer import send_email


class AccountRequestService(DatabaseService):
    """
    Service for persistence and retrieval of AccountRequests
    """

    MESSAGE_TEMPLATE_REQUESTED = "Dear %s,\r\n\r\n" \
                                 "Your request for a Majic account has been passed on to the Majic admin team. " \
                                 "Once it has been approved you will receive an email letting you know that an " \
                                 "account has been created for you," \
                                 "\r\n\r\nThanks for registering your interest with Majic!"

    MESSAGE_TEMPLATE_ADMIN = "Dear Majic admin,\r\n\r\nThe following request for a Majic " \
                             "account has been received:\r\n\r\n" \
                             "Name: %s\r\n" \
                             "Email: %s\r\n" \
                             "Institution: %s\r\n" \
                             "Expected usage: %s\r\n\r\n" \
                             "Please login to Majic and review this user request"

    MESSAGE_TEMPLATE_FULL = "Dear %s,\r\n\r\n" \
                            "Unfortunately we are unable to accept any more account requests for today. We're " \
                            "sorry for the inconvenience, please try again tomorrow."

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
            msg = self.MESSAGE_TEMPLATE_FULL % account_request.name
            send_email(config['email.from_address'], account_request.email,
                       "Unable to process account request", msg)
            return

        self._add_account_request(account_request)
        # Email the person who requested the account
        msg = self.MESSAGE_TEMPLATE_REQUESTED % account_request.name
        send_email(config['email.from_address'], account_request.email, "Majic Account Requested", msg)

        # Then email the admin to approve
        msg = self.MESSAGE_TEMPLATE_ADMIN % (account_request.name, account_request.email,
                                             account_request.institution,
                                             account_request.usage)
        send_email(config['email.from_address'], config['email.admin_address'], "Majic Account Requested", msg)


    def _is_database_full(self):
        """
        Check if the number of account requests in the database has reached a preset limit
        :return: True if database has reached limit, False otherwise
        """
        with self.transaction_scope() as session:
            account_requests_in_database = session.query(AccountRequest).count()
        return account_requests_in_database >= int(config['max_request_accounts'])