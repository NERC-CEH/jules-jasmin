from sqlalchemy import engine_from_config, Column, Integer, String, ForeignKey, Table, DateTime, create_engine, Text, Boolean, \
    ForeignKeyConstraint, BigInteger
from sqlalchemy.orm import relationship
from joj.model.meta import Session, Base
from contextlib import contextmanager
#import all the database models in so they can be built

from joj.model.account_request import AccountRequest
from joj.model.model_run_status import ModelRunStatus
from joj.model.model_file import ModelFile
from joj.model.model_run import ModelRun
from joj.model.code_version import CodeVersion
from joj.model.namelist_file import NamelistFile
from joj.model.namelist import Namelist
from joj.model.parameter import Parameter
from joj.model.parameter_value import ParameterValue
from joj.model.user import User
from joj.model.user_level import UserLevel
from joj.model.ecomaps_models import *

def initialise_session(config, manual_connection_string=None):
    """Sets up our database engine and session
    Params
        In: config - The config object containing 'sqlalchemy.blah' items"""

    # Attach our engine to the session, either from the config file or
    # using a supplied string
    if manual_connection_string:
        engine = create_engine(manual_connection_string)
    else:
        engine = engine_from_config(config, 'sqlalchemy.')

    Session.configure(bind=engine)

@contextmanager
def session_scope(session_class=Session):
    """Provide a transactional scope that we can wrap around calls to the database"""

    session = session_class()

    try:
        # Give this session back to the 'with' block
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
