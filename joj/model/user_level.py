# Header

from joj.model.meta import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref
from joj.utils import constants


class UserLevel(Base):
    """Level of experience list of values
    """
    __tablename__ = "user_levels"

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))

    parameters = relationship("Parameter", backref=backref('user_level', order_by=id))

    def __repr__(self):
        """String representation"""

        return "<UserLevel(name=%s)>" % self.name
