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

from joj.model.model_run_extent_schema import ModelRunExtentSchema

from joj.utils.utils import find_by_id, KeyNotFound
from joj.utils import output_controller_helper
from joj.utils import extents_controller_helper
from joj.utils.output_controller_helper import JULES_MONTHLY_PERIOD, JULES_DAILY_PERIOD, JULES_YEARLY_PERIOD

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

        if not request.POST:
            extents_controller_helper.add_selected_extents_to_template_context(c, model_run, driving_data)

            # Set the values to display in the form
            values = {
                'lat_n': c.lat_n,
                'lat_s': c.lat_s,
                'lon_w': c.lon_w,
                'lon_e': c.lon_e,
                'start_date': c.run_start.date(),
                'end_date': c.run_end.date()
            }

            # We need to check that saved values for user selected spatial extent are consistent with the chosen
            # driving data (e.g. in case the user has gone back and changed their driving data).
            extents_controller_helper.validate_spatial_extents(spatial_extent, errors,
                                                               c.lat_n, c.lat_s, c.lon_e, c.lon_w)
            extents_controller_helper.validate_temporal_extents(temporal_extent, errors, c.run_start, c.run_end)

            # Finally in our GET we render the page with any errors and values we have
            return htmlfill.render(
                render('model_run/extents.html'),
                defaults=values,
                errors=errors,
                auto_error_formatter=BaseController.error_formatter)

        # This is a POST
        else:
            values = self.form_result

            # Set the start and end times to be the times at which the driving data starts and ends.
            run_start = datetime.datetime.combine(values['start_date'], driving_data.time_start.time())
            run_end = datetime.datetime.combine(values['end_date'], driving_data.time_end.time())

            extents_controller_helper.validate_spatial_extents(spatial_extent, errors,
                                                               values['lat_n'], values['lat_s'],
                                                               values['lon_e'], values['lon_w'])
            extents_controller_helper.validate_temporal_extents(temporal_extent, errors, run_start, run_end)

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
                redirect(url(controller='model_run', action='output'))
            else:
                redirect(url(controller='model_run', action='driving_data'))

    def output(self):
        """
        Select output parameters
        """
        # First we need to check that we are allowed to be on this page
        model_run = self.get_model_run_being_created_or_redirect(self._model_run_service)

        if not request.POST:
            # We need to not show the output variables which are dependent on JULES_MODEL_LEVELS::nsmax if nsmax is 0
            jules_param_nsmax = model_run.get_python_parameter_value(constants.JULES_PARAM_NSMAX)
            c.output_variables = self._model_run_service.get_output_variables(
                include_depends_on_nsmax=jules_param_nsmax > 0)

            # We want to pass the renderer a list of which output variables are already selected and for which time
            # periods so that we can render these onto the page as selected
            output_controller_helper.add_selected_outputs_to_template_context(c, model_run)

            return render("model_run/output.html")
        else:
            values = dict(request.params)

            # Identify the requested output variables and save the appropriate parameters
            output_variable_groups = output_controller_helper.create_output_variable_groups(values,
                                                                                            self._model_run_service,
                                                                                            model_run)

            self._model_run_service.set_output_variables_for_model_being_created(output_variable_groups,
                                                                                 self.current_user)
            # Get the action to perform
            try:
                action = values['submit']
            except KeyError:
                action = None
            if action == u'Next':
                redirect(url(controller='model_run', action='submit'))
            else:
                redirect(url(controller='model_run', action='extents'))

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
                redirect(url(controller='model_run', action='output'))

    def submit(self):
        """
        Page to submit the model un
        """
        model_run = None
        try:
            model_run = \
                self._model_run_service.get_model_being_created_with_non_default_parameter_values(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before submitting the model run")
            redirect(url(controller='model_run', action='create'))

        if not request.POST:

            c.model_run = model_run
            c.science_config = self._model_run_service.get_science_configuration_by_id(
                model_run.science_configuration_id)

            extents_controller_helper.add_selected_extents_to_template_context(c, model_run, None)

            c.driving_data_name = model_run.driving_dataset.name

            selected_vars = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_VAR)
            selected_output_periods = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PERIOD)

            hourly = []
            daily = []
            monthly = []
            yearly = []

            outputs = {}

            # Each group contains one output variable and one output period
            for selected_var in selected_vars:
                var_name = selected_var.get_value_as_python()
                if var_name not in outputs:
                    outputs[var_name] = []
                for output_period in selected_output_periods:
                    if output_period.group_id == selected_var.group_id:
                        period = output_period.get_value_as_python()
                        if period == JULES_YEARLY_PERIOD:
                            outputs[var_name].append('Yearly')
                        elif period == JULES_MONTHLY_PERIOD:
                            outputs[var_name].append('Monthly')
                        elif period == JULES_DAILY_PERIOD:
                            outputs[var_name].append('Daily')
                        else:
                            outputs[var_name].append('Hourly')
            c.outputs = []
            for output in outputs:
                c.outputs.append(output + ' - ' + ', '.join(map(str, outputs[output])) + '')

            if len(hourly) == 0:
                c.hourly = 'None'
            else:
                c.hourly = ', '.join(map(str, hourly))
            if len(daily) == 0:
                c.daily = 'None'
            else:
                c.daily = ', '.join(map(str, daily))
            if len(monthly) == 0:
                c.monthly = 'None'
            else:
                c.monthly = ', '.join(map(str, monthly))
            if len(yearly) == 0:
                c.yearly = 'None'
            else:
                c.yearly = ', '.join(map(str, yearly))

        else:
            if request.params.getone('submit') == u'Submit':
                status, message = self._model_run_service.submit_model_run(self.current_user)
                if status.name == constants.MODEL_RUN_STATUS_SUBMITTED:
                    helpers.success_flash(message)
                else:
                    helpers.error_flash(message)

                redirect(url(controller='model_run', action='index'))
            else:
                redirect(url(controller='model_run', action='output'))

        return render('model_run/submit.html')
