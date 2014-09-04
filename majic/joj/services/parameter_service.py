"""
header
"""
import logging
from sqlalchemy.orm import subqueryload, contains_eager
from sqlalchemy.orm.exc import NoResultFound
from joj.services.general import DatabaseService
from joj.model import Session, ParameterValue, Namelist, Parameter, ModelRun, User, ModelRunStatus
from joj.utils import constants

log = logging.getLogger(__name__)


class ParameterService(DatabaseService):
    """Encapsulates operations on the Parameters"""

    def __init__(self, session=Session):
        super(ParameterService, self).__init__(session)

    def save_new_parameters(self, params_values, params_to_delete, user_id):
        """
        Save a list of parameters against the model currently being created and delete old parameters
        in the same transaction.
        :param params_values: List of parameter namelist / name pair and value
        in the form [[[parameter namelist, name], value]]
        :param params_to_delete: List of parameter namelist / name pairs to delete
        :param user_id: The current user id
        """
        with self.transaction_scope() as session:
            model_run = self.get_model_being_created_with_non_default_parameter_values(user_id, session)
            param_values_to_delete = []
            # Delete any parameters we've been asked to delete
            for parameter in params_to_delete:
                param_values_to_delete += model_run.get_parameter_values(parameter)
            self.remove_parameter_set_from_model(param_values_to_delete, model_run, session)
            # And save new parameters
            for parameter in params_values:
                self.save_parameter(model_run, parameter[0], parameter[1], session)

    def remove_parameter_set_from_model(self, parameter_values, model_run, session):
        """
        Remove a group of parameters from a model
        :param parameter_values: the values to remove
        :param model_run: the model run to remove them from
        :param session: the session to use
        :return: nothing
        """
        for model_parameter_value in model_run.parameter_values:
            for parameter_value_to_remove in parameter_values:
                if parameter_value_to_remove.parameter_id == model_parameter_value.parameter_id:
                    session.delete(model_parameter_value)

    def save_parameter(self, model_run, param_namelist_name, value, session, group_id=None):
        """
        Save parameter using a supplied session
        :param model_run: Model run to save against
        :param param_namelist_name: List containing the parameter namelist, name
        :param session: Session to use
        :param value: Value to set
        :param group_id: Specify an optional group_id to group parameters
        :return:
        """
        parameter = self.get_parameter_by_constant(param_namelist_name, session)
        try:
            parameter_value = session.query(ParameterValue) \
                .filter(ParameterValue.model_run_id == model_run.id) \
                .filter(ParameterValue.group_id == group_id) \
                .filter(ParameterValue.parameter_id == parameter.id).one()
        except NoResultFound:
            parameter_value = ParameterValue()
            parameter_value.parameter = parameter
            parameter_value.model_run = model_run
            parameter_value.group_id = group_id
        parameter_value.set_value_from_python(value)
        session.add(parameter_value)

    def get_parameter_by_constant(self, parameter_constant, session):
        """
        Get a JULES parameter by name
        :param parameter_constant: tuple of Namelist name and Parameter name
        :param session: Session to use
        :return: The first matching Parameter
        """
        nml_id = session.query(Namelist) \
            .filter(Namelist.name == parameter_constant[0]) \
            .one().id
        parameter = session.query(Parameter) \
            .filter(Parameter.namelist_id == nml_id) \
            .filter(Parameter.name == parameter_constant[1]) \
            .one()
        return parameter

    def get_model_being_created_with_non_default_parameter_values(self, user_id, session):
        """
        Get the current model run being created including all parameter_value which are not defaults
        Uses a supplied session
        :param user_id: Logged in user
        :param session: Session
        :return: Model run with parameters populated
        """
        return session.query(ModelRun) \
            .join(User) \
            .join(ModelRun.status) \
            .outerjoin(ModelRun.parameter_values, "parameter", "namelist") \
            .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATED) \
            .filter(ModelRun.user_id == user_id) \
            .options(subqueryload(ModelRun.code_version)) \
            .options(contains_eager(ModelRun.parameter_values)
                     .contains_eager(ParameterValue.parameter)
                     .contains_eager(Parameter.namelist))\
            .one()