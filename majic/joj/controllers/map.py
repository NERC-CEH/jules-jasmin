# header

import logging
import urllib2
from pylons import config, request
from pylons.decorators import jsonify
from joj.lib.base import BaseController, render, c
from joj.services.user import UserService
from joj.services.model_run_service import ModelRunService
from joj.services.dap_client import DapClient
from joj.services.dataset import DatasetService

log = logging.getLogger(__name__)


class MapController(BaseController):
    """
    Controller for the map view page
    """

    _user_service = None
    _model_run_service = None
    _dataset_service = None

    def __init__(self, user_service=UserService(), model_run_service=ModelRunService(),
                 dataset_service=DatasetService()):
        """
        Constructor
        :param user_service: Service to access user data
        :param model_run_service: Service to access model runs
        :param dataset_service: Service to access datasets
        """

        super(MapController, self).__init__()

        self._user_service = user_service
        self._model_run_service = model_run_service
        self._dataset_service = dataset_service

    def view(self, id):
        """
        Controller to load specific model_runs onto the map viewer
        :param id: Database ID of model_run to view data for
        :return: Rendered map page
        """
        models = self._model_run_service.get_models_for_user(self.current_user)
        models_to_view = [m for m in models if m.status.allow_visualise()]
        c.model_run_sorts = \
            [
                {
                    'name': "Mine",
                    'model_runs': models_to_view
                },
                {
                    'name': "Published",
                    'model_runs': self._model_run_service.get_published_models()
                }
            ]
        c.id = id
        return render('map.html')

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
        dap_client = DapClient(url)
        return dap_client.get_graph_data(lat, lon)

    @jsonify
    def test(self):
        """
            Tests the connection to the map server
        """
        try:
            response = urllib2.urlopen(config['thredds.server_url'], timeout=int(config['thredds.server_timeout'])).read()
            return True
        except:
            return False