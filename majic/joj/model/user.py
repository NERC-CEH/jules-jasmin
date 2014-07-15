"""
# Header
"""

from joj.model.meta import Base
from sqlalchemy import Column, Integer, String, BigInteger
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
    storage_quota_in_gb = Column(BigInteger)

    def __repr__(self):
        """String representation of the user"""

        return "<User(username=%s, name=%s)>" % (self.username, self.name)
