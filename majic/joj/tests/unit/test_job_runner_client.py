# header
from formencode import Invalid

from mock import MagicMock, ANY

from joj.services.tests.base import BaseTest
from hamcrest import *
from joj.model import User, Parameter, ModelRun, CodeVersion, ParameterValue, NamelistFile, Namelist
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from tests import TestController


class TestJobRunnerClient(TestController):

    def test_GIVEN_valid_model_WHEN_convert_to_dictionary_THEN_dictionary_is_correct(self):

        job_runner_client = JobRunnerClient()

        parameter = Parameter(name='param1')
        expected_parameter_value = '12'
        parameter.parameter_values = [ParameterValue(value=expected_parameter_value)] #There is only one parameter value per run

        namelist = Namelist(name='NAME_LIST')
        namelist_file = NamelistFile(filename='filename')

        namelist.parameters = [parameter]
        namelist.namelist_file=namelist_file

        model_run = ModelRun()
        model_run.id=101
        code_version = CodeVersion(name='Jules v3.4.1')

        model_run.code_version = code_version
        code_version.parameters = [parameter]


        result = job_runner_client.convert_model_to_dictionary(model_run)

        assert_that(result[constants.JSON_MODEL_RUN_ID], is_(model_run.id), "value is correct")
        assert_that(result[constants.JSON_MODEL_CODE_VERSION], is_(model_run.code_version.name), "value is correct")
        namelist_file_result =result[constants.JSON_MODEL_NAMELIST_FILES][0]
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELIST_FILE_FILENAME], is_(namelist_file.filename), "value is correct")
        assert_that(namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_NAMELIST_NAME],
                    is_(namelist.name), "value is correct")
        parameters_result = namelist_file_result[constants.JSON_MODEL_NAMELISTS][0][constants.JSON_MODEL_PARAMETERS]
        assert_that(parameters_result, is_({parameter.name: expected_parameter_value}), "value is correct")
