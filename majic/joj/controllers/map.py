"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import logging
import datetime

from pylons import request, config
from pylons.decorators import jsonify

from joj.lib.base import BaseController, render, c
from joj.services.user import UserService
from joj.services.model_run_service import ModelRunService
from joj.services.dataset import DatasetService
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.utils.general_controller_helper import is_thredds_up
from joj.utils import constants


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
        c.DATASET_TYPE_COVERAGE = constants.DATASET_TYPE_COVERAGE
        c.DATASET_TYPE_SINGLE_CELL = constants.DATASET_TYPE_SINGLE_CELL
        c.DATASET_TYPE_TRANSECT = constants.DATASET_TYPE_TRANSECT
        c.DATASET_TYPE_LAND_COVER_FRAC = constants.DATASET_TYPE_LAND_COVER_FRAC
        c.DATASET_TYPE_SOIL_PROP = constants.DATASET_TYPE_SOIL_PROP
        c.GRAPH_NPOINTS = constants.GRAPH_NPOINTS

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
        str_time = request.params['time']
        if len(str_time.strip()) > 0:
            time = datetime.datetime.strptime(str_time, constants.GRAPH_TIME_FORMAT)
        else:
            time = None
        dataset = self._dataset_service.get_dataset_by_id(id, self.current_user.id)
        model_run = self._model_run_service.get_model_by_id(self.current_user, dataset.model_run_id)
        url = dataset.netcdf_url
        dap_client = self._dap_factory.get_graphing_dap_client(url)
        return dap_client.get_graph_data(lat, lon, time, run_name=model_run.name)