"""
header
"""
import logging

from pylons import response, config
from pylons.controllers.util import Response, abort
from pylons.decorators import jsonify
from repoze.who.api import get_api
from sqlalchemy.orm.exc import NoResultFound

from joj.lib.base import BaseController, request, render, c
from joj.services.dataset import DatasetService
from joj.services.netcdf import NetCdfService
from joj.services.user import UserService
from joj.lib import wmc_util
from joj.services.model_run_service import ModelRunService
from joj.utils import constants
from joj.utils.download.ascii_dataset_download_helper import AsciiDatasetDownloadHelper
from joj.utils.download.netcdf_dataset_download_helper import NetcdfDatasetDownloadHelper


log = logging.getLogger(__name__)


class DatasetController(BaseController):
    """
    Dataset Controller
    """

    _dataset_service = None
    _netcdf_service = None

    def __init__(self,
                 dataset_service=DatasetService(),
                 netcdf_service=NetCdfService(),
                 user_service=UserService(),
                 model_run_service=ModelRunService()):
        """ Constructs a new dataset controller
        @param dataset_service: The dataset service to use with this controller
        @param netcdf_service: The NetCDF service to use with this controller
        @param user_service: The user service we're going to use
        """

        super(DatasetController, self).__init__()

        self._user_service = user_service
        self._dataset_service = dataset_service
        self._netcdf_service = netcdf_service
        self._model_run_service = model_run_service

    @jsonify
    def columns(self, id):
        """ Returns a list of the variable columns for the given dataset id
        @param id: The ID of the dataset to get columns for
        """
        ds = self._dataset_service.get_dataset_by_id(id, user_id=self.current_user.id)

        if ds:
            return self._netcdf_service.get_variable_column_names(ds.netcdf_url)
        else:
            return None

    @jsonify
    def list(self):
        """
        Gets a list of datasets for the currently logged in user
        :return: List of Datasets
        """
        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])

        return self._dataset_service.get_datasets_for_user(user.id)

    def wms(self, id):
        """ Indirection layer between ecomaps and the underlying dataset mapping
        server (currently THREDDS)
            @param id - ID of the dataset containing the real URL to the data
        """

        log.debug("Request for %s" % request.query_string)
        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])
        ds = self._dataset_service.get_dataset_by_id(id, user_id=user.id)

        redirect_url = "%s?%s" % (ds.wms_url.split('?')[0], request.query_string)

        log.debug("Redirecting to %s" % redirect_url)
        return wmc_util.create_request_and_open_url(redirect_url, external=False).read()

    def base(self):
        """
        Indirection layer to enable a base map wms service to be wrapped up in our domain
        """

        redirect_url = "http://vmap0.tiles.osgeo.org/wms/vmap0?%s" % request.query_string
        map_request = wmc_util.create_request_and_open_url(redirect_url, external=True)
        return Response(body=map_request.read(), content_type='image/jpeg')

    def timeselection(self, id):
        """ Gets the possible time points for a temporal dataset
            @param id: ID of the dataset to get time points for
        """

        ds = self._dataset_service.get_dataset_by_id(id, user_id=self.current_user.id)
        c.time_points = self._netcdf_service.get_time_points(ds.netcdf_url)

        c.dataset_name = ds.name
        c.column_name = request.params.get('col', '')
        c.identifier = "%s_%s" % (ds.id, c.column_name)

        if c.time_points:
            # Render the points back
            return render("dataset_time_values.html")

    @jsonify
    def single_cell_location(self, id):
        """
        Gets the location of a single cell dataset
        :param id:
        :return: ID of the dataset to get single cell location for
        """
        dataset = self._dataset_service.get_dataset_by_id(id, self.current_user.id)
        model_run = self._model_run_service.get_model_by_id(self.current_user, dataset.model_run_id)
        latlon = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE, is_list=True)
        if latlon is not None:
            lat, lon = latlon
            return {'lat': lat, 'lon': lon}
        else:
            return {'error': 'No single cell lat lon information found for this dataset'}

    @jsonify
    def multi_cell_location(self, id):
        """
        Gets the boundaries for a multi cell dataset
        :param id:
        :return:ID of the dataset to get location for
        """
        dataset = self._dataset_service.get_dataset_by_id(id, self.current_user.id)
        model_run = self._model_run_service.get_model_by_id(self.current_user, dataset.model_run_id)
        lat_bounds = model_run.get_python_parameter_value(constants.JULES_PARAM_LAT_BOUNDS, is_list=True)
        lon_bounds = model_run.get_python_parameter_value(constants.JULES_PARAM_LON_BOUNDS, is_list=True)

        if lat_bounds is not None and lon_bounds is not None:
            lat_s, lat_n = lat_bounds
            lon_w, lon_e = lon_bounds
            return {'lat_n': lat_n,
                    'lat_s': lat_s,
                    'lon_w': lon_w,
                    'lon_e': lon_e}
        else:
            return {'error': 'Multi cell location information unavailable for this dataset'}

    def download(self):
        """
        Download an output dataset specified by model run ID (model_run_id),
        output variable ID (output), period string (period) and year (year)
        :return: NetCDF File download
        """
        # NOTE: This controller action can be accessed without being a logged in user.
        if request.method == 'POST':
            who_api = get_api(request.environ)
            authenticated, headers = who_api.login(dict(request.params))
            if authenticated:
                self.current_user = self._user_service.get_user_by_username(request.environ['user.username'])
        if self.current_user is None:
            abort(status_code=400, detail="User not logged in - action aborted")

        dl_format = request.params.get('format')
        _config = dict(config)
        if dl_format.lower() == 'ascii':
            download_helper = AsciiDatasetDownloadHelper(config=_config)
        else:
            download_helper = NetcdfDatasetDownloadHelper(config=_config)
        try:
            model_run_id, output_var_name, period, year = download_helper.validate_parameters(request.params,
                                                                                              self.current_user)
            model_run = self._model_run_service.get_model_by_id(self.current_user, model_run_id)
            single_cell = not model_run.get_python_parameter_value(constants.JULES_PARAM_LATLON_REGION)
            file_path = download_helper.generate_output_file_path(
                model_run_id, output_var_name, period, year, single_cell)
            download_helper.set_response_header(response.headers, file_path, model_run, output_var_name, period, year)
            # This will stream the file to the browser without loading it all in memory
            # BUT only if the .ini file does not have 'debug=true' enabled
            return download_helper.download_file_generator(file_path, model_run)
        except (ValueError, TypeError):
            abort(status_code=400, detail="Invalid request parameters")
        except NoResultFound:
            abort(status_code=400, detail="Model run ID or Output variable ID could not be found.")
