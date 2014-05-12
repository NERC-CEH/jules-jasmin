from sqlalchemy import or_
from sqlalchemy.orm import joinedload, contains_eager, immediateload
from ecomaps.model import Dataset, DatasetType, Analysis
from ecomaps.services.general import DatabaseService

__author__ = 'Phil Jenkins (Tessella)'

class DatasetService(DatabaseService):
    """Encapsulates operations on Map datasets"""

    def get_datasets_for_user(self, user_id, dataset_type=None, dataset_type_id=None):
        """Returns a list of datasets that the supplied user has access to,
            and is of a particular type. This can be specified as either an ID
            or a name, depending on which is more convenient

            Params:
                user_id: ID of the user to get a list of datasets for
                dataset_type: String name of the dataset type
                dataset_type_id: ID of the dataset type
        """

        with self.readonly_scope() as session:

            # Find all datasets that are viewable by this user (private)
            # or are public (null viewable_by)
            # Note SQLAlchemy wants '== None' not 'is None'
            if dataset_type_id is None and dataset_type is None:
                return session.query(DatasetType).join(DatasetType.datasets) \
                                                .options(contains_eager(DatasetType.datasets)) \
                                                .filter(or_(Dataset.viewable_by_user_id == user_id,
                                                 Dataset.viewable_by_user_id == None), Dataset.deleted == False).all()
            elif dataset_type_id is None:
                return session.query(Dataset).join(DatasetType).filter(DatasetType.type == dataset_type, or_(Dataset.viewable_by_user_id == user_id,
                                                 Dataset.viewable_by_user_id == None), Dataset.deleted == False).all()
            else:
                return session.query(Dataset).filter(Dataset.dataset_type_id == dataset_type_id, or_(Dataset.viewable_by_user_id == user_id,
                                                 Dataset.viewable_by_user_id == None), Dataset.deleted == False).all()



    def get_dataset_types(self):
        """Returns all of the dataset types in the system"""

        with self.readonly_scope() as session:

            return session.query(DatasetType).all()

    def get_dataset_by_id(self, dataset_id, user_id=None):
        """ Returns a single dataset with the given ID
            Params:
                dataset_id: ID of the dataset to look for
        """

        with self.readonly_scope() as session:
                return session.query(Dataset)\
                            .options(joinedload(Dataset.dataset_type)) \
                            .filter(Dataset.id == dataset_id,
                                    or_(Dataset.viewable_by_user_id == user_id,
                                                 Dataset.viewable_by_user_id == None)).one()

    def get_all_datasets(self):
        """
        Returns a list of all active datasets in EcoMaps
        """
        with self.readonly_scope() as session:
            return session.query(Dataset)\
                        .options(joinedload(Dataset.dataset_type)) \
                        .filter(Dataset.deleted == False) \
                        .all()

    def create_coverage_dataset(self,name,wms_url,netcdf_url,low_res_url,
                                data_range_from, data_range_to, is_categorical):
        """
        Creates a coverage dataset in the EcoMaps DB
            @param name: Display name of the dataset
            @param wms_url: Endpoint for the mapping server
            @param netcdf_url: URL of the OpenDAP endpoint for this dataset
            @param low_res_url: URL for accessing the NetCDF file over the HTTP protocol
            @param data_range_from: Low range for the data
            @param data_range_to: High range for the data
            @param is_categorical: Set to true if the data is categorical (not continuous)
        """
        with self.transaction_scope() as session:

            dataset_type = session.query(DatasetType).filter(DatasetType.type=='Coverage').one()

            dataset = Dataset()
            dataset.name = name
            dataset.dataset_type = dataset_type
            dataset.netcdf_url = netcdf_url
            dataset.wms_url = wms_url
            dataset.low_res_url = low_res_url
            dataset.data_range_from = data_range_from
            dataset.data_range_to  = data_range_to
            dataset.is_categorical = is_categorical

            session.add(dataset)

    def create_point_dataset(self,name,wms_url,netcdf_url):
        """
        Creates a point dataset in the EcoMaps DB
            @param name: Display name of the dataset
            @param wms_url: Endpoint for the mapping server
            @param netcdf_url: URL of the OpenDAP endpoint for this dataset
        """

        with self.transaction_scope() as session:

            dataset_type = session.query(DatasetType).filter(DatasetType.type=='Point').one()

            dataset = Dataset()
            dataset.name = name
            dataset.dataset_type = dataset_type
            dataset.netcdf_url = netcdf_url
            dataset.wms_url = wms_url
            dataset.low_res_url = None

            session.add(dataset)

    def delete(self, id, user_id):
        """
        Soft-deletes a dataset to remove it from active lists
            @param id: ID of dataset to delete
            @param user_id: ID of the user attempting the delete operation
        """
        # First let's make sure the user specified can access the dataset
        ds = self.get_dataset_by_id(id, user_id)

        if ds:
            with self.transaction_scope() as session:

                dataset = session.query(Dataset).get(id)
                dataset.deleted = True

                session.add(dataset)

    def update(self, id, data_range_from, data_range_to, is_categorical):
        """
        Updates basic properties on the dataset specified
            @param id: ID of the dataset to update
            @param data_range_from: Low range of data
            @param data_range_to: High range of data
            @param is_categorical: Set to true for non-continuous data
        """
        with self.transaction_scope() as session:

            dataset = session.query(Dataset).get(id)

            dataset.data_range_from = data_range_from
            dataset.data_range_to = data_range_to
            dataset.is_categorical = is_categorical

            session.add(dataset)