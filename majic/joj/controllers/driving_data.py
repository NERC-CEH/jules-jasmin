"""
# header
"""
import logging
from formencode.validators import Invalid
from formencode import variabledecode
from pylons.controllers.util import redirect
from pylons import tmpl_context as c, url
from formencode import htmlfill

from joj.lib.base import BaseController, request, render, helpers
from joj.services.user import UserService
from joj.services.dataset import DatasetService
from joj.utils.general_controller_helper import must_be_admin, put_errors_in_table_on_line, remove_deleted_keys
from joj.services.model_run_service import ModelRunService
from joj.model import DrivingDataset
from joj.services.land_cover_service import LandCoverService
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams
from joj.model.schemas.driving_dataset_edit import DrivingDatasetEdit
from joj.model.non_database.datetime_period_validator import DatetimePeriodValidator
from joj.utils import constants
from joj.model.non_database.driving_data_file_location_validator import DrivingDataFileLocationValidator
from joj.services.general import ServiceException

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

    # noinspection PyArgumentList
    @must_be_admin
    def index(self):
        """
        Allow admins to list the driving data sets
        :return: html to render
        """

        c.driving_data_sets = self._dataset_service.get_driving_datasets()
        return render('driving_data/list.html')

    # noinspection PyArgumentList
    @must_be_admin
    def edit(self, id=None):
        """
        Allow an admin to edit a driving data se
        :param id: id of the data ste or none for new dataset
        :return: html to render
        """
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
            remove_deleted_keys(
                values,
                'drive_nvars',
                constants.PREFIX_FOR_DRIVING_VARS,
                ['vars', 'names', 'templates', 'interps'])
            remove_deleted_keys(values, 'params_count', 'param', ['id', 'value'])

            schema = DrivingDatasetEdit()
            results = {}
            service_exception = False
            try:
                results = schema.to_python(values, c)
                locations = DrivingDataFileLocationValidator(errors).get_file_locations(results)
            except Invalid, e:
                errors.update(e.unpack_errors())
            except ServiceException as ex:
                helpers.error_flash("Could not save: %s" % ex.message)
                service_exception = True

            date_period_validator = DatetimePeriodValidator(errors)
            results["driving_data_start"], results["driving_data_end"] = \
                date_period_validator.get_valid_start_end_datetimes("driving_data_start", "driving_data_end", values)

            if len(errors) == 0 and not service_exception:
                self._dataset_service.create_driving_dataset(
                    id,
                    results,
                    self._model_run_service,
                    self._landcover_service)
                redirect(url(controller="driving_data", acion="index"))

            put_errors_in_table_on_line(errors, "region", "path")
            put_errors_in_table_on_line(errors, constants.PREFIX_FOR_DRIVING_VARS, "interps")
            put_errors_in_table_on_line(errors, "param", "value")

            values["param_names"] = []
            for parameter in all_parameters:
                for parameter_index in range(int(values["params_count"])):
                    parameter_id = values.get("param-{}.id".format(str(parameter_index)))
                    if str(parameter.id) == parameter_id:
                        values["param_names"].append("{}::{}".format(parameter.namelist.name, parameter.name))

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
        try:
            c.nvar = int(values['drive_nvars'])
        except (ValueError, KeyError):
            c.nvar = 0

        c.param_names = values["param_names"]
        html = render('driving_data/edit.html')

        return htmlfill.render(
            html,
            defaults=values,
            errors=variabledecode.variable_encode(errors, add_repetitions=False),
            auto_error_formatter=BaseController.error_formatter,
            prefix_error=False)
