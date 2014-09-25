"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
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
from joj.utils.general_controller_helper import must_be_admin, put_errors_in_table_on_line, remove_deleted_keys, \
    show_error_if_thredds_down
from joj.services.model_run_service import ModelRunService
from joj.model import DrivingDataset
from joj.services.land_cover_service import LandCoverService
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams
from joj.model.schemas.driving_dataset_edit import DrivingDatasetEdit
from joj.model.non_database.datetime_period_validator import DatetimePeriodValidator
from joj.utils import constants
from joj.model.non_database.driving_data_file_location_validator import DrivingDataFileLocationValidator
from joj.services.general import ServiceException
from joj.model.non_database.spatial_extent import SpatialExtent, InvalidSpatialExtent

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

        c.driving_data_sets = self._dataset_service.get_driving_datasets(self.current_user)
        return render('driving_data/list.html')

    @must_be_admin
    @show_error_if_thredds_down
    def edit(self, id=None):
        """
        Allow an admin to edit a driving data se
        :param id: id of the data ste or none for new dataset
        :return: html to render
        """
        errors = {}

        c.namelist = {}
        c.region_error = []
        c.driving_var_errors = []
        c.param_errors = []
        c.lat_lon_error = None

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
            remove_deleted_keys(values, 'mask_count', 'region', ['id', 'category', 'name', 'path'])

            schema = DrivingDatasetEdit()
            results = {}
            service_exception = False
            try:
                results = schema.to_python(values, c)
            except Invalid, e:
                errors.update(e.unpack_errors())
            except ServiceException as ex:
                helpers.error_flash("Could not save: %s" % ex.message)
                service_exception = True

            date_period_validator = DatetimePeriodValidator(errors)
            results["driving_data_start"], results["driving_data_end"] = \
                date_period_validator.get_valid_start_end_datetimes("driving_data_start", "driving_data_end", values)

            try:
                lat_north = float(values['boundary_lat_north'])
                lat_south = float(values['boundary_lat_south'])
                lon_east = float(values['boundary_lon_east'])
                lon_west = float(values['boundary_lon_west'])
                SpatialExtent(lat_north, lat_south, lon_west, lon_east)
            except InvalidSpatialExtent as ex:
                c.lat_lon_error = ex.message
                service_exception = True
            except (ValueError, KeyError):
                # Not float value Handled in schema validation
                pass

            validator = DrivingDataFileLocationValidator(errors, self._dataset_service.get_dataset_types_dictionary())
            locations = validator.get_file_locations(results)

            if len(errors) == 0 and not service_exception:
                self._dataset_service.create_driving_dataset(
                    id,
                    results,
                    locations,
                    self._model_run_service,
                    self._landcover_service)
                redirect(url(controller="driving_data", acion="index"))

            c.region_error = put_errors_in_table_on_line(errors, "region", "path")
            c.driving_var_errors = put_errors_in_table_on_line(errors, constants.PREFIX_FOR_DRIVING_VARS, "interps")
            c.param_errors = put_errors_in_table_on_line(errors, "param", "value")

            values["param_names"] = []
            for parameter in all_parameters:
                for parameter_index in range(int(values["params_count"])):
                    parameter_id = values.get("param-{}.id".format(str(parameter_index)))
                    if str(parameter.id) == parameter_id:
                        values["param_names"].append("{}::{}".format(parameter.namelist.name, parameter.name))
            helpers.error_flash("Some of the values entered below are incorrect, please correct them")
        else:
            if id is None:
                driving_dataset = DrivingDataset()
                driving_dataset.is_restricted_to_admins = True
                c.regions = []

            else:
                driving_dataset = self._dataset_service.get_driving_dataset_by_id(id)
                c.regions = self._landcover_service.get_land_cover_regions(id)

            jules_params = DrivingDatasetJulesParams()
            jules_params.set_from(driving_dataset, c.regions)

            values = jules_params.create_values_dict(c.namelist)

        c.masks = int(values['mask_count'])
        c.mask_can_be_deleted = []
        for mask_index in range(c.masks):
            mask_id = values['region-{}.id'.format(mask_index)]
            c.mask_can_be_deleted.append(mask_id is None or mask_id == "")

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
