"""
header
"""

import logging
from formencode import htmlfill
from formencode.validators import Invalid

from pylons import url

from pylons.decorators import validate

from sqlalchemy.orm.exc import NoResultFound

from joj.services.user import UserService
from joj.lib.base import BaseController, c, request, render, redirect
from joj.model.model_run_create_form import ModelRunCreateFirst
from joj.model.model_run_create_parameters import ModelRunCreateParameters
from joj.services.model_run_service import ModelRunService, DuplicateName
from joj.services.dataset import DatasetService
from joj.lib import helpers
from joj.utils import constants
from joj.utils.error import abort_with_error

# The prefix given to parameter name in html elements
from joj.model import session_scope, Session

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
            model_run = self._model_run_service.get_model_being_created_with_non_default_parameter_values(self.current_user)
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
            try:
                driving_dataset = [driving_dataset for driving_dataset
                                   in driving_datasets if driving_dataset.id == int(values['driving_dataset'])][0]
            except (IndexError, KeyError):
                html = render('model_run/driving_data.html')
                errors['driving_dataset'] = 'Driving data not recognised'
                return htmlfill.render(
                    html,
                    defaults=values,
                    errors=errors,
                    auto_error_formatter=BaseController.error_formatter)
            self._model_run_service.save_driving_dataset_for_new_model(driving_dataset, self.current_user)

            if values['submit'] == u'Next':
                redirect(url(controller='model_run', action='parameters'))
            else:
                redirect(url(controller='model_run', action='create'))

    def extents(self):
        """
        Specify the spatial and temporal extents of the model
        """

        if not request.POST:
            pass
        else:
            pass

        return "Specify Spatial and Temporal Extents"


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
            schema = ModelRunCreateParameters(c.parameters)
            values = dict(request.params)

            # get the action to perform and remove it from the dictionary
            action = request.params.getone('submit')
            del values['submit']

            try:
                c.form_result = schema.to_python(values)
            except Invalid, error:
                c.form_result = error.value
                c.form_errors = error.error_dict or {}
                html = render('model_run/parameters.html')
                return htmlfill.render(
                    html,
                    defaults=c.form_result,
                    errors=c.form_errors,
                    auto_error_formatter=BaseController.error_formatter
                )

            parameters = {}
            for param_name, param_value in c.form_result.iteritems():
                if param_name.startswith(PARAMETER_NAME_PREFIX):
                    parameters[param_name.replace(PARAMETER_NAME_PREFIX, '')] = param_value

            self._model_run_service.store_parameter_values(parameters, self.current_user)

            if action == u'Next':
                redirect(url(controller='model_run', action='submit'))
            else:
                redirect(url(controller='model_run', action='create'))

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
