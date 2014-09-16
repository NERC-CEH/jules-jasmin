"""
header
"""
import logging
from pylons import response
from pylons.controllers.util import Response
from pylons.decorators import jsonify
from joj.lib.base import BaseController, request, render, c
from joj.services.dataset import DatasetService
from joj.services.netcdf import NetCdfService
from joj.services.user import UserService
from formencode import htmlfill
from joj.lib import wmc_util
from joj.services.model_run_service import ModelRunService
from joj.utils import constants
from joj.utils.dataset_download_helper import DatasetDownloadHelper


log = logging.getLogger(__name__)


class DatasetController(BaseController):

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

    def preview(self, id):
        """ Renders a preview view of the first 10 rows of a dataset (currently point data only!)
        """

        # Need to make sure the user has access to the dataset in question
        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])
        ds = self._dataset_service.get_dataset_by_id(id, user_id = user.id)

        c.dataset_name = ds.name

        # This should contain the first 10 rows
        preview_data = self._netcdf_service.get_point_data_preview(ds.netcdf_url, 10)

        c.columns = preview_data.keys()

        # Number of rows - 1 for the row range--------------------------------------v
        c.row_set = [[preview_data[col][row] for col in c.columns] for row in range(9)]

        return render('dataset_preview.html')

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

    def download(self):
        """
        Download an output dataset specified by model run ID (model_run_id),
        output variable ID (output), period string (period) and year (year)
        :return: NetCDF File download
        """
        download_helper = DatasetDownloadHelper()
        try:
            model_run_id, output_var_id, period, year = download_helper.validate_parameters(request.params,
                                                                                            self.current_user)
            file_path = download_helper.generate_output_file_path(model_run_id, output_var_id, period, year)
            download_helper.set_header(response.headers, file_path)
            # This will stream the file to the browser without loading it all in memory
            # BUT only if the .ini file does not have 'debug=true' enabled
            return download_helper.download_file_generator(file_path)
        except (ValueError, TypeError):
            pass

def custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )
