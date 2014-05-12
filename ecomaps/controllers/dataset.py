import logging
import urllib2
from pylons import url
from pylons.controllers.util import redirect, Response
import formencode
from pylons.decorators import jsonify
from ecomaps.lib.base import BaseController, request, render, c
from ecomaps.services.dataset import DatasetService
from ecomaps.services.netcdf import NetCdfService
from ecomaps.services.user import UserService
from ecomaps.model.add_dataset_form import AddDatasetForm, UpdateDatasetForm
from formencode import htmlfill


__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class DatasetController(BaseController):

    _dataset_service = None
    _netcdf_service = None


    def __init__(self, dataset_service=DatasetService(), netcdf_service=NetCdfService(),
                 user_service=UserService()):
        """ Constructs a new dataset controller
        @param dataset_service: The dataset service to use with this controller
        @param netcdf_service: The NetCDF service to use with this controller
        @param user_service: The user service we're going to use
        """

        super(DatasetController, self).__init__()

        self._user_service = user_service
        self._dataset_service = dataset_service
        self._netcdf_service = netcdf_service

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
        return urllib2.urlopen(redirect_url).read()

    def base(self):
        """ Indirection layer to enable a base map wms service to be wrapped up in our domain
        """

        redirect_url = "http://vmap0.tiles.osgeo.org/wms/vmap0?%s" % request.query_string
        #return urllib2.urlopen(redirect_url).read()
        return Response(body=urllib2.urlopen(redirect_url).read(), content_type='image/jpeg')


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

    def index(self):
        """Allow admin-user to see all available datasets. If user is non-admin, redirect to page not found.
        """
        identity = request.environ.get('REMOTE_USER')

        user = self._user_service.get_user_by_username(identity)

        if user.access_level == "Admin":

            c.datasets = self._dataset_service.get_all_datasets()
            return render('all_datasets.html')

        else:

            return render('not_found.html')

    def add(self):
        "Add a new dataset"
        if not request.POST:

            return render('add_dataset.html')

        schema = AddDatasetForm()
        c.form_errors = {}

        if request.POST:

            try:
                c.form_result = schema.to_python(request.params)

            except formencode.Invalid, error:

                c.form_result = error.value
                c.form_errors = error.error_dict or {}

            if c.form_errors:
                html = render('add_dataset.html')
                return htmlfill.render(html,
                                       defaults=c.form_result,
                                       errors=c.form_errors,
                                       auto_error_formatter=custom_formatter)
            else:
                dataset_type = c.form_result.get('type')

                if dataset_type == "Coverage":
                    self._dataset_service.create_coverage_dataset(c.form_result.get('name'),
                                                            c.form_result.get('wms_url'),
                                                            c.form_result.get('netcdf_url'),
                                                            c.form_result.get('low_res_url'),
                                                            c.form_result.get('data_range_from'),
                                                            c.form_result.get('data_range_to'),
                                                            c.form_result.get('is_categorical'))
                else:
                    # Point data, so we only need the netcdf OpenDAP url,
                    # we need to generate a gridded copy for the WMS
                    opendap_url = c.form_result.get('netcdf_url')
                    wms_url = self._netcdf_service.overlay_point_data(opendap_url)

                    self._dataset_service.create_point_dataset(c.form_result.get('name'),
                                                            wms_url,
                                                            opendap_url)

                return redirect(url(controller="dataset"))

    def edit(self, id):
        """Enables a dataset's details to be updated, intended as an admin-only function

            @param id: ID of the dataset to edit
        """
        # Kick unauthorized users out straight away
        if not self.current_user.access_level == 'Admin':
            return render('not_found.html')

        c.dataset_to_edit = self._dataset_service.get_dataset_by_id(id, user_id=self.current_user.id)

        # GET request...
        if not request.method == 'POST':

            return render('edit_dataset.html')

        else:

            # Define our form schema
            schema = UpdateDatasetForm()
            c.form_errors = {}

            try:
                c.form_result = schema.to_python(request.params)

            except formencode.Invalid, error:

                c.form_result = error.value
                c.form_errors = error.error_dict or {}

            if c.form_errors:
                html = render('edit_dataset.html')
                return htmlfill.render(html,
                                       defaults=c.form_result,
                                       errors=c.form_errors,
                                       auto_error_formatter=custom_formatter)
            else:

                # Perform the update
                self._dataset_service.update(c.form_result.get('dataset_id'),
                                             c.form_result.get('data_range_from'),
                                             c.form_result.get('data_range_to'),
                                             c.form_result.get('is_categorical'))
                # By default a user will be an external user
                # self._user_service.update(c.form_result.get('first_name'),
                #                           c.form_result.get('last_name'),
                #                           user_email,
                #                           "Admin" if c.form_result.get('is_admin') else "CEH",
                #                           c.form_result.get('user_id'))

                return redirect(url(controller="dataset"))


    def timeselection(self, id):
        """ Gets the possible time points for a temporal dataset
            @param id: ID of the dataset to get time points for
        """

        ds = self._dataset_service.get_dataset_by_id(id, user_id = self.current_user.id)
        c.time_points = self._netcdf_service.get_time_points(ds.netcdf_url)

        c.dataset_name = ds.name
        c.column_name = request.params.get('col', '')
        c.identifier = "%s_%s" % (ds.id, c.column_name)

        if c.time_points:
            # Render the points back
            return render("dataset_time_values.html")


def custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )
