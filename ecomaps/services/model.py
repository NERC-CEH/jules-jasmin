from sqlalchemy.orm.exc import NoResultFound
from ecomaps.model import Model
from ecomaps.services.general import DatabaseService

__author__ = 'Chirag Mistry (Tessella)'

class ModelService(DatabaseService):
    """Encapsulates operations on the Models"""

    def get_model_by_id(self, model_id):
        """Returns a single model with the given ID
            Params:
                model_id - ID of the model to look for
        """

        with self.readonly_scope() as session:

            try:
                return session.query(Model)\
                    .filter(Model.id == model_id).one()

            except NoResultFound:
                return None

    def get_all_models(self):

        with self.readonly_scope() as session:

            try:
                return session.query(Model).distinct()
            except NoResultFound:
                return None
