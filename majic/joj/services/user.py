"""
# header
"""
import logging
import datetime
from pylons import config, url
from sqlalchemy.orm.exc import NoResultFound
from joj.model import User, Session
from joj.services.general import DatabaseService, ServiceException
from joj.utils import constants
import uuid
from joj.services.email_service import EmailService
from joj.utils import email_messages

log = logging.getLogger(__name__)


class UserService(DatabaseService):
    """Provides operations on User objects"""

    def __init__(self, session=Session, email_service=EmailService()):
        super(UserService, self).__init__(session)
        self._email_service = email_service

    def create_in_session(self, session, username, first_name, last_name, email, access_level, institution=""):
        """
        Creates a user within a session

        :param session: session to use
        :param username: The login name of the user
        :param first_name: User's first name
        :param last_name: User's last name
        :param email: User's email address
        :param access_level: Set to 'Admin' for administrative functions
        :param institution: users institution may be blank
        :return: nothing
        """

        user = User()
        user.username = username
        user.name = " ".join([first_name, last_name])
        user.email = email
        user.access_level = access_level
        user.first_name = first_name
        user.last_name = last_name
        user.institution = institution
        if user.access_level == constants.USER_ACCESS_LEVEL_ADMIN:
            user.storage_quota_in_gb = config['storage_quota_admin_GB']
        else:
            user.storage_quota_in_gb = config['storage_quota_user_GB']
        session.add(user)
        return user

    def create(self, username, first_name, last_name, email, access_level, institution=""):
        """
        Creates a user

        :param username: The login name of the user
        :param first_name: User's first name
        :param last_name: User's last name
        :param email: User's email address
        :param access_level: Set to 'Admin' for administrative functions
        :param institution: users institution may be blank
        :return: nothing
        """

        with self.transaction_scope() as session:
            self.create_in_session(session, username, first_name, last_name, email, access_level, institution)

    def get_user_by_username(self, username):
        """
        Gets a single user by their username
        :param username: Login name of the user to retrieve
        :return: user object or None if there is no match or username was None
        """
        if username is None:
            return None

        with self.readonly_scope() as session:
            return self.get_user_by_username_in_session(session, username)

    def get_user_by_username_in_session(self, session, username):
        """
        Get a user from their user name, or none if the user doesn't exist
        :param session: session to use
        :param username: username
        :return:user
        """
        try:
            return session.query(User).filter(User.username == username).one()
        except NoResultFound as e:
            # We'll get an exception if the user can't be found
            log.info("No user found: %s", e)
            return None
        except Exception as ex:
            # A general error has occurred - pass this up
            raise ServiceException(ex)

    def get_user_by_email_address(self, email):
        """ Returns a user with the given email (which should be unique)

            @param email: email address to filter on
        """

        with self.readonly_scope() as session:

            try:
                return session.query(User).filter(User.email == email).one()

            except:
                # We'll get an exception if the user can't be found
                return None

    def get_user_by_id(self, id):
        """ Simply returns the user with the specified ID

            @param id: ID of the user to get
        """

        with self.readonly_scope() as session:

            try:
                return session.query(User).get(id)
            except:
                return None

    def get_all_users(self):
        """
        Returns an array containing all the users
        """

        with self.readonly_scope() as session:

            return session\
                .query(User)\
                .order_by(User.email)\
                .all()

    def update(self, first_name, last_name, email, access_level, user_id, storage_quota):
        """ Updates the user specified by the ID passed in

            :param first_name: New friendly name for the user
            :param last_name: User's surname
            :param email: New email address
            :param access_level: New access level
            :param user_id: ID of the user to update
            :param storage_quota: the new storage quota for the user
        """
        with self.transaction_scope() as session:

            user = session.query(User).get(user_id)

            user.first_name = first_name
            user.last_name = last_name
            user.name = " ".join([first_name, last_name])
            user.email = email
            user.access_level = access_level
            user.storage_quota_in_gb = storage_quota

            session.add(user)

    def set_current_model_run_creation_action(self, user, action):
        """
        Set the current action for the user when created a model run
        :param user: the user to change the action on
        :param action: the model run action
        :return: nothing
        """
        with self.transaction_scope() as session:
            user = session.merge(user)
            user.model_run_creation_action = action

    def set_forgot_password_in_session(self, user):
        """
        Set that the user has forgotten their password in a session
        :param user: the user who forgot their password
        :return:link to reset their password
        """

        user.forgotten_password_uuid = str(uuid.uuid4().get_hex())
        expiry_time = datetime.datetime.now() + datetime.timedelta(hours=constants.FORGOTTEN_PASSWORD_UUID_VALID_TIME)
        user.forgotten_password_expiry_date = expiry_time
        return url(controller="home", action="password_reset", id=user.id, uuid=user.forgotten_password_uuid)

    def set_forgot_password(self, user_id, send_email=False):
        """
        Set that the user has forgotten their password
        :param user_id: the id of the user who forgot their password
        :param send_email: send an email to the user for password reset
        :return:link to reset their password
        """
        with self.transaction_scope() as session:
            user = session.query(User).get(user_id)
            link = self.set_forgot_password_in_session(user)
            if send_email:
                msg = email_messages.PASSWORD_RESET_MESSAGE.format(
                    name=user.name,
                    link=link
                )
                self._email_service.send_email(
                    config['email.from_address'],
                    user.email,
                    email_messages.PASSWORD_RESET_SUBJECT,
                    msg)
            return link