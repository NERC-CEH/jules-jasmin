# Header


from joj.model.meta import Base

from sqlalchemy import Column, Integer, String
from joj.utils import constants


class NamelistFile(Base):
    """A file which contains fortran namelist
    """

    __tablename__ = 'namelist_files'

    id = Column(Integer, primary_key=True)
    filename = Column(String(constants.DB_STRING_SIZE))

    def __repr__(self):
        """String representation"""

        return "<NamelistFile(filename=%s)>" % self.filename
