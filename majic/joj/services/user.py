"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import logging
import datetime
from pylons import config, url
from sqlalchemy.orm.exc import NoResultFound
from joj.crowd.client import ClientException
from joj.crowd.crowd_client_factory import CrowdClientFactory
from joj.model import User, Session
from joj.services.general import DatabaseService, ServiceException
from joj.utils import constants
import uuid
from joj.services.email_service import EmailService
from joj.utils import email_messages

log = logging.getLogger(__name__)


class UserService(DatabaseService):
    """Provides operations on User objects"""

    def __init__(self, session=Session, email_service=EmailService(), crowd_client_factory=CrowdClientFactory()):
        super(UserService, self).__init__(session)
        self._email_service = email_service
        self._crowd_client_factory = crowd_client_factory

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
        user.username = username.strip()
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
        """ Returns the user with the specified ID or None if they don't exist

            :param id: ID of the user to get
            :return; user or none if they don't exist
        """

        with self.readonly_scope() as session:
            return session.query(User).get(id)

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

            user = session.query(User).filter(User.id == user_id).one()

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
        return config['serverurl'].rstrip('/') \
            + url(controller="home", action="password", id=user.id, uuid=user.forgotten_password_uuid)

    def set_forgot_password(self, user_id, send_email=False):
        """
        Set that the user has forgotten their password
        :param user_id: the id of the user who forgot their password
        :param send_email: send an email to the user for password reset
        :return:link to reset their password
        """
        with self.transaction_scope() as session:
            user = session.query(User).filter(User.id == user_id).one()
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

    def reset_password(self, user_id, password_one, password_two):
        """
        Reset a users password. Passwords must be the same and longer than the minimum length
        :param user_id: user id
        :param password_one: password, first entry
        :param password_two: password, second entry
        :return:nothing throws Service Exception on error
        """

        if password_one != password_two:
            raise ServiceException("passwords are not the same.")
        password = password_one
        if len(password) < constants.PASSWORD_MINIMUM_LENGTH:
            raise ServiceException("password must be at least %s characters long." % constants.PASSWORD_MINIMUM_LENGTH)

        try:
            with self.transaction_scope() as session:
                user = session.query(User).filter(User.id == user_id).one()
                crowd_client = self._crowd_client_factory.get_client()
                crowd_client.update_users_password(user.username, password)
                user.forgotten_password_expiry_date = None
                user.forgotten_password_uuid = None
        except NoResultFound:
            raise ServiceException("user not found.")
        except ClientException as ex:
            log.exception("On password reset problem with crowd")
            raise ServiceException("there is a problem with the crowd service: %s"
                                   % ex.message)
