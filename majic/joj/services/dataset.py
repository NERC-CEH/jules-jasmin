"""
header
"""
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, contains_eager, subqueryload
from joj.model import Dataset, DatasetType, DrivingDataset, DrivingDatasetParameterValue, Parameter, \
    DrivingDatasetLocation
from joj.services.general import DatabaseService
from joj.model.non_database.spatial_extent import SpatialExtent
from joj.model.non_database.temporal_extent import TemporalExtent
from joj.utils import constants
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams


class DatasetService(DatabaseService):
    """Encapsulates operations on Map datasets"""

    def get_datasets_for_user(self, user_id, dataset_type=None, dataset_type_id=None):
        """
        Returns a list of datasets that the supplied user has access to,
        and is of a particular type. This can be specified as either an ID
        or a name, depending on which is more convenient
        :param user_id: ID of the user to get a list of datasets for
        :param dataset_type: String name of the dataset type
        :param dataset_type_id: ID of the dataset type
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
                return session.query(Dataset).join(DatasetType).filter(DatasetType.type == dataset_type,
                                                                       or_(Dataset.viewable_by_user_id == user_id,
                                                                           Dataset.viewable_by_user_id == None),
                                                                       Dataset.deleted == False).all()
            else:
                return session.query(Dataset).filter(Dataset.dataset_type_id == dataset_type_id,
                                                     or_(Dataset.viewable_by_user_id == user_id,
                                                         Dataset.viewable_by_user_id == None),
                                                     Dataset.deleted == False).all()

    def get_dataset_types(self):
        """Returns all of the dataset types in the system"""

        with self.readonly_scope() as session:
            return session.query(DatasetType).all()

    def get_dataset_by_id(self, dataset_id, user_id=None):
        """ Returns a single dataset with the given ID
        :param dataset_id: ID of the dataset to look for
        :param user_id: Optional user ID to match
        """

        with self.readonly_scope() as session:
            return session.query(Dataset) \
                .options(joinedload(Dataset.dataset_type)) \
                .filter(Dataset.id == dataset_id,
                        or_(Dataset.viewable_by_user_id == user_id,
                            Dataset.viewable_by_user_id == None)).one()

    def get_all_datasets(self):
        """
        Returns a list of all active datasets in EcoMaps
        """
        with self.readonly_scope() as session:
            return session.query(Dataset) \
                .options(joinedload(Dataset.dataset_type)) \
                .filter(Dataset.deleted == False) \
                .all()

    def create_coverage_dataset(self, name, wms_url, netcdf_url, low_res_url,
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
            dataset_type = session.query(DatasetType).filter(DatasetType.type == 'Coverage').one()

            dataset = Dataset()
            dataset.name = name
            dataset.dataset_type = dataset_type
            dataset.netcdf_url = netcdf_url
            dataset.wms_url = wms_url
            dataset.low_res_url = low_res_url
            dataset.data_range_from = data_range_from
            dataset.data_range_to = data_range_to
            dataset.is_categorical = is_categorical

            session.add(dataset)

    def create_point_dataset(self, name, wms_url, netcdf_url):
        """
        Creates a point dataset in the EcoMaps DB
            @param name: Display name of the dataset
            @param wms_url: Endpoint for the mapping server
            @param netcdf_url: URL of the OpenDAP endpoint for this dataset
        """

        with self.transaction_scope() as session:
            dataset_type = session.query(DatasetType).filter(DatasetType.type == 'Point').one()

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

    def get_driving_datasets(self, user):
        """
        Returns a list of availiable driving datasets
         If you are an admin this is all of them, if you are a normal user this is only the published ones
        :return: List of driving datasets
        """

        with self.readonly_scope() as session:
            query = session.query(DrivingDataset)\
                .options(joinedload(DrivingDataset.parameter_values))\
                .order_by(DrivingDataset.view_order_index)
            if not user.is_admin():
                query = query.filter(DrivingDataset.is_restricted_to_admins == False)
            return query.all()

    def _get_driving_dataset_by_id_in_session(self, driving_dataset_id, session):
        """
        get a driving dataset by id inside a session
        :param driving_dataset_id: the driving dataset id
        :param session: the session o use
        :return:a driving dataset
        """
        return session.query(DrivingDataset) \
            .outerjoin(DrivingDataset.parameter_values, "parameter", "namelist") \
            .options(contains_eager(DrivingDataset.parameter_values)
                     .contains_eager(DrivingDatasetParameterValue.parameter)
                     .contains_eager(Parameter.namelist)) \
            .options(subqueryload(DrivingDataset.locations)) \
            .filter(DrivingDataset.id == driving_dataset_id) \
            .one()

    def get_driving_dataset_by_id(self, id):
        """
        Get a driving dataset specified by an ID
        :param id: Driving dataset ID
        :return: DrivingDataset
        """
        with self.readonly_scope() as session:
            return self._get_driving_dataset_by_id_in_session(id, session)

    def get_spatial_extent(self, driving_dataset_id):
        """
        Returns a SpatialExtent representing the available lat/long boundaries for the dataset
        :param driving_dataset_id: The database ID
        :return: SpatialExtent for the specified dataset
        """
        with self.readonly_scope() as session:
            driving_dataset = session.query(DrivingDataset)\
                .filter(DrivingDataset.id == driving_dataset_id)\
                .one()
        return SpatialExtent(driving_dataset.boundary_lat_north,
                             driving_dataset.boundary_lat_south,
                             driving_dataset.boundary_lon_west,
                             driving_dataset.boundary_lon_east)

    def get_temporal_extent(self, driving_dataset_id):
        """
        Returns a TemporalExtent representing the available time boundaries for the dataset
        :param driving_dataset_id: The database ID
        :return: TemporalExtent for the specified dataset
        """
        with self.readonly_scope() as session:
            driving_dataset = session.query(DrivingDataset)\
                .filter(DrivingDataset.id == driving_dataset_id)\
                .one()
        return TemporalExtent(driving_dataset.time_start, driving_dataset.time_end)

    def get_id_for_user_upload_driving_dataset(self):
        """
        Return the database ID for the driving dataset which indicates
        the special case where the user has uploaded their own driving dataset.
        :return: The database ID of the user uploaded driving dataset
        """
        with self.readonly_scope() as session:
            driving_dataset = session.query(DrivingDataset)\
                .filter(DrivingDataset.name == constants.USER_UPLOAD_DRIVING_DATASET_NAME)\
                .one()
        return driving_dataset.id

    def create_driving_dataset(self, driving_dataset_id, results, locations, model_run_service, land_cover_service):

        """
        Create a driving dataset object from a results dictionary
        :param driving_dataset_id: id of the driving dataset to edit (None for create new)
        :param locations: locations list to use
        :param results: the results
        :param model_run_service: model run service
        :param land_cover_service: land cover service
        :return: nothing
        """

        with self.transaction_scope() as session:
            if driving_dataset_id is None:
                driving_dataset = DrivingDataset()
                session.add(driving_dataset)
            else:
                session\
                    .query(DrivingDatasetParameterValue)\
                    .filter(DrivingDatasetParameterValue.driving_dataset_id == driving_dataset_id)\
                    .delete()
                session\
                    .query(DrivingDatasetLocation)\
                    .filter(DrivingDatasetLocation.driving_dataset_id == driving_dataset_id)\
                    .delete()
                driving_dataset = self._get_driving_dataset_by_id_in_session(driving_dataset_id, session)

            driving_dataset_jules_params = DrivingDatasetJulesParams()

            driving_dataset_jules_params.update_driving_dataset_from_dict(
                driving_dataset,
                session,
                model_run_service,
                land_cover_service,
                results,
                locations)

    def get_dataset_types_dictionary(self):
        """
        Get the dataset types as a dictionary, index is name value is database id
        :return: dictionary
        """

        dataset_types_dictionary = {}
        for dataset in self.get_dataset_types():
            dataset_types_dictionary[dataset.type] = dataset.id
        return  dataset_types_dictionary