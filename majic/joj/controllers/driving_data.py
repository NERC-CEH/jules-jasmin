"""
# header
"""
import logging
from formencode.validators import Invalid
from pylons.controllers.util import redirect
from pylons.decorators import validate
from sqlalchemy.orm.exc import NoResultFound
from pylons import tmpl_context as c, url
from formencode import htmlfill
import formencode

from joj.crowd.client import ClientException
from joj.lib.base import BaseController, request, render
from joj.lib import helpers
from joj.services.user import UserService
from joj.services.dataset import DatasetService
from joj.model.create_new_user_form import CreateUserForm, UpdateUserForm
from joj.utils import constants, utils
from joj.utils.general_controller_helper import must_be_admin
from joj.services.model_run_service import ModelRunService
from joj.services.account_request_service import AccountRequestService
from joj.services.general import ServiceException
from joj.model import DrivingDataset
from joj.services.land_cover_service import LandCoverService
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams
from joj.model.schemas.driving_dataset_edit import DrivingDatasetEdit
from joj.model.non_database.datetime_period_validator import DatetimePeriodValidator

log = logging.getLogger(__name__)


class DrivingDataController(BaseController):
    """Provides operations for driving data page actions"""

    def __init__(self,
                 user_service=UserService(),
                 dataset_service=DatasetService(),
                 landcover_service=LandCoverService(),
                 model_run_service=ModelRunService()):
        """
        Constructor for the user controller, takes in any services required
        :param user_service: User service to use within the controller
        :param landcover_service: Land cover service to use
        :return: nothing
        """
        super(DrivingDataController, self).__init__(user_service)

        self._model_run_service = model_run_service
        self._dataset_service = dataset_service
        self._landcover_service = landcover_service

    @must_be_admin
    def index(self):
        """
        Allow admins to list the driving data sets
        :return: html to render
        """

        c.driving_data_sets = self._dataset_service.get_driving_datasets()
        return render('driving_data/list.html')

    @must_be_admin
    def edit(self, id=None):
        """
        Allow an admin to edit a driving data se
        :param id: id of the data ste or none for new dataset
        :return: html to render
        """

        values = {}
        errors = {}

        c.namelist = {}
        all_parameters = self._model_run_service.get_parameters_for_default_code_version()
        for parameter in all_parameters:
            if parameter.namelist.name not in c.namelist:
                c.namelist[parameter.namelist.name] = {}
            c.namelist[parameter.namelist.name][parameter.id] = parameter.name

        c.driving_dataset_id = id
        if request.POST:
            values = dict(request.params)

            schema = DrivingDatasetEdit()
            result = None
            try:
                result = schema.to_python(dict(request.params), c)
            except Invalid, e:
                errors.update(e.unpack_errors())

            date_period_validator = DatetimePeriodValidator(errors)
            date_period_validator.get_valid_start_end_datetimes("driving_data_start", "driving_data_end", values)

            if len(errors) == 0:
                driving_dataset_jules_params = DrivingDatasetJulesParams()
                driving_dataset = driving_dataset_jules_params.create_driving_dataset_from_dict(values)
                self._dataset_service.create_driving_dataset(driving_dataset)
                redirect(url(controller="driving_data", acion="index"))
            values["param_names"] = []
        else:
            if id is None:
                driving_dataset = DrivingDataset()
                c.regions = []

            else:
                driving_dataset = self._dataset_service.get_driving_dataset_by_id(id)
                c.regions = self._landcover_service.get_land_cover_regions(id)

            jules_params = DrivingDatasetJulesParams()
            jules_params.set_from(driving_dataset, c.regions)

            values = jules_params.create_values_dict(c.namelist)

        c.masks = int(values['mask_count'])
        c.nvar = int(values['drive_nvars'])
        c.param_names = values["param_names"]
        html = render('driving_data/edit.html')

        return htmlfill.render(
            html,
            defaults=values,
            errors=errors,
            auto_error_formatter=BaseController.error_formatter)
