# header
from sqlalchemy.orm.exc import NoResultFound

from joj.services.general import DatabaseService
from joj.model import CodeVersion, ModelRun, ModelRunStatus
from formencode.validators import Invalid

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

    def define_model_run(self, name, code_version_id):
        with self.transaction_scope() as session:
            model_run = ModelRun()
            model_run.name = name
            code_version = session.query(CodeVersion).filter(CodeVersion.id == code_version_id).one()
            model_run.code_version = code_version
            model_status = session.query(ModelRunStatus).filter(ModelRunStatus.name == 'Defining').one()
            model_run.status = model_status
            session.add(model_run)


