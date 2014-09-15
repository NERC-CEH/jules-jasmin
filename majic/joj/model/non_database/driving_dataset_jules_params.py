"""
header
"""
from joj.model import DrivingDatasetParameterValue
from joj.utils import f90_helper, constants


class DrivingDatasetJulesParams(object):
    """
    Encapsulate the driving data jules parameters
    """

    def __init__(self,
                 dataperiod=None,
                 data_start=None,
                 data_end=None,
                 drive_file=None,
                 drive_var=None,
                 var_names=None,
                 var_templates=None,
                 var_interps=None,
                 nx=None,
                 ny=None,
                 x_dim_name='Longitude',
                 y_dim_name='Latitude',
                 time_dim_name='Time',
                 latlon_file=None,
                 latlon_lat_name='Grid_lat',
                 latlon_lon_name='Grid_lon',
                 land_frac_file=None,
                 land_frac_frac_name='land',
                 frac_file=None,
                 frac_frac_dim_name='frac',
                 frac_type_dim_name='psuedo',
                 soil_props_file=None,
                 extra_parameters=None,
                 driving_dateset=None,
                 regions=None):
        """
        Initialise
        :param dataperiod: the period of each time step
        :param drive_file: the file name for the driving data
        :param drive_var: list of variables
        :param var_names: list of varaile names
        :param var_templates: list of template names
        :param var_interps: list of interpolation flags
        :param nx: number of cells in x
        :param ny: number of cells in y
        :param x_dim_name: x dimension name
        :param y_dim_name: y dimension name
        :param time_dim_name: time dimension name
        :return: nothing
        """
        self._names_constant_dict = {
            'driving_data_period': constants.JULES_PARAM_DRIVE_DATA_PERIOD,
            'driving_data_start': constants.JULES_PARAM_DRIVE_DATA_START,
            'driving_data_end': constants.JULES_PARAM_DRIVE_DATA_END,
            'drive_file': constants.JULES_PARAM_DRIVE_FILE,
            'drive_var_vars': constants.JULES_PARAM_DRIVE_VAR,
            'drive_nvars': constants.JULES_PARAM_DRIVE_NVARS,
            'drive_var_names': constants.JULES_PARAM_DRIVE_VAR_NAME,
            'drive_var_templates': constants.JULES_PARAM_DRIVE_TPL_NAME,
            'drive_var_interps': constants.JULES_PARAM_DRIVE_INTERP,
            'drive_nx': constants.JULES_PARAM_INPUT_GRID_NX,
            'drive_ny': constants.JULES_PARAM_INPUT_GRID_NY,
            'drive_x_dim_name': constants.JULES_PARAM_INPUT_GRID_X_DIM_NAME,
            'drive_y_dim_name': constants.JULES_PARAM_INPUT_GRID_Y_DIM_NAME,
            'drive_time_dim_name': constants.JULES_PARAM_INPUT_TIME_DIM_NAME,
            'latlon_file': constants.JULES_PARAM_LATLON_FILE,
            'latlon_lat_name': constants.JULES_PARAM_LATLON_LAT_NAME,
            'latlon_lon_name': constants.JULES_PARAM_LATLON_LON_NAME,
            constants.LAND_COVER_FRAC_FILE_INPUT_NAME: constants.JULES_PARAM_FRAC_FILE,
            'frac_frac_name': constants.JULES_PARAM_FRAC_NAME,
            'frac_type_dim_name': constants.JULES_PARAM_INPUT_TYPE_DIM_NAME,
            'land_frac_file': constants.JULES_PARAM_LAND_FRAC_FILE,
            'land_frac_frac_name': constants.JULES_PARAM_LAND_FRAC_LAND_FRAC_NAME,
            'soil_props_file': constants.JULES_PARAM_SOIL_PROPS_FILE}

        self.values = {}
        self._extra_parameters = {}

        self.driving_dataset = driving_dateset
        if driving_dateset is not None:
            self.set_from(driving_dateset, regions if regions is not None else [])

        self.values.update({
            'driving_data_period': dataperiod,
            'driving_data_start': data_start,
            'driving_data_end': data_end,
            'drive_file': drive_file,
            'drive_var_vars': drive_var if drive_var is not None else [],
            'drive_var_names': var_names if var_names is not None else [],
            'drive_var_templates': var_templates if var_templates is not None else [],
            'drive_var_interps': var_interps if var_interps is not None else [],
            'drive_nx': nx,
            'drive_ny': ny,
            'drive_x_dim_name': x_dim_name,
            'drive_y_dim_name': y_dim_name,
            'drive_time_dim_name': time_dim_name,
            'latlon_file': latlon_file,
            'latlon_lat_name': latlon_lat_name,
            'latlon_lon_name': latlon_lon_name,
            constants.LAND_COVER_FRAC_FILE_INPUT_NAME: frac_file,
            'frac_frac_name': frac_frac_dim_name,
            'frac_type_dim_name': frac_type_dim_name,
            'land_frac_file': land_frac_file,
            'land_frac_frac_name': land_frac_frac_name,
            'soil_props_file': soil_props_file})

        self.values['drive_nvars'] = len(self.values['drive_var_vars'])

        if extra_parameters is not None:
            self._extra_parameters.update(extra_parameters)

    def add_to_driving_dataset(self, model_run_service, driving_dataset, session):
        """
        Create driving data set parameters for non-none parameters set and add them to the driving dataset
        :param model_run_service: model run service to use
        :param driving_dataset: the driving dataset to add the parameters to
        :param session: database session to use
        :return:nothing
        """

        for key, value in self.values.iteritems():
            if value is not None and value != []:
                val = f90_helper.python_to_f90_str(value)
                DrivingDatasetParameterValue(
                    model_run_service,
                    driving_dataset,
                    self._names_constant_dict[key],
                    val,
                    session)

        for parameter_id, value in self._extra_parameters.iteritems():
            if value is not None and value != []:
                DrivingDatasetParameterValue(model_run_service, driving_dataset, parameter_id, value, session)

    def set_from(self, driving_dataset, regions):
        """
        Set values from a driving set with parameters in
        :param driving_dataset: the driving data set
        :param regions: regions foe the driving dataset
        :return: nothing
        """

        for name, constant in self._names_constant_dict.iteritems():
            val = driving_dataset.get_python_parameter_value(constant)
            self.values[name] = val

        #values which can not be none
        if self.values['drive_nvars'] is None:
            self.values['drive_nvars'] = 0

        for parameter_value in driving_dataset.parameter_values:
            found = False
            for named_param in self._names_constant_dict.values():
                    if named_param[0] == parameter_value.parameter.namelist.name \
                            and named_param[1] == parameter_value.parameter.name:
                        found = True
                    continue
            if not found:
                self._extra_parameters[parameter_value.parameter_id] = parameter_value.value

        self.regions = regions
        self.driving_dataset = driving_dataset

    def _get_driving_var_variable_field_name(self, name):
        """
        Get the driving variable name e.g. drive_var_interps interps is returned
        :param name: full name
        :return: field name
        """

        return name[len(constants.PREFIX_FOR_DRIVING_VARS):]

    def create_values_dict(self, namelists):
        """
        Create a jules parameters values dictionary
        :param namelists: the list of namelists with parameters
        :return: values dictionary
        """

        values_dict = self.driving_dataset.__dict__

        for name in self._names_constant_dict.keys():
            if name in self.values:
                value = self.values[name]
                if name.startswith(constants.PREFIX_FOR_DRIVING_VARS) and value is not None:
                    for val, index in zip(value, range(len(value))):
                        values_dict["{}-{}.{}".format(constants.PREFIX_FOR_DRIVING_VARS, str(index),
                                                      self._get_driving_var_variable_field_name(name))] = val
                else:
                    values_dict[name] = value
            else:
                values_dict[name] = ''

        values_dict['parameters_nvar'] = len(self._extra_parameters)

        params = []
        for param_id, val in self._extra_parameters.iteritems():

            name = "Unknown"
            for namelist_name, namelist in namelists.iteritems():
                if param_id in namelist:
                    name = namelist_name + '::' + namelist[param_id]
                    continue
            params.append([name, param_id, val])

        params = sorted(params, key=lambda param: param[0], reverse=True)
        index = 0
        for name, param_id, val in params:
            values_dict["param-{}.id".format(str(index))] = param_id
            values_dict["param-{}.value".format(str(index))] = val
            index += 1

        values_dict["param_names"] = [param[0] for param in params]
        values_dict['params_count'] = len(params)

        mask_count = 0
        for region in self.regions:
            values_dict['region-{}.id'.format(mask_count)] = region.id
            values_dict['region-{}.name'.format(mask_count)] = region.name
            values_dict['region-{}.path'.format(mask_count)] = region.mask_file
            values_dict['region-{}.category'.format(mask_count)] = region.category.name
            mask_count += 1
        values_dict['mask_count'] = mask_count

        return values_dict

    def update_driving_dataset_from_dict(
            self,
            driving_dataset,
            session,
            model_run_service,
            land_cover_service,
            results,
            locations):
        """
        Update a driving dataset object from a results dictionary
        :param driving_dataset: the driving dataset to update
        :param results: the results
        :param session: session to use
        :param model_run_service: model run service
        :param land_cover_service: land cover service
        :param locations: file locations for driving dataset
        :return: the driving dataset
        """

        driving_dataset.set_from(results)

        driving_dataset.time_start = results.get("driving_data_start")
        driving_dataset.time_end = results.get("driving_data_end")

        for name, jules_parameter_constant in self._names_constant_dict.iteritems():
            if name.startswith(constants.PREFIX_FOR_DRIVING_VARS) and constants.PREFIX_FOR_DRIVING_VARS in results:
                field_name = self._get_driving_var_variable_field_name(name)
                value = [result[field_name] for result in results[constants.PREFIX_FOR_DRIVING_VARS]]
                self.values[name] = value
            elif name in results:
                self.values[name] = results[name]

        if 'param' in results:
            for result in results['param']:
                self._extra_parameters[result['id']] = result['value']

        self.add_to_driving_dataset(model_run_service, driving_dataset, session)

        land_cover_service\
            .update_regions_and_categories_in_session(session, driving_dataset, results["region"])

        driving_dataset.locations = locations

        return driving_dataset
