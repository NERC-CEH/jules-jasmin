"""
header
"""
from sqlalchemy import Column, Integer, String, Boolean
from joj.model import Base
from joj.utils import constants


class OutputVariable(Base):
    """
    JULES Output variable
    """

    __tablename__ = 'output_variables'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))
    depends_on_nsmax = Column(Boolean, default=False)

    def __repr__(self):
        """String representation"""

        return "<Parameter(name=%s)>" % self.name