# header

import logging
from formencode import htmlfill
from formencode import variabledecode
from formencode.validators import Invalid

from pylons import url

from pylons.decorators import validate

from sqlalchemy.orm.exc import NoResultFound

from webhelpers.html.tags import Option

from joj.services.user import UserService
from joj.lib.base import BaseController, c, request, render, redirect
from joj.model.model_run_create_form import ModelRunCreateFirst
from joj.model.model_run_create_parameters import ModelRunCreateParameters
from joj.model import ModelRun
from joj.services.model_run_service import ModelRunService
from joj.lib import helpers

# The prefix given to parameter name in html elements
PARAMETER_NAME_PREFIX = 'param'

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
                self._model_run_service.update_model_run(self.form_result['name'], self.form_result['code_version'])

                redirect(url(controller='model_run', action='parameters'))
            except NoResultFound:
                errors = {'code_version': 'Code version is not recognised'}
        else:
            model = self._model_run_service.get_model_run_being_created_or_default()
            values['name'] = model.name
            values['code_version'] = model.code_version_id

        c.all_models = self._model_run_service.get_model_being_created(self.current_user)
        c.code_versions = [Option(version.id, version.name) for version in versions]

        html = render('model_run/create.html')
        return htmlfill.render(html, defaults=values, errors=errors, auto_error_formatter=self.error_formatter)

    def parameters(self):
        """
        Define parameters for the current new run being created
        """

        try:
            c.parameters = self._model_run_service.get_defining_model_with_parameters()
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

            self._model_run_service.store_parameter_values(parameters)

            if action == u'Next':
                redirect(url(controller='model_run', action='summary'))
            else:
                redirect(url(controller='model_run', action='create'))

