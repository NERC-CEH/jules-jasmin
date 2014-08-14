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
                 drive_file=None,
                 drive_var=None,
                 var_names=None,
                 var_templates=None,
                 var_interps=None,
                 nx=None,
                 ny=None,
                 x_dim_name='Longitude',
                 y_dim_name='Latitude',
                 time_dim_name='Time'):
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

        self.data_period = dataperiod
        self.drive_file = drive_file
        self.vars = drive_var if drive_var is not None else []
        self.var_names = var_names if var_names is not None else []
        self.var_templates = var_templates if var_templates is not None else []
        self.var_interps = var_interps if var_interps is not None else []
        self.nx = nx
        self.ny = ny
        self.x_dim_name = x_dim_name
        self.y_dim_name = y_dim_name
        self.time_dim_name = time_dim_name

    def add_to_driving_dataset(self, model_run_service, driving_dataset):
        """
        Create driving data set parameters for non-none parameters set and add them to the driving dataset
        :param model_run_service: model run service to use
        :param driving_dataset: the driving dataset to add the parameters to
        :return:nothing
        """

        if self.drive_file is not None:
            val = f90_helper.python_to_f90_str(self.drive_file)
            DrivingDatasetParameterValue(model_run_service, driving_dataset, constants.JULES_PARAM_DRIVE_FILE, val)
        if self.vars is not None:
            val = f90_helper.python_to_f90_str(self.vars)
            DrivingDatasetParameterValue(model_run_service, driving_dataset, constants.JULES_PARAM_DRIVE_VAR, val)
        if self.var_names is not None:
            val = f90_helper.python_to_f90_str(self.var_names)
            DrivingDatasetParameterValue(model_run_service, driving_dataset, constants.JULES_PARAM_DRIVE_VAR_NAME, val)
        if self.var_templates is not None:
            val = f90_helper.python_to_f90_str(self.var_templates)
            DrivingDatasetParameterValue(model_run_service, driving_dataset, constants.JULES_PARAM_DRIVE_TPL_NAME, val)
        if self.var_interps is not None:
            val = f90_helper.python_to_f90_str(self.var_interps)
            DrivingDatasetParameterValue(model_run_service, driving_dataset, constants.JULES_PARAM_DRIVE_INTERP, val)
        if self.data_period is not None:
            val = f90_helper.python_to_f90_str(self.data_period)
            DrivingDatasetParameterValue(
                model_run_service,
                driving_dataset,
                constants.JULES_PARAM_DRIVE_DATA_PERIOD,
                val)
        if self.nx is not None:
            val = f90_helper.python_to_f90_str(self.nx)
            DrivingDatasetParameterValue(model_run_service, driving_dataset, constants.JULES_PARAM_INPUT_GRID_NX, val)
        if self.ny is not None:
            val = f90_helper.python_to_f90_str(self.ny)
            DrivingDatasetParameterValue(model_run_service, driving_dataset, constants.JULES_PARAM_INPUT_GRID_NY, val)
        if self.x_dim_name is not None:
            val = f90_helper.python_to_f90_str(self.x_dim_name)
            DrivingDatasetParameterValue(
                model_run_service,
                driving_dataset,
                constants.JULES_PARAM_INPUT_GRID_X_DIM_NAME,
                val)
        if self.y_dim_name is not None:
            val = f90_helper.python_to_f90_str(self.y_dim_name)
            DrivingDatasetParameterValue(
                model_run_service,
                driving_dataset,
                constants.JULES_PARAM_INPUT_GRID_Y_DIM_NAME,
                val)
        if self.time_dim_name is not None:
            val = f90_helper.python_to_f90_str(self.time_dim_name)
            DrivingDatasetParameterValue(
                model_run_service,
                driving_dataset,
                constants.JULES_PARAM_INPUT_TIME_DIM_NAME,
                val)

    def create_from(self, driving_data_set):
        self.data_period = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_PERIOD)
        self.drive_file = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_DRIVE_FILE)

        self.vars = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_DRIVE_VAR, is_list=True)
        self.var_names = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_DRIVE_VAR_NAME, is_list=True)
        self.var_templates = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_DRIVE_TPL_NAME, is_list=True)
        self.var_interps = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_DRIVE_INTERP, is_list=True)
        self.nx = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_INPUT_GRID_NX)
        self.ny = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_INPUT_GRID_NY)
        self.x_dim_name = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_INPUT_GRID_X_DIM_NAME)
        self.y_dim_name = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_INPUT_GRID_Y_DIM_NAME)
        self.time_dim_name = driving_data_set.get_python_parameter_value(constants.JULES_PARAM_INPUT_TIME_DIM_NAME)

    def add_to_dict(self, values):
        values['driving_data_period'] = self.data_period
        values['drive_file'] = self.drive_file
        values['drive_nx'] = self.nx
        values['drive_ny'] = self.ny
        values['drive_x_dim_name'] = self.x_dim_name
        values['drive_y_dim_name'] = self.y_dim_name
        values['drive_time_dim_name'] = self.time_dim_name

        if self.vars is None:
            nvar = 0
        else:
            nvar = 0
            for var, name, template, interp_flag in zip(self.vars, self.var_names, self.var_templates, self.var_interps):
                nvar += 1
                values['drive_var_{}'.format(nvar - 1)] = var
                values['drive_var_name_{}'.format(nvar - 1)] = name
                values['drive_var_template_{}'.format(nvar - 1)] = template
                values['drive_var_interp_{}'.format(nvar - 1)] = interp_flag
        values['drive_nvar'] = nvar