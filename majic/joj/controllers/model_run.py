"""
header
"""

import logging
import datetime
from formencode import htmlfill

from pylons import url

from pylons.decorators import validate

from sqlalchemy.orm.exc import NoResultFound

from joj.services.user import UserService
from joj.lib.base import BaseController, c, request, render, redirect
from joj.model.model_run_create_form import ModelRunCreateFirst
from joj.services.model_run_service import ModelRunService, DuplicateName
from joj.services.dataset import DatasetService
from joj.lib import helpers
from joj.utils import constants
from joj.utils.error import abort_with_error

from joj.model.non_database.spatial_extent import InvalidSpatialExtent
from joj.model.model_run_extent_schema import ModelRunExtentSchema
from joj.model.non_database.temporal_extent import InvalidTemporalExtent

from joj.utils.utils import find_by_id, KeyNotFound

# The prefix given to parameter name in html elements

PARAMETER_NAME_PREFIX = 'param'

# Message to show when the submission has failed
SUBMISSION_FAILED_MESSAGE = \
    "Failed to submit the model run, this may be because the cluster is down. Please try again later."

log = logging.getLogger(__name__)


class ModelRunController(BaseController):
    """Provides operations for model runs"""

    def __init__(self, user_service=UserService(), model_run_service=ModelRunService(),
                 dataset_service=DatasetService()):
        """Constructor
            Params:
                user_service: service to access user details
                model_run_service: service to access model runs
        """
        super(ModelRunController, self).__init__(user_service)
        self._model_run_service = model_run_service
        self._dataset_service = dataset_service

    def index(self):
        """
        Default controller providing access to the catalogue of user model runs
        :return: Rendered catalogue page
        """
        # all non-created runs
        c.model_runs = [model
                        for model in self._model_run_service.get_models_for_user(self.current_user)
                        if model.status.name != constants.MODEL_RUN_STATUS_CREATED]
        c.showing = "mine"
        return render("model_run/catalogue.html")

    def published(self):
        """
        Controller providing access to the catalogue of published model runs
        :return: Rendered catalogue page
        """
        c.model_runs = self._model_run_service.get_published_models()
        c.showing = "published"
        return render("model_run/catalogue.html")

    def publish(self, id):
        """
        Controller allowing existing model runs to be published
        :param id: ID of model run to publish
        :return: redirect to the page you came from
        """
        if request.POST:
            self._model_run_service.publish_model(self.current_user, id)
            came_from = request.params['came_from']
            if came_from == 'catalogue':
                redirect(url(controller='model_run', action='index'))
            elif came_from == 'summary':
                redirect(url(controller='model_run', action='summary', id=id))

    def summary(self, id):
        """
        Controller providing a detailed summary of a single model run
        :param id: the id of the model run to display
        :return: Rendered summary page of requested model run
        """
        c.model_run = self._model_run_service.get_model_by_id(self.current_user, id)
        return render("model_run/summary.html")

    @validate(schema=ModelRunCreateFirst(), form='create', post_only=False, on_get=False, prefix_error=False,
              auto_error_formatter=BaseController.error_formatter)
    def create(self):
        """
        Controller for creating a new run
        """

        scientific_configurations = self._model_run_service.get_scientific_configurations()

        values = dict(request.params)
        errors = None
        if request.POST:
            try:
                self._model_run_service.update_model_run(
                    self.current_user,
                    self.form_result['name'],
                    self.form_result['science_configuration'],
                    self.form_result['description'])
                redirect(url(controller='model_run', action='driving_data'))
            except NoResultFound:
                errors = {'science_configuration': 'Configuration is not recognised'}
            except DuplicateName:
                errors = {'name': 'Name can not be the same as another model run'}
        else:
            model = self._model_run_service.get_model_run_being_created_or_default(self.current_user)
            values['name'] = model.name
            values['science_configuration'] = model.science_configuration_id
            values['description'] = model.description

        c.scientific_configurations = scientific_configurations

        html = render('model_run/create.html')
        return htmlfill.render(
            html,
            defaults=values,
            errors=errors,
            auto_error_formatter=BaseController.error_formatter)

    def driving_data(self):
        """
        Select a driving data set
        """
        model_run = None
        try:
            model_run = \
                self._model_run_service.get_model_being_created_with_non_default_parameter_values(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before you can choose a driving data set")
            redirect(url(controller='model_run', action='create'))

        driving_datasets = self._dataset_service.get_driving_datasets()
        errors = {}

        if not request.POST:
            # Get all the driving data-sets and render the page
            if len(driving_datasets) == 0:
                abort_with_error("There are no driving datasets available - cannot create a new model run")
            driving_dataset_id = model_run.driving_dataset_id
            if driving_dataset_id is None:
                driving_dataset_id = driving_datasets[0].id
            values = {'driving_dataset': driving_dataset_id}
            c.driving_datasets = driving_datasets
            html = render('model_run/driving_data.html')
            return htmlfill.render(
                html,
                defaults=values,
                errors=errors,
                auto_error_formatter=BaseController.error_formatter)
        else:
            values = dict(request.params)

            # get the action to perform and remove it from the dictionary
            action = request.params.getone('submit')
            del values['submit']

            try:
                driving_dataset = find_by_id(driving_datasets, int(values['driving_dataset']))
            except (KeyNotFound, KeyError):
                html = render('model_run/driving_data.html')
                errors['driving_dataset'] = 'Driving data not recognised'
                return htmlfill.render(
                    html,
                    defaults=values,
                    errors=errors,
                    auto_error_formatter=BaseController.error_formatter)

            old_driving_dataset = None
            if model_run.driving_dataset_id is not None:
                old_driving_dataset = find_by_id(driving_datasets, model_run.driving_dataset_id)

            self._model_run_service.save_driving_dataset_for_new_model(
                driving_dataset,
                old_driving_dataset,
                self.current_user)

            if action == u'Next':
                redirect(url(controller='model_run', action='extents'))
            else:
                redirect(url(controller='model_run', action='create'))

    @validate(schema=ModelRunExtentSchema(), form='extents', post_only=False, on_get=False, prefix_error=False,
              auto_error_formatter=BaseController.error_formatter)
    def extents(self):
        """
        Specify the spatial and temporal extents of the model
        """

        # First we need to check that we are allowed to be on this page
        model_run = self.get_model_run_being_created_or_redirect(self._model_run_service)
        c.dataset = driving_data = model_run.driving_dataset
        if driving_data is None:
            helpers.error_flash(u"You must select a driving data set before you can set the extents")
            redirect(url(controller='model_run', action='driving_data'))
        errors = {}

        # Get the driving data extents so we can validate
        spatial_extent = self._dataset_service.get_spatial_extent(driving_data.id)
        temporal_extent = self._dataset_service.get_temporal_extent(driving_data.id)

        def _validate_extents(_lat_n, _lat_s, _lon_e, _lon_w, _run_end, _run_start):
            """
            Validate extents and set errors if needed
            :param _lat_n:
            :param _lat_s:
            :param _lon_e:
            :param _lon_w:
            :param _run_end:
            :param _run_start:
            """
            try:
                spatial_extent.set_lat(_lat_n, _lat_s)
            except InvalidSpatialExtent as e:
                errors['lat_n'] = e.message
            try:
                spatial_extent.set_lon(_lon_w, _lon_e)
            except InvalidSpatialExtent as e:
                errors['lon_w'] = e.message

            # We need to check the same thing with the values for temporal extent
            if _run_start is not None:
                try:
                    temporal_extent.set_start(_run_start)
                except InvalidTemporalExtent as e:
                    errors['start_date'] = e.message
            if _run_end is not None:
                try:
                    temporal_extent.set_end(_run_end)
                except InvalidTemporalExtent as e:
                    errors['end_date'] = e.message

        if not request.POST:
            # Get the extents from the database if already set or default them to dataset boundaries if not
            lat_s, lat_n = model_run.get_parameter_value(constants.JULES_PARAM_LAT_BOUNDS) \
                or (driving_data.boundary_lat_south, driving_data.boundary_lat_north)
            lon_w, lon_e = model_run.get_parameter_value(constants.JULES_PARAM_LON_BOUNDS) \
                or (driving_data.boundary_lon_west, driving_data.boundary_lon_east)
            run_start = model_run.get_parameter_value(constants.JULES_PARAM_RUN_START) \
                or driving_data.time_start
            run_end = model_run.get_parameter_value(constants.JULES_PARAM_RUN_END) \
                or driving_data.time_end

            # Set the values to display in the form
            values = {
                'lat_n': lat_n,
                'lat_s': lat_s,
                'lon_w': lon_w,
                'lon_e': lon_e,
                'start_date': run_start.date(),
                'start_time': run_start.time(),
                'end_date': run_end.date(),
                'end_time': run_end.time()
            }

            # We need to check that saved values for user selected spatial extent are consistent with the chosen
            # driving data (e.g. in case the user has gone back and changed their driving data).
            _validate_extents(lat_n, lat_s, lon_e, lon_w, run_end, run_start)

            # Finally in our GET we render the page with any errors and values we have
            return htmlfill.render(
                render('model_run/extents.html'),
                defaults=values,
                errors=errors,
                auto_error_formatter=BaseController.error_formatter)

        # This is a POST
        else:
            values = self.form_result

            run_start = datetime.datetime.combine(values['start_date'], values['start_time'])
            run_end = datetime.datetime.combine(values['end_date'], values['end_time'])

            _validate_extents(values['lat_n'], values['lat_s'], values['lon_e'], values['lon_w'], run_end, run_start)

            if len(errors) > 0:
                return htmlfill.render(
                    render('model_run/extents.html'),
                    defaults=values,
                    errors=errors,
                    auto_error_formatter=BaseController.error_formatter)

            # Save to DB
            self._model_run_service.save_parameter(constants.JULES_PARAM_LATLON_REGION,
                                                   True, self.current_user)
            self._model_run_service.save_parameter(constants.JULES_PARAM_USE_SUBGRID,
                                                   True, self.current_user)
            self._model_run_service.save_parameter(constants.JULES_PARAM_LAT_BOUNDS,
                                                   spatial_extent.get_lat_bounds(), self.current_user)
            self._model_run_service.save_parameter(constants.JULES_PARAM_LON_BOUNDS,
                                                   spatial_extent.get_lon_bounds(), self.current_user)
            self._model_run_service.save_parameter(constants.JULES_PARAM_RUN_START,
                                                   run_start, self.current_user)
            self._model_run_service.save_parameter(constants.JULES_PARAM_RUN_END,
                                                   run_end, self.current_user)
            # get the action to perform
            try:
                action = values['submit']
            except KeyError:
                action = None
            if action == u'Next':
                redirect(url(controller='model_run', action='parameters'))
            else:
                redirect(url(controller='model_run', action='driving_data'))

    def parameters(self):
        """
        Define parameters for the current new run being created
        """

        try:
            c.parameters = self._model_run_service.get_parameters_for_model_being_created(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before any parameters can be set")
            redirect(url(controller='model_run', action='create'))

        if not request.POST:
            html = render('model_run/parameters.html')
            parameter_values = {}
            for parameter in c.parameters:
                if parameter.parameter_values:
                    parameter_values[PARAMETER_NAME_PREFIX + str(parameter.id)] = parameter.parameter_values[0].value
            return htmlfill.render(
                html,
                defaults=parameter_values,
                errors={},
                auto_error_formatter=BaseController.error_formatter
            )
        else:

            # get the action to perform and remove it from the dictionary
            action = request.params.getone('submit')

            if action == u'Next':
                redirect(url(controller='model_run', action='submit'))
            else:
                redirect(url(controller='model_run', action='extents'))

    def submit(self):
        """
        Page to submit the model un
        """

        try:
            c.model = \
                self._model_run_service.get_model_being_created_with_non_default_parameter_values(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before submitting the model run")
            redirect(url(controller='model_run', action='create'))

        if request.POST:
            if request.params.getone('submit') == u'Submit':
                status, message = self._model_run_service.submit_model_run(self.current_user)
                if status.name == constants.MODEL_RUN_STATUS_PENDING:
                    helpers.success_flash(message)
                else:
                    helpers.error_flash(message)

                redirect(url(controller='model_run', action='index'))
            else:
                redirect(url(controller='model_run', action='parameters'))

        return render('model_run/submit.html')
