"""
# header
"""

import logging

from pylons import request, config
from pylons.decorators import jsonify

from joj.lib.base import BaseController, render, c
from joj.services.user import UserService
from joj.services.model_run_service import ModelRunService
from joj.services.dataset import DatasetService
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.utils.general_controller_helper import is_thredds_up


log = logging.getLogger(__name__)


class MapController(BaseController):
    """
    Controller for the map view page
    """

    _user_service = None
    _model_run_service = None
    _dataset_service = None

    def __init__(self,
                 user_service=UserService(),
                 model_run_service=ModelRunService(),
                 dataset_service=DatasetService(),
                 dap_factory=DapClientFactory()):
        """
        Constructor
        :param user_service: Service to access user data
        :param model_run_service: Service to access model runs
        :param dataset_service: Service to access datasets
        :param dap_factory: Factory to create a dap client
        """

        super(MapController, self).__init__()

        self._user_service = user_service
        self._model_run_service = model_run_service
        self._dataset_service = dataset_service
        self._dap_factory = dap_factory

    def view(self, id):
        """
        Controller to load specific model_runs onto the map viewer
        :param id: Database ID of model_run to view data for
        :return: Rendered map page
        """
        models = self._model_run_service.get_models_for_user(self.current_user)
        models_to_view = [m for m in models if m.status.allow_visualise()]
        counter = 0
        for model in models_to_view:
            for dataset in model.datasets:
                dataset.layer_id = counter
                counter += 1
        published_models_to_view = self._model_run_service.get_published_models()
        for model in published_models_to_view:
            for dataset in model.datasets:
                dataset.layer_id = counter
                counter += 1
        c.model_run_sorts = \
            [
                {
                    'name': "Mine",
                    'model_runs': models_to_view
                },
                {
                    'name': "Published",
                    'model_runs': published_models_to_view
                }
            ]
        c.id = id
        c.DATASET_TYPE_COVERAGE = 'Coverage'
        c.DATASET_TYPE_SINGLE_CELL = 'Single Cell'
        c.DATASET_TYPE_TRANSECT = 'Transect'
        c.DATASET_TYPE_LAND_COVER_FRAC = 'Land Cover Fraction'
        c.DATASET_TYPE_SOIL_PROP = 'Soil Properties File'

        return render('map.html')

    @jsonify
    def is_thredds_up(self):
        """
        See if the THREDDS server is up
        :return:
        """
        thredds_up = is_thredds_up(config)
        return {'thredds_up': thredds_up}

    @jsonify
    def graph(self, id):
        """
        Get time-series graphing data for a specified dataset and position
        :param id: The dataset ID to request
        :return: JSON graphing data
        """
        lat = float(request.params['lat'])
        lon = float(request.params['lon'])
        dataset = self._dataset_service.get_dataset_by_id(id, self.current_user.id)
        url = dataset.netcdf_url
        dap_client = self._dap_factory.get_graphing_dap_client(url)
        return dap_client.get_graph_data(lat, lon)