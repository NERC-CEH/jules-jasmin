"""
# header
"""
from joj.model.meta import Session, Base

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
from joj.model.dataset_type import DatasetType
from joj.model.dataset import Dataset
from joj.model.ecomaps_models import *
from joj.model.driving_dataset_location import DrivingDatasetLocation
from joj.model.driving_dataset import DrivingDataset
from joj.model.driving_dataset_parameter_value import DrivingDatasetParameterValue
from joj.model.system_alert_email import SystemAlertEmail
from joj.model.land_cover_region import LandCoverRegion
from joj.model.land_cover_region_type import LandCoverRegionType
from joj.model.land_cover_region_action import LandCoverRegionAction


def initialise_session(config, manual_connection_string=None):
    """
    Sets up our database engine and session

    :param config: The config object containing 'sqlalchemy.blah' items
    :param manual_connection_string: An alternate connection string
    :return:nothing
    """

    # Attach our engine to the session, either from the config file or
    # using a supplied string
    if manual_connection_string:
        engine = create_engine(manual_connection_string)
    else:
        engine = engine_from_config(config, 'sqlalchemy.')

    Session.configure(bind=engine)


@contextmanager
def session_scope(session_class=Session):
    """
    Provide a transactional scope that we can wrap around calls to the database
    use like with session_scope() as session
    :param session_class: session class to create a session from
    :return: nothing
    """

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
