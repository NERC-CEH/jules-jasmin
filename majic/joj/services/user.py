"""
# header
"""
import logging
from pylons import config
from sqlalchemy.orm.exc import NoResultFound
from joj.model import User
from joj.services.general import DatabaseService, ServiceException
from joj.utils import constants

log = logging.getLogger(__name__)


class UserService(DatabaseService):
    """Provides operations on User objects"""

    def create(self, username, first_name, last_name, email, access_level):
        """
        Creates a user (if the user doesn't already exist)

        :param username: The login name of the user
        :param first_name: User's first name
        :param last_name: User's last name
        :param email: User's email address
        :param access_level: Set to 'Admin' for administrative functions
        :return: nothing
        """

        with self.transaction_scope() as session:

            user = User()
            user.username = username
            user.name = " ".join([first_name, last_name])
            user.email = email
            user.access_level = access_level
            user.first_name = first_name
            user.last_name = last_name
            if user.access_level == constants.USER_ACCESS_LEVEL_ADMIN:
                user.storage_quota_in_gb = config['storage_quota_admin_GB']
            else:
                user.storage_quota_in_gb = config['storage_quota_user_GB']

            session.add(user)

    def get_user_by_username(self, username):
        """
        Gets a single user by their username
        :param username: Login name of the user to retrieve
        :return: user object or None if there is no match
        """

        with self.readonly_scope() as session:

            try:
                return session.query(User).filter(User.username == username).one()

            except NoResultFound as e:
                # We'll get an exception if the user can't be found

                log.error("No user found: %s", e)
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
