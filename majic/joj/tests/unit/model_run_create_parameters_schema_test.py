# header
from formencode import Invalid

from mock import MagicMock, ANY

from joj.services.tests.base import BaseTest
from hamcrest import *
from joj.model import User, Parameter
from joj.model.model_run_create_parameters import ModelRunCreateParameters
from joj.utils import constants


class GIVEN_one_required_integer_without_min_parameter(BaseTest):

    def setUp(self):
        super(GIVEN_one_required_integer_without_min_parameter, self).setUp()

        self.parameter = Parameter()
        self.parameter.type = constants.PARAMETER_TYPE_INTEGER
        self.parameter.id = 1
        self.parameter.required = True
        self.parameters = [self.parameter]
        self.schema = ModelRunCreateParameters(self.parameters)


    def test_WHEN_valid_integer_THEN_validation_success(self):

        result = self.schema.to_python({'param1': u'1'})

        assert_that(result['param1'], is_(1), "value is correct")

    def test_WHEN_empty_THEN_error(self):
        with self.assertRaises(Invalid):
            self.schema.to_python({'param1': ''})

    def test_WHEN_is_non_integer_THEN_error(self):
        with self.assertRaises(Invalid):
            self.schema.to_python({'param1': 'abc'})


class GIVEN_one_optional_integer_parameter(BaseTest):

    def setUp(self):
        super(GIVEN_one_optional_integer_parameter, self).setUp()

        self.parameter = Parameter()
        self.parameter.type = constants.PARAMETER_TYPE_INTEGER
        self.parameter.id = 1
        self.parameter.required = False
        self.parameters = [self.parameter]
        self.schema = ModelRunCreateParameters(self.parameters)

    def test_WHEN_valid_integer_THEN_validation_success(self):

        result = self.schema.to_python({'param1': u'1'})

        assert_that(result['param1'], is_(1), "value is correct")

    def test_WHEN_empty_THEN_validation_success(self):
        result = self.schema.to_python({'param1': u''})

        assert_that(result['param1'], none(), "value is correct")

    def test_WHEN_is_non_integer_THEN_error(self):
        with self.assertRaises(Invalid):
            self.schema.to_python({'param1': 'abc'})


class GIVEN_one_required_integer_with_min_and_max_parameter(BaseTest):

    def setUp(self):
        super(GIVEN_one_required_integer_with_min_and_max_parameter, self).setUp()

        self.parameter = Parameter()
        self.parameter.type = constants.PARAMETER_TYPE_INTEGER
        self.parameter.id = 1
        self.parameter.required = True
        self.parameter.min = 1
        self.parameter.max = 10
        self.parameters = [self.parameter]
        self.schema = ModelRunCreateParameters(self.parameters)

    def test_WHEN_valid_integer_THEN_validation_success(self):

        result = self.schema.to_python({'param1': u'1'})

        assert_that(result['param1'], is_(1), "value is correct")

    def test_WHEN_smaller_than_min_THEN_error(self):
        with self.assertRaises(Invalid):
            self.schema.to_python({'param1': '0'})

    def test_WHEN_larger_than_max_THEN_error(self):
        with self.assertRaises(Invalid):
            self.schema.to_python({'param1': '11'})


class GIVEN_invalid_parameters(BaseTest):

    def setUp(self):
        super(GIVEN_invalid_parameters, self).setUp()

    def test_GIVEN_one_required_integer_parameter_WHEN_is_non_integer_THEN_error(self):
        with self.assertRaises(Exception):
            self.parameter = Parameter()
            self.parameter.type = 'rubbish'
            self.parameter.id = 1
            self.parameter.required = True
            self.parameters = [self.parameter]
            self.schema = ModelRunCreateParameters(self.parameters)
