"""
header
"""

import logging
from sqlalchemy.orm import subqueryload, contains_eager, joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_, desc
from joj.model import ModelRun, CodeVersion, ModelRunStatus, Parameter, ParameterValue, Session, User
from joj.services.general import DatabaseService
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from joj.services.general import ServiceException
from joj.model import Namelist
from joj.model.output_variable import OutputVariable

log = logging.getLogger(__name__)


class DuplicateName(Exception):
    """
    Exception thrown when the name of the run is a duplicate
    """
    pass


class ModelRunService(DatabaseService):
    """Encapsulates operations on the Run Models"""

    def __init__(self, session=Session, job_runner_client=JobRunnerClient()):
        super(ModelRunService, self).__init__(session)
        self._job_runner_client = job_runner_client

    def get_models_for_user(self, user):
        """
        Get all the run models a user can view

        :param user: the user trying to access the data
        :return : a list of model runs the user can see
        """
        with self.readonly_scope() as session:
            try:
                return session \
                    .query(ModelRun) \
                    .join(User) \
                    .filter(ModelRun.user == user) \
                    .order_by(desc(ModelRun.date_created)) \
                    .options(joinedload('user')) \
                    .all()
            except NoResultFound:
                return []

    def get_published_models(self):
        """
        Get all the published model runs
        :return: A list of published model runs
        """
        with self.readonly_scope() as session:
            try:
                return session.query(ModelRun).join(ModelRun.status) \
                    .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_PUBLISHED) \
                    .order_by(desc(ModelRun.date_created)).options(joinedload('user')).all()
            except NoResultFound:
                return []

    def get_model_by_id(self, user, id):
        """
        Get a specified model by the model id
        :param user: User to verify access to model run
        :param id: ID of the model run requested
        :return: The matching ModelRun.
        """
        with self.readonly_scope() as session:
            model_run = session.query(ModelRun).filter(ModelRun.id == id).options(joinedload('user')).one()
            # Is user allowed to acces this ID?
            if model_run.user_id == user.id or model_run.status.is_published():
                return model_run
            raise NoResultFound

    def publish_model(self, user, id):
        """
        Publish a specified model run
        :param user: User to verify ownership of model run
        :param id: ID of the model run to publish
        :return: void
        """
        with self.transaction_scope() as session:
            try:
                model_run = session.query(ModelRun) \
                    .join(ModelRunStatus) \
                    .join(User) \
                    .filter(ModelRun.user == user) \
                    .filter(ModelRun.id == id) \
                    .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_COMPLETED).one()
            except NoResultFound:
                raise ServiceException("Error publishing model run. Either the requested model run doesn't exist, "
                                       "has not completed or you are not authorised to access it")
            model_run.change_status(session, constants.MODEL_RUN_STATUS_PUBLISHED)

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

        :param code_version_id: id for the code version
        :return the code version model or throws Invalid
        """

        with self.readonly_scope() as session:
            return session.query(CodeVersion).filter(CodeVersion.id == code_version_id).one()

    def update_model_run(self, user, name, science_configuration_id, description=""):
        """
        Update the creation model run definition

        :param user: user creating the model
        :param name: name of the model run
        :param science_configuration_id: the science_configuration for the run
        :param description: description
        """
        with self.transaction_scope() as session:

            duplicate_names = session \
                .query(ModelRun) \
                .join(User) \
                .join(ModelRunStatus) \
                .filter(ModelRun.user == user) \
                .filter(ModelRun.name == name) \
                .filter(ModelRunStatus.name != constants.MODEL_RUN_STATUS_CREATED) \
                .count()

            if duplicate_names != 0:
                raise DuplicateName()

            try:
                model_run = self._get_model_run_being_created(session, user)
                if model_run.science_configuration_id is not None:
                    old_configuration = \
                        self._get_science_configuration(model_run.science_configuration_id, session)
                    self._remove_parameter_set_from_model(old_configuration.parameter_values, model_run, session)

            except NoResultFound:
                model_run = ModelRun()
                model_run.change_status(session, constants.MODEL_RUN_STATUS_CREATED)
                model_run.user = user
                session.add(model_run)

            model_run.name = name
            science_configuration = self._get_science_configuration(science_configuration_id, session)
            model_run.science_configuration_id = science_configuration.id
            model_run.code_version = science_configuration.code_version
            model_run.description = description
            self._copy_parameter_set_into_model(science_configuration.parameter_values, model_run, session)

    def get_model_run_being_created_or_default(self, user):
        """
        Get the run being created or a default model if no run is being created

        :param user: logged in user
        :returns: Model run being created or a new Model
        """
        try:
            with self.readonly_scope() as session:
                return self._get_model_run_being_created(session, user)
        except NoResultFound:
            return ModelRun(science_configuration_id=constants.DEFAULT_SCIENCE_CONFIGURATION)

    def get_parameters_for_model_being_created(self, user):
        """
        Get the parameters for the model being created

        :param user the logged in user
        :return a list of populated parameters, populated with parameter values
        """
        with self.readonly_scope() as session:
            return self._get_parameters_for_creating_model(session, user)

    def store_parameter_values(self, parameters_to_set, user):
        """
        Store the parameter values in the database
        :param parameters_to_set: dictionary of parameter ids and parameter values
        :param user: the logged in user
        :return: Nothing
        """

        with self.transaction_scope() as session:
            model_run = self._get_model_run_being_created(session, user)
            session.query(ParameterValue) \
                .filter(ParameterValue.model_run == model_run) \
                .delete()
            parameters = self._get_parameters_for_creating_model(session, user)
            for parameter in parameters:
                if parameter.id in parameters_to_set.keys():
                    parameter_value = parameters_to_set[parameter.id]
                    if parameter_value is not None:
                        val = ParameterValue()
                        val.set_value_from_python(parameter_value)
                        val.parameter = parameter
                        val.model_run = model_run
                        session.add(val)

    def get_model_being_created_with_non_default_parameter_values(self, user):
        """
        Get the current model run being created including all parameter_value which are not defaults
        :param user: logged in user
        :return:model run with parameters populated
        """
        with self.readonly_scope() as session:
            return self._get_model_being_created_with_non_default_parameter_values(user, session)

    def submit_model_run(self, user):
        """
        Submit the model run which is being created to be run
        :param user: the logged in user
        :return:new status of the job
        """
        with self.transaction_scope() as session:
            model = self._get_model_run_being_created(session, user)
            status_name, message = self._job_runner_client.submit(model)
            status = model.change_status(session, status_name)
            return status, message

    def get_scientific_configurations(self):
        """
        get all the scientific configurations
        :return: a list of scientific configurations
        """
        with self.readonly_scope() as session:
            runs = session \
                .query(ModelRun) \
                .join(ModelRunStatus) \
                .join(User) \
                .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATED) \
                .filter(User.username == constants.CORE_USERNAME) \
                .all()

            return [{'id': run.id, 'name': run.name, 'description': run.description} for run in runs]

    def save_driving_dataset_for_new_model(self, driving_dataset, old_driving_dataset, user):
        """
        Save a driving dataset against the current model run being created
        :param driving_dataset: Driving dataset to save
        :param old_driving_dataset: Set of old diving data parameter to remove
        :param user: Currently logged in user
        """
        with self.transaction_scope() as session:
            model_run = self._get_model_run_being_created(session, user)
            model_run.driving_dataset_id = driving_dataset.id
            if old_driving_dataset is not None:
                self._remove_parameter_set_from_model(old_driving_dataset.parameter_values, model_run, session)
            self._copy_parameter_set_into_model(driving_dataset.parameter_values, model_run, session)

    def get_parameter_by_name(self, param_name, param_namelist):
        """
        Look up the parameter for a given parameter name and namelist
        :param param_name: Parameter name
        :param param_namelist: Parameter namelist
        :return: The first matching parameter
        """
        with self.readonly_scope() as session:
            parameter = self._get_parameter_by_name(param_name, param_namelist, session)
            return parameter

    def save_parameter(self, param_namelist_name, value, user, group_id=None):
        """
        Save a parameter against the model currently being created
        :param param_namelist_name: List containing the parameter namelist, name
        :param value: The value to set
        :param user: The currently logged in user
        :param group_id: If this parameter's namelist is used more than once, specify a group ID to group parameters
        together into one instance of the namelist
        :return:
        """
        with self.transaction_scope() as session:
            model_run = self._get_model_being_created_with_non_default_parameter_values(user, session)
            parameter = self._get_parameter_by_name(param_namelist_name[1], param_namelist_name[0], session)
            try:
                parameter_value = session.query(ParameterValue)\
                    .filter(ParameterValue.model_run_id == model_run.id)\
                    .filter(ParameterValue.group_id == group_id)\
                    .filter(ParameterValue.parameter_id == parameter.id).one()
            except NoResultFound:
                parameter_value = ParameterValue()
                parameter_value.parameter = parameter
                parameter_value.model_run = model_run
                parameter_value.group_id = group_id
            parameter_value.set_value_from_python(value)
            session.add(parameter_value)

    def _get_parameter_by_name(self, param_name, param_namelist, session):
        """
        Get a JULES parameter by name
        :param param_name: Parameter name
        :param param_namelist: Namelist parameter belongs to
        :param session: Session to use
        :return: The first matching Parameter
        """
        nml_id = session.query(Namelist) \
            .filter(Namelist.name == param_namelist) \
            .one().id
        parameter = session.query(Parameter) \
            .filter(Parameter.namelist_id == nml_id) \
            .filter(Parameter.name == param_name) \
            .one()
        return parameter

    def _get_science_configuration(self, science_configuration_id, session):
        """
        get The science configuration indicated by the id using the current session
        :param science_configuration_id:
        :param session:
        :return:
        """
        science_configuration = session \
            .query(ModelRun) \
            .join(User) \
            .filter(ModelRun.id == science_configuration_id) \
            .filter(User.username == constants.CORE_USERNAME) \
            .outerjoin(ModelRun.parameter_values) \
            .options(contains_eager(ModelRun.parameter_values)) \
            .one()
        return science_configuration

    def _get_model_being_created_with_non_default_parameter_values(self, user, session):
        """
        Get the current model run being created including all parameter_value which are not defaults
        Uses a supplied session
        :param user: Logged in user
        :param session: Session
        :return: Model run with parameters populated
        """
        return session.query(ModelRun) \
            .join(User) \
            .join(ModelRun.status) \
            .outerjoin(ModelRun.parameter_values, "parameter", "namelist") \
            .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATED) \
            .filter(ModelRun.user == user) \
            .options(subqueryload(ModelRun.code_version)) \
            .options(contains_eager(ModelRun.parameter_values)
                     .contains_eager(ParameterValue.parameter)
                     .contains_eager(Parameter.namelist)) \
            .one()

    def _get_parameters_for_creating_model(self, session, user):
        """
        get parameters for the model run being created
        :param session: session to use
        :param user: the logged in user
        :return: a list of parameters
        """
        code_version, model_run = session.query(CodeVersion, ModelRun) \
            .join(ModelRun) \
            .join(ModelRunStatus) \
            .join(User) \
            .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATED) \
            .filter(ModelRun.user == user) \
            .one()
        return session.query(Parameter) \
            .outerjoin(ParameterValue,
                       and_(Parameter.id == ParameterValue.parameter_id, ParameterValue.model_run == model_run)) \
            .options(contains_eager(Parameter.parameter_values)) \
            .options(subqueryload(Parameter.namelist)) \
            .filter(Parameter.code_versions.contains(code_version)) \
            .all()

    def _get_model_run_being_created(self, session, user):
        """
        Get the model run being created
        :param session: the session to use to get the model
        :param user: the currently logged in user
        :return: the run model
        """
        return session.query(ModelRun) \
            .join(ModelRunStatus) \
            .join(User) \
            .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATED) \
            .filter(ModelRun.user == user) \
            .one()

    def _remove_parameter_set_from_model(self, parameter_values, model_run, session):
        """
        Remove a group of parameters from a model
        :param parameter_values: the values to remove
        :param model_run: the model run to remove them from
        :param session: the session to use
        :return: nothing
        """
        for model_parameter_value in model_run.parameter_values:
            for parameter_value_to_remove in parameter_values:
                if parameter_value_to_remove.parameter.id == model_parameter_value.parameter.id:
                    session.delete(model_parameter_value)

    def _copy_parameter_set_into_model(self, parameter_values, model_run, session):
        """
        Copy the parameters into a model
        :param parameter_values: the values to copy
        :param model_run: the model run to copy them to
        :param session: the session to use
        :return: nothing
        """
        for parameter_value in parameter_values:
            val = ParameterValue()
            val.value = parameter_value.value
            val.parameter_id = parameter_value.parameter_id
            val.model_run = model_run
            session.add(val)

    def get_output_variables(self):
        """
        Get all the JULES output variables
        :return: list of OutputVariables
        """
        with self.readonly_scope() as session:
            return session.query(OutputVariable).all()

    def get_output_variable_by_id(self, id):
        """
        Get an Output Variable by Database ID
        :param id: Database ID of Output Variable to retrieve
        :return: Matching OutputVariable
        """
        with self.readonly_scope() as session:
            return session.query(OutputVariable).filter(OutputVariable.id == id).one()