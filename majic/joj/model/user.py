"""
# Header
"""

from joj.model.meta import Base
from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from joj.utils import constants


class User(Base):
    """A user of the system"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(constants.DB_STRING_SIZE))
    email = Column(String(constants.DB_LONG_STRING_SIZE))
    name = Column(String(constants.DB_STRING_SIZE))
    access_level = Column(String(constants.DB_STRING_SIZE))
    first_name = Column(String(constants.DB_STRING_SIZE))
    last_name = Column(String(constants.DB_STRING_SIZE))
    institution = Column(String(constants.DB_STRING_SIZE))
    storage_quota_in_gb = Column(BigInteger)
    model_run_creation_action = Column(String(constants.DB_STRING_SIZE))
    forgotten_password_uuid = Column(String(constants.DB_STRING_SIZE))
    forgotten_password_expiry_date = Column(DateTime)

    def is_admin(self):
        """
        Checks to see if the user is an admin
        :return: True if the current user is an admin, false otherwise
        """
        return self.access_level == constants.USER_ACCESS_LEVEL_ADMIN

    def __repr__(self):
        """String representation of the user"""

        return "<User(username=%s, name=%s)>" % (self.username, self.name)
