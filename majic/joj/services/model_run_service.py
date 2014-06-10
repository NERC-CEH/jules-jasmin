# header
import logging
from sqlalchemy.orm import subqueryload, contains_eager
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_, desc, asc
from joj.services.general import DatabaseService
from joj.model import ModelRun, CodeVersion, ModelRunStatus, Parameter, ParameterValue
from joj.utils import constants
from joj.services.general import DatabaseService, ServiceException
from joj.model import ModelRun, CodeVersion, ModelRunStatus
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
                return session.query(ModelRun).filter(ModelRun.user_id == user.id)\
                    .order_by(desc(ModelRun.date_created)).all()
            except NoResultFound:
                return []

    def get_published_models(self):
        """
        Get all the published model runs
        :return: A list of published model runs
        """
        with self.readonly_scope() as session:
            try:
                return session.query(ModelRun).join(ModelRun.status)\
                    .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_PUBLISHED)\
                    .order_by(desc(ModelRun.date_created)).all()
            except NoResultFound:
                return []

    def get_model_by_id(self, user, id):
         with self.readonly_scope() as session:
            return session.query(ModelRun).filter(ModelRun.id == id).first()

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
                model_run = self._get_model_run_being_created(session)
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
                return self._get_model_run_being_created(session)
        except NoResultFound:
            return ModelRun()

    def get_parameters_for_model_being_created(self):
        """
        Get the parameters for the model being created

        Return:
        a list of populated parameters, populated with parameter values
        """
        with self.readonly_scope() as session:
            return self._get_parameters_for_creating_model(session)

    def store_parameter_values(self, parameters_to_set):
        """
        Store the parameter values inb the database
        :param parameters_to_set: dictionary of parameter ids and parameter values
        :return: Nothing
        """

        with self.transaction_scope() as session:
            model_run = self._get_model_run_being_created(session)
            session.query(ParameterValue)\
                .filter(ParameterValue.model_run == model_run)\
                .delete()
            parameters = self._get_parameters_for_creating_model(session)
            for parameter in parameters:
                parameter_value = parameters_to_set[str(parameter.id)]
                if parameter_value is not None:
                    val = ParameterValue()
                    val.value = parameter_value
                    val.parameter = parameter
                    val.model_run = model_run
                    session.add(val)

    def get_model_being_created_with_non_default_parameter_values(self):
        """
        Get the current model run being created including all parameter_value which are not defaults
        :return:model tun with parameters populated
        """
        with self.readonly_scope() as session:
            return session.query(ModelRun) \
                .join(ModelRun.status) \
                .outerjoin(ModelRun.parameter_values, "parameter", "namelist") \
                .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATING)\
                .options(subqueryload(ModelRun.code_version)) \
                .options(contains_eager(ModelRun.parameter_values)
                            .contains_eager(ParameterValue.parameter)
                            .contains_eager(Parameter.namelist)) \
                .one()

    def submit_model_run(self):
        """
        Submit the model run which is being created to be run
        :return:new status of the job
        """
        with self.transaction_scope() as session:
            model = self._get_model_run_being_created(session)
            status = session \
                .query(ModelRunStatus) \
                .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_SUBMIT_FAILED) \
                .one()
            model.status = status
            return status

    def _get_parameters_for_creating_model(self, session):
        """
        get parameters for the model run being created
        :param session: session to use
        :return: a list of parameters
        """
        code_version, model_run = session.query(CodeVersion, ModelRun) \
            .join(ModelRun) \
            .join(ModelRunStatus) \
            .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATING)\
            .one()
        return session.query(Parameter) \
            .outerjoin(ParameterValue, and_(ParameterValue.model_run == model_run)) \
            .options(contains_eager(Parameter.parameter_values)) \
            .options(subqueryload(Parameter.namelist)) \
            .filter(Parameter.code_versions.contains(code_version))\
            .all()

    def _get_model_run_being_created(self, session):
        """
        Get the model run being created
        :param session: the session to use to get the model
        :return: the run model
        """
        return session.query(ModelRun) \
            .join(ModelRunStatus) \
            .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATING)\
            .one()
