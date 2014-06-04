# Header


from joj.model.meta import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, ForeignKey, Table, SmallInteger, Boolean
from joj.utils import constants

# table for many to many association between code and parameters
_parameter_code_version_association_table = \
    Table(
        'parameter_code_version_association',
        Base.metadata,
        Column('parameter', Integer, ForeignKey('parameters.id')),
        Column('code_version', SmallInteger, ForeignKey('code_versions.id'))
    )

class Parameter(Base):
    """A parameter for the Jules model
    This is the definition of a single parameter which the user may set for a given versions of the code
    """

    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))

    default_value = Column(String(constants.DB_PARAMETER_VALUE_STRING_SIZE))
    type = Column(String(constants.DB_STRING_SIZE))
    required = Column(Boolean())
    min = Column(Integer)
    max = Column(Integer)

    #The url suffix to add to the url from the code version
    url_suffix = Column(String(constants.DB_LONG_STRING_SIZE))

    user_level_id = Column(Integer, ForeignKey('user_levels.id'))
    namelist_id = Column(Integer, ForeignKey('namelists.id'))

    parameter_values = relationship("ParameterValue", backref=backref('parameter', order_by=id))

    code_versions = relationship("CodeVersion", secondary=_parameter_code_version_association_table, backref="parameters")

    def __repr__(self):
        """String representation"""

        return "<Parameter(name=%s)>" % self.name


# class PossibleValues(Base):
#         """A possible value for a parameter for the Jules model. The value must be constrained to one of these values
#         This is includes filenames which are restricted by the admin
#         """
#
#         __tablename__ = 'parameter'
#
#         #this is the value as it will end up in the final files
#         value =
#
#         #this is the display value as it is shown
#         display_value =
#
#         parameter = relationship("Parameter", backref=backref('possible_values', order_by=id))
#
#         possibleValues = Column(Integer, ForeignKey('possible_value.id'), nullable=True)