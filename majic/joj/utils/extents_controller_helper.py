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
import datetime
from dateutil.relativedelta import relativedelta

from pylons import config

from joj.model.non_database.spatial_extent import InvalidSpatialExtent, SpatialExtent
from joj.model.non_database.temporal_extent import InvalidTemporalExtent, TemporalExtent
from joj.utils import constants
from joj.services.dataset import DatasetService
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.utils.spinup_helper import SpinupHelper


class ExtentsControllerHelper(object):
    """
    Helper class for the extents controller
    """

    def __init__(self,
                 dataset_service=DatasetService(),
                 dap_client_factory=DapClientFactory(),
                 spinup_helper=SpinupHelper()):
        self.dataset_service = dataset_service
        self.dap_client_factory = dap_client_factory
        self.spinup_helper = spinup_helper

    def create_values_dict_from_database(self, model_run, driving_data):
        """
        Create a dictionary of values corresponding to the form elements on the page and the values they should have,
        based on either the values in the database or on appropriate defaults
        :param model_run: The model run currently being used
        :param driving_data: The driving data selected for the model_run
        :return: Dictionary of form input names -> values
        """

        values = {}
        is_user_data = self._is_user_driving_data(driving_data)

        # Defaults to true unless it's user uploaded single site data
        singlecell = model_run.is_for_single_cell()
        if singlecell is None:
            singlecell = is_user_data
        values['site'] = 'single' if singlecell else 'multi'

        values['lat'], values['lon'] = self._get_lat_lon(model_run, is_user_data)

        values['lat_s'], values['lat_n'] = self._get_lat_bounds(model_run, driving_data, is_user_data)
        values['lon_w'], values['lon_e'] = self._get_lon_bounds(model_run, driving_data, is_user_data)

        point_data = model_run.get_python_parameter_value(constants.JULES_PARAM_SWITCHES_L_POINT_DATA) or False
        if point_data:
            values['point_data'] = 1

        values['start_date'] = self._get_start_datetime(model_run, driving_data, is_user_data).date()
        values['end_date'] = self._get_end_datetime(model_run, driving_data, is_user_data).date()

        return values

    def _get_lat_lon(self, model_run, is_user_data):
        latlon = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE, is_list=True)
        return latlon if latlon is not None else self._get_default_lat_lon(model_run, is_user_data)

    def _get_default_lat_lon(self, model_run, is_user_data):
        if is_user_data:
            return model_run.driving_data_lat, model_run.driving_data_lon
        else:
            return None, None

    def _get_lat_bounds(self, model_run, driving_data, is_user_data):
        lat_bounds = model_run.get_python_parameter_value(constants.JULES_PARAM_LAT_BOUNDS, is_list=True)
        return lat_bounds if lat_bounds is not None else self._get_default_lat_bounds(model_run, driving_data,
                                                                                      is_user_data)

    def _get_default_lat_bounds(self, model_run, driving_data, is_user_data):
        if is_user_data:
            return model_run.driving_data_lat, model_run.driving_data_lat
        else:
            return driving_data.boundary_lat_south, driving_data.boundary_lat_north

    def _get_lon_bounds(self, model_run, driving_data, is_user_data):
        lon_bounds = model_run.get_python_parameter_value(constants.JULES_PARAM_LON_BOUNDS, is_list=True)
        return lon_bounds if lon_bounds is not None else self._get_default_lon_bounds(model_run, driving_data,
                                                                                      is_user_data)

    def _get_default_lon_bounds(self, model_run, driving_data, is_user_data):
        if is_user_data:
            return model_run.driving_data_lon, model_run.driving_data_lon
        else:
            return (driving_data.boundary_lon_west, driving_data.boundary_lon_east)

    def _get_start_datetime(self, model_run, driving_data, is_user_data):
        start = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_START)
        return start if start is not None else self._get_acceptable_start_datetime(model_run, driving_data,
                                                                                   is_user_data)

    def _get_end_datetime(self, model_run, driving_data, is_user_data):
        end = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_END)
        if end is not None:
            return end
        else:
            acceptable_end = self._get_acceptable_end_datetime(model_run, driving_data, is_user_data)
            default_start = self._get_acceptable_start_datetime(model_run, driving_data, is_user_data)
            max_default_end = default_start + relativedelta(years=10)
            default_end = min(max_default_end, acceptable_end)
            return default_end

    def _get_acceptable_start_datetime(self, model_run, driving_data, is_user_data):
        """
        Get the earliest acceptable run start time - taking into account the needs of the various
        interpolation flags to have spare driving data points at the beginning and / or end of the run
        :param model_run: The model run being used.
        :return:
        """

        if is_user_data:
            start_datetime = model_run.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_START)
        else:
            start_datetime = driving_data.time_start

        delta = self._get_delta_for_interpolation_flags(model_run, constants.INTERPS_EXTRA_STEPS_RUN_START)
        return start_datetime + delta

    def _get_acceptable_end_datetime(self, model_run, driving_data, is_user_data):
        """
        Get the latest acceptable run end time - taking into account the needs of the various
        interpolation flags to have spare driving data points at the beginning and / or end of the run
        :param model_run: The model run being used.
        :return:
        """

        if is_user_data:
            end_datetime = model_run.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_END)
        else:
            end_datetime = driving_data.time_end

        delta = self._get_delta_for_interpolation_flags(model_run, constants.INTERPS_EXTRA_STEPS_RUN_END)
        return end_datetime - delta

    def _get_delta_for_interpolation_flags(self, model_run, interpolation_dict):
        period = model_run.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_PERIOD)
        interps = model_run.get_python_parameter_value(constants.JULES_PARAM_DRIVE_INTERP, is_list=True)
        extra_time = []
        for interp in interps:
            if interp in interpolation_dict:
                extra_time.append(interpolation_dict[interp])
        if len(extra_time) > 0:
            n_steps = max(extra_time)
        else:
            n_steps = 0
        delta = datetime.timedelta(seconds=(period * n_steps))
        return delta

    def set_template_context_fields(self, tmpl_context, model_run, driving_data):
        """
        Add any required values to the template context object
        :param tmpl_context: Template context object
        :param model_run: The model run currently being used
        :param driving_data: The currently selected driving data
        :return:
        """
        is_user_data = self._is_user_driving_data(driving_data)
        tmpl_context.boundary_lat_s, tmpl_context.boundary_lat_n = self._get_default_lat_bounds(model_run,
                                                                                                driving_data,
                                                                                                is_user_data)
        tmpl_context.boundary_lon_w, tmpl_context.boundary_lon_e = self._get_default_lon_bounds(model_run,
                                                                                                driving_data,
                                                                                                is_user_data)
        tmpl_context.start_date = self._get_acceptable_start_datetime(model_run, driving_data, is_user_data).date()
        tmpl_context.end_date = self._get_acceptable_end_datetime(model_run, driving_data, is_user_data).date()

    def save_extents_against_model_run(self, values, driving_data, model_run, spinup_duration, parameter_service, user):
        """
        Save spatial and temporal extents against the model run currently being created
        :param values: The extents page POST values
        :param driving_data: Chosen driving data
        :param model_run: The model run currently being used
        :param spinup_duration: Spinup duration in years
        :param parameter_service: Model run service to use
        :param user: Currently logged in user
        :return: Nothing
        """
        params_to_delete = [constants.JULES_PARAM_USE_SUBGRID,
                            constants.JULES_PARAM_LATLON_REGION,
                            constants.JULES_PARAM_LAT_BOUNDS,
                            constants.JULES_PARAM_LON_BOUNDS,
                            constants.JULES_PARAM_NPOINTS,
                            constants.JULES_PARAM_POINTS_FILE,
                            constants.JULES_PARAM_SWITCHES_L_POINT_DATA,
                            constants.JULES_PARAM_RUN_START,
                            constants.JULES_PARAM_RUN_END]

        params_to_save = [[constants.JULES_PARAM_USE_SUBGRID, True]]
        if values['site'] == 'multi':
            params_to_save.append([constants.JULES_PARAM_LATLON_REGION, True])
            params_to_save.append([constants.JULES_PARAM_LAT_BOUNDS, [values['lat_s'], values['lat_n']]])
            params_to_save.append([constants.JULES_PARAM_LON_BOUNDS, [values['lon_w'], values['lon_e']]])
        else:
            params_to_save.append([constants.JULES_PARAM_LATLON_REGION, False])
            params_to_save.append([constants.JULES_PARAM_NPOINTS, 1])

            # Convert the lat, lon to the closest point if needed
            if self._is_user_driving_data(driving_data):
                lat, lon = values['lat'], values['lon']
            else:
                # We need the locations initialised
                driving_data = self.dataset_service.get_driving_dataset_by_id(driving_data.id)
                url = str(config['thredds.server_url'] + "dodsC/model_runs/" + driving_data.locations[0].base_url)
                dap_client = self.dap_client_factory.get_dap_client(url)
                lat, lon = dap_client.get_closest_lat_lon(values['lat'], values['lon'])

            params_to_save.append([constants.JULES_PARAM_POINTS_FILE, [lat, lon]])
            params_to_save.append([constants.JULES_PARAM_SWITCHES_L_POINT_DATA, 'point_data' in values])

        is_user_data = self._is_user_driving_data(driving_data)
        run_start = datetime.datetime.combine(values['start_date'],
                                              self._get_acceptable_start_datetime(model_run, driving_data,
                                                                                  is_user_data).time())
        run_end = datetime.datetime.combine(values['end_date'],
                                            self._get_acceptable_end_datetime(model_run, driving_data,
                                                                              is_user_data).time())
        params_to_save.append([constants.JULES_PARAM_RUN_START, run_start])
        params_to_save.append([constants.JULES_PARAM_RUN_END, run_end])
        parameter_service.save_new_parameters(params_to_save, params_to_delete, user.id)

        self._save_spinup(spinup_duration,
                          self._get_acceptable_start_datetime(model_run, driving_data, is_user_data),
                          self._get_acceptable_end_datetime(model_run, driving_data, is_user_data),
                          run_start, parameter_service, user.id)

    def validate_extents_form_values(self, values, model_run, driving_data, errors):
        """
        Validate extents values dictionary and add errors to an errors object if needed
        :param values: Dictionary of form element names : values
        :param model_run: Current model run
        :param driving_data: Chosen driving data
        :param errors: Object to add errors to
        :return: nothing
        """
        # Set the start and end times to be the times at which the driving data starts and ends.
        is_user_data = self._is_user_driving_data(driving_data)

        run_start = datetime.datetime.combine(values['start_date'],
                                              self._get_acceptable_start_datetime(model_run, driving_data,
                                                                                  is_user_data).time())
        run_end = datetime.datetime.combine(values['end_date'],
                                            self._get_acceptable_end_datetime(model_run, driving_data,
                                                                              is_user_data).time())
        temporal_extent = TemporalExtent(self._get_acceptable_start_datetime(model_run, driving_data, is_user_data),
                                         self._get_acceptable_end_datetime(model_run, driving_data, is_user_data))

        lat_bounds = self._get_default_lat_bounds(model_run, driving_data, is_user_data)
        lon_bounds = self._get_default_lon_bounds(model_run, driving_data, is_user_data)
        spatial_extent = SpatialExtent(lat_bounds[1], lat_bounds[0], lon_bounds[0], lon_bounds[1])

        if values['site'] == 'multi':
            self._validate_multicell_spatial_extents(spatial_extent, errors,
                                                     values['lat_n'], values['lat_s'],
                                                     values['lon_e'], values['lon_w'])
        else:
            self.validate_singlecell_spatial_extents(spatial_extent, errors,
                                                     values['lat'], values['lon'])

        self.validate_temporal_extents(temporal_extent, errors, run_start, run_end)

    def _validate_multicell_spatial_extents(self, spatial_extent, errors, lat_n, lat_s, lon_e, lon_w):
        """
        Validate multi cell spatial extents and add errors to an errors object if needed
        :param spatial_extent: Driving data spatial extent object
        :param errors: Object to add errors to
        :param lat_n: Northern latitude
        :param lat_s: Southern latitude
        :param lon_e: Eastern longitude
        :param lon_w: Western longitude
        :return: nothing
        """
        try:
            spatial_extent.set_lat_n(lat_n)
        except InvalidSpatialExtent as e:
            errors['lat_n'] = e.message
        try:
            spatial_extent.set_lat_s(lat_s)
        except InvalidSpatialExtent as e:
            errors['lat_s'] = e.message
        try:
            spatial_extent.set_lon_w(lon_w)
        except InvalidSpatialExtent as e:
            errors['lon_w'] = e.message
        try:
            spatial_extent.set_lon_e(lon_e)
        except InvalidSpatialExtent as e:
            errors['lon_e'] = e.message

    def validate_singlecell_spatial_extents(self, spatial_extent, errors, lat, lon):
        """
        Validate single cell spatial extents and add errors to an errors object if needed
        :param spatial_extent: Driving data spatial extent object
        :param errors: Object to add errors to
        :param lat: Latitude
        :param lon: Longitude
        :return: nothing
        """
        lat_s, lat_n = spatial_extent.get_lat_bounds()
        if not (-90 <= lat <= 90):
            errors['lat'] = "Latitude must be between -90 and 90"
        elif lat < lat_s:
            errors['lat'] = "Latitude (%s deg N) cannot be south of %s deg N" % (lat, lat_s)
        elif lat > lat_n:
            errors['lat'] = "Latitude (%s deg N) cannot be north of %s deg N" % (lat, lat_n)

        lon_w, lon_e = spatial_extent.get_lon_bounds()
        if not (-180 <= lon <= 180):
            errors['lon'] = "Longitude must be between -180 and 180"
        elif lon < lon_w:
            errors['lon'] = "Longitude (%s deg E) cannot be west of %s deg E" % (lon, lon_w)
        elif lon > lon_e:
            errors['lon'] = "Longitude (%s deg E) cannot be east of %s deg E" % (lon, lon_e)

    def validate_temporal_extents(self, temporal_extent, errors, run_start, run_end):
        """
        Validate temporal extents and add errors to an errors object if needed
        :param temporal_extent: Driving data temporal extent object
        :param errors: Object to add errors to
        :param run_start: Model run start datetime
        :param run_end:  Model run end datetime
        :return: nothing
        """
        if run_start is not None:
            try:
                temporal_extent.set_start(run_start)
            except InvalidTemporalExtent as e:
                errors['start_date'] = e.message
        if run_end is not None:
            try:
                temporal_extent.set_end(run_end)
            except InvalidTemporalExtent as e:
                errors['end_date'] = e.message

    def _is_user_driving_data(self, driving_data):
        return driving_data.id == self.dataset_service.get_id_for_user_upload_driving_dataset()

    def _save_spinup(self, duration, driving_start, driving_end, run_start, parameter_service, user_id):
        """
        Save the spinup parameters
        :param duration: duration in years
        :param driving_start: start
        :param driving_end: end
        :param run_start: run start
        :param parameter_service: parameter service
        :param user_id: users id
        :return: nothing
        """
        spin_start = self.spinup_helper.calculate_spinup_start(driving_start, run_start, duration)
        spin_end = self.spinup_helper.calculate_spinup_end(spin_start, driving_end, duration)
        spin_cycles = self.spinup_helper.calculate_spinup_cycles(spin_start, spin_end, duration)
        spin_params = [[constants.JULES_PARAM_SPINUP_START, spin_start],
                       [constants.JULES_PARAM_SPINUP_END, spin_end],
                       [constants.JULES_PARAM_SPINUP_CYCLES, spin_cycles]]
        old_spin_params = [constants.JULES_PARAM_SPINUP_START,
                           constants.JULES_PARAM_SPINUP_END,
                           constants.JULES_PARAM_SPINUP_CYCLES]
        parameter_service.save_new_parameters(spin_params, old_spin_params, user_id)
