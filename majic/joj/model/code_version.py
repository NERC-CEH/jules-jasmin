# Header


from joj.model.meta import Base
from sqlalchemy import Column, String, SmallInteger, Boolean
from joj.utils import constants


class CodeVersion(Base):
    """The version of the Jules code to be run
    """

    __tablename__ = 'code_versions'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    is_default = Column(Boolean)
    url_base = Column(String(constants.DB_URL_STRING_SIZE))

    def __repr__(self):
        """String representation of the code version"""

        return "<CodeVersion(name=%s)>" % self.name
