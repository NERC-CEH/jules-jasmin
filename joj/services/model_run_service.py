# header

from joj.services.general import DatabaseService
from joj.model import CodeVersion


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