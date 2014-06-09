# Header


from joj.model.meta import Base

from sqlalchemy import Column, Integer, String, ForeignKey
from joj.utils import constants

class ParameterValue(Base):
    """A parameter value for a model run
    This is the definition of a parameter which is NOT the default value
    """

    __tablename__ = 'parameter_values'

    id = Column(Integer, primary_key=True)
    value = Column(String(constants.DB_PARAMETER_VALUE_STRING_SIZE))

    model_run_id = Column(Integer, ForeignKey('model_runs.id'))
    parameter_id = Column(Integer, ForeignKey('parameters.id'))

    def __repr__(self):
        """String representation"""

        return "<ParameterValue(value=%s)>" % self.value

