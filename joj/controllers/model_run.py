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
from joj.services.model_run_service import ModelRunService

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
        Default controller providing access to the catalogue of model_runs
        :return: Rendered catalogue page
        """
        c.published_models = self._model_run_service.get_published_models()
        c.user_models = self._model_run_service.get_models_for_user(self.current_user)
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
                self._model_run_service.define_model_run(self.form_result['name'], self.form_result['code_version'])

                redirect(url(controller='model_run', action='parameters'))
            except Invalid, e:
                    values = values,
                    errors = variabledecode.variable_encode(
                        e.unpack_errors() or {},
                        add_repetitions=False
                    )
            except NoResultFound:
                errors = {'code_version': 'Code version is not recognised'}

        c.all_models = self._model_run_service.get_model_being_created(self.current_user)
        c.code_versions = [Option(version.id, version.name) for version in versions]

        html = render('model_run/create.html')
        return htmlfill.render(html, defaults=values, errors=errors, auto_error_formatter=self.error_formatter)

    def parameters(self):
        """
        Define parameters for the current new run being created
        """

        return render('model_run/parameters.html')