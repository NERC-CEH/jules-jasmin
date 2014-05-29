# header
import logging
from sqlalchemy.orm.exc import NoResultFound
from joj.services.general import DatabaseService, ServiceException
from joj.model import ModelRun

log = logging.getLogger(__name__)


class ModelRunService(DatabaseService):
    """Encapsulates operations on the Run Models"""


    def get_models_for_user(self, user):
        """
        Get all the run models a user can view

        Arguments:
        user -- the user trying to access the data

        returns:
        a list of model runs the user can see
        """
        with self.readonly_scope() as session:
            try:
                return session.query(ModelRun).filter(ModelRun.user_id == user.id).all()
            except NoResultFound as e:
                return []
            except Exception as ex:
                # A general error has occurred - pass this up
                raise ServiceException(ex)

    def get_model_being_created(self, user):
        """
        The user can have a single model run they are creating
        This function returns it if it exists

        Arguments:
        user -- the user

        Returns:
        a model run model that the user will submit
        """
        pass