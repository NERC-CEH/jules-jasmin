"""
header
"""
from sqlalchemy.orm.exc import NoResultFound
from joj.utils import constants
from joj.utils.utils import insert_before_file_extension
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.services.model_run_service import ModelRunService


class DatasetDownloadHelper(object):
    """
    Manages downloads of output datasets
    """

    def __init__(self, model_run_service=ModelRunService(), dap_client_factory=DapClientFactory()):
        self.model_run_service = model_run_service
        self.dap_client_factory = dap_client_factory

    def generate_output_file_path(self, model_run_id, output_var_name, period, year=None):
        """
        Generate a file path for an output dataset
        :param model_run_id: ID of Model Run to download from
        :param output_var_name: Variable name to download
        :param period: Period (e.g. 'daily')
        :param year: Calendar year to download (only required if period is daily or hourly)
        :return: File path (relative to run directory)
        """
        name_template = "run{model_run_id}/{output_dir}/{run_id}.{var_name}_{period}.nc"
        file_name = name_template.format(
            model_run_id=model_run_id,
            output_dir=constants.OUTPUT_DIR,
            run_id=constants.RUN_ID,
            var_name=output_var_name,
            period=period.lower()
        )
        if year is not None and period.lower() not in ['monthly', 'yearly']:
            year_suffix = ".%s" % year
            file_name = insert_before_file_extension(file_name, year_suffix)
        return file_name

    def validate_parameters(self, params, user):
        """
        Validate and return any parameters
        :param params: Request Parameters dictionary
        :param user: Currently logged in user
        :return: Model Run ID, Output variable ID, Period, Year
        :raises: ValueError or TypeError on validation fail.
        """
        # Check values are integers to prevent directory traversal.
        try:
            model_run_id = int(params.get('model_run_id'))
            output_var_id = int(params.get('output'))
            year = params.get('year')
            if year is not None:
                if len(year) > 0:
                    year = int(year)
                else:
                    year = None
            period = str(params.get('period'))
            if period.lower() not in ['yearly', 'daily', 'monthly', 'hourly']:
                raise ValueError  # Only these four permitted
            # Check model run viewable by user
            try:
                self.model_run_service.get_model_by_id(user, model_run_id)
                output_var_name = self.model_run_service.get_output_variable_by_id(output_var_id).name
            except NoResultFound:
                raise ValueError
        except TypeError:
            raise ValueError
        return model_run_id, output_var_name, period, year

    def download_file_generator(self, file_path, model_run):
        pass

    def set_response_header(self, header_dict, filepath):
        pass