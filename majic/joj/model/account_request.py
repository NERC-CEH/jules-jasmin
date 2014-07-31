"""
# header
"""
from sqlalchemy import Column, Integer, String
from joj.model import Base
from joj.utils import constants


class AccountRequest(Base):
    """A request for a system account"""

    __tablename__ = 'account_request'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(constants.DB_STRING_SIZE))
    last_name = Column(String(constants.DB_STRING_SIZE))
    email = Column(String(constants.DB_STRING_SIZE))
    institution = Column(String(constants.DB_STRING_SIZE))
    usage = Column(String(constants.DB_LONG_STRING_SIZE))

    def __repr__(self):
        """String representation of the account request"""
        return "<AccountRequest(name=%s %s, email=%s)>" % (self.first_name, self.last_name, self.email)