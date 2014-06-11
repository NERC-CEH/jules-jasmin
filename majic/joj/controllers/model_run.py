# header

import logging
from formencode import htmlfill
from formencode.validators import Invalid

from pylons import url

from pylons.decorators import validate

from sqlalchemy.orm.exc import NoResultFound

from webhelpers.html.tags import Option

from joj.services.user import UserService
from joj.lib.base import BaseController, c, request, render, redirect
from joj.model.model_run_create_form import ModelRunCreateFirst
from joj.model.model_run_create_parameters import ModelRunCreateParameters
from joj.services.model_run_service import ModelRunService
from joj.lib import helpers
from joj.utils import constants

# The prefix given to parameter name in html elements
PARAMETER_NAME_PREFIX = 'param'

#Message to show when the submission has failed
SUBMISSION_FAILED_MESSAGE = \
    "Failed to submit the model run, this may be because the cluster is down. Please try again later."

log = logging.getLogger(__name__)


class ModelRunController(BaseController):
    """Provides operations for model runs"""

    def __init__(self, user_service=UserService(), model_run_service=ModelRunService()):
        """Constructor
            Params:
                user_service: service to access user details
                model_run_service: service to access model runs
        """
        super(ModelRunController, self).__init__(user_service)
        self._model_run_service = model_run_service

    def index(self):
        """
        Default controller providing access to the catalogue of user model runs
        :return: Rendered catalogue page
        """
        c.model_runs = self._model_run_service.get_models_for_user(self.current_user)
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

    def summary(self, id):
        """
        Controller providing a detailed summary of a single model run
        :param id: the id of the model run to display
        :return: Rendered summary page of requested model run
        """
        c.model_run = self._model_run_service.get_model_by_id(self.current_user, id)
        return render("model_run/summary.html")

    @validate(schema=ModelRunCreateFirst(), form='create', post_only=False, on_get=False, prefix_error=False)
    def create(self):
        """
        Controller for creating a new run
        """

        versions = self._model_run_service.get_code_versions()

        values = dict(request.params)
        errors = None
        if request.POST:
            try:
                self._model_run_service.update_model_run(
                    self.current_user,
                    self.form_result['name'],
                    self.form_result['code_version'],
                    self.form_result['description'])
                redirect(url(controller='model_run', action='parameters'))
            except NoResultFound:
                errors = {'code_version': 'Code version is not recognised'}
        else:
            model = self._model_run_service.get_model_run_being_created_or_default(self.current_user)
            values['name'] = model.name
            values['code_version'] = model.code_version_id
            values['description'] = model.description

        c.all_models = self._model_run_service.get_model_being_created(self.current_user)
        c.code_versions = [Option(version.id, version.name) for version in versions]

        html = render('model_run/create.html')
        return htmlfill.render(html, defaults=values, errors=errors, auto_error_formatter=self.error_formatter)

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
                errors={}
            )
        else:
            schema = ModelRunCreateParameters(c.parameters)
            values = dict(request.params)

            #get the action to perform and remove it from the dictionary
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
                    errors=c.form_errors
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
