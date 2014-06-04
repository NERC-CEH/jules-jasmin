# header
import logging
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound
from joj.services.general import DatabaseService, ServiceException
from joj.model import ModelRun, CodeVersion, ModelRunStatus, Parameter, ParameterValue
from joj.utils import constants

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
            except NoResultFound:
                return []

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

    def get_code_versions(self):
        """
        Get the list of code versions the user can select from

        Returns:
        list of code versions
        """

        with self.readonly_scope() as session:
            return session.query(CodeVersion).all()

    def get_code_version_by_id(self, code_version_id):
        """
        Gets the code version object based on the id of the code version

        Arguments:
        code_version_id -- id for the code version

        Returns:
        the code version model or throws Invalid
        """

        with self.readonly_scope() as session:
            return session.query(CodeVersion).filter(CodeVersion.id == code_version_id).one()

    def update_model_run(self, name, code_version_id):
        """
        Update the creation model run definition

        Arguments:
        name -- name of the model run
        code_version_id -- the id of the code version
        """
        with self.transaction_scope() as session:

            try:
                model_run = session.query(ModelRun)\
                    .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATING)\
                    .one()
            except NoResultFound:
                model_run = ModelRun()
                model_status = session\
                    .query(ModelRunStatus)\
                    .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATING)\
                    .one()
                model_run.status = model_status

            model_run.name = name
            code_version = session.query(CodeVersion).filter(CodeVersion.id == code_version_id).one()
            model_run.code_version = code_version
            session.add(model_run)

    def get_model_run_being_created_or_default(self):
        """
        Get the run being created or a default model if no run is being created

        Returns:
        Model run being created or a new Model
        """
        try:
            with self.readonly_scope() as session:
                return session.query(ModelRun)\
                    .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATING).one()
        except NoResultFound:
            return ModelRun()

    def get_defining_model_with_parameters(self):
        """
        Get the parameters for the model being create

        Return:
        a list of populated parameters, populated with parameter values
        """
        with self.readonly_scope() as session:
            code_version = session.query(CodeVersion)\
                .join(ModelRun)\
                .join(ModelRunStatus)\
                .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATING).one()

            return session.query(Parameter)\
                .options(subqueryload(Parameter.parameter_values))\
                .filter(Parameter.code_versions.contains(code_version))



