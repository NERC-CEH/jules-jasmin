"""
# Header
"""

from joj.model.meta import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.utils import constants


class Namelist(Base):
    """A fortran namelist in which a parameters for Jules appears
    """

    __tablename__ = 'namelists'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    namelist_file_id = Column(Integer, ForeignKey('namelist_files.id'))
    index_in_file = Column(Integer)

    namelist_file = relationship("NamelistFile", backref=backref('namelists', order_by=id))
    parameters = relationship("Parameter", backref=backref('namelist', order_by=id))

    def __repr__(self):
        """String representation"""

        return "<Namelist(name=%s)>" % self.name
