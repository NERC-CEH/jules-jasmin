"""
header
"""

import logging
from formencode import htmlfill
from pylons import url, response
from pylons.decorators import validate, jsonify
from sqlalchemy.orm.exc import NoResultFound

from joj.lib import helpers
from joj.lib.base import BaseController, c, request, render, redirect
from joj.model.model_run_create_form import ModelRunCreateFirst
from joj.model.model_run_extent_schema import ModelRunExtentSchema
from joj.utils import constants
from joj.utils.error import abort_with_error
from joj.utils.utils import find_by_id, KeyNotFound
from joj.utils import output_controller_helper
from joj.utils import utils
from joj.utils.extents_controller_helper import ExtentsControllerHelper
from joj.utils.model_run_controller_helper import ModelRunControllerHelper
from joj.utils.bng_to_latlon_converter import OSGB36toWGS84
from joj.utils.driving_data_controller_helper import DrivingDataControllerHelper
from joj.utils.land_cover_controller_helper import LandCoverControllerHelper
from joj.services.land_cover_service import LandCoverService
from joj.services.user import UserService
from joj.services.dataset import DatasetService
from joj.services.general import ServiceException
from joj.services.model_run_service import ModelRunService, DuplicateName, ModelPublished
from joj.services.parameter_service import ParameterService


# The prefix given to parameter name in html elements

PARAMETER_NAME_PREFIX = 'param'

# Message to show when the submission has failed
SUBMISSION_FAILED_MESSAGE = \
    "Failed to submit the model run, this may be because the cluster is down. Please try again later."

log = logging.getLogger(__name__)


class ModelRunController(BaseController):
    """Provides operations for model runs"""

    def __init__(self, user_service=UserService(), model_run_service=ModelRunService(),
                 dataset_service=DatasetService(), parameter_service=ParameterService()):
        """Constructor
            Params:
                user_service: service to access user details
                model_run_service: service to access model runs
        """
        super(ModelRunController, self).__init__(user_service)
        self._model_run_service = model_run_service
        self._dataset_service = dataset_service
        self._parameter_service = parameter_service
        self._model_run_controller_helper = ModelRunControllerHelper(model_run_service)

    def index(self):
        """
        Default controller providing access to the catalogue of user model runs
        :return: Rendered catalogue page
        """
        # all non-created runs for the user
        c.user = self.current_user
        c.model_runs = [model
                        for model in self._model_run_service.get_models_for_user(self.current_user)
                        if model.status.name != constants.MODEL_RUN_STATUS_CREATED]

        total_user_storage = 0
        for model in c.model_runs:
            if model.status.name != constants.MODEL_RUN_STATUS_PUBLISHED:
                if model.storage_in_mb is not None:
                    total_user_storage += model.storage_in_mb

        c.storage_total_used_in_gb = utils.convert_mb_to_gb_and_round(total_user_storage)
        c.storage_percent_used = round(c.storage_total_used_in_gb / c.user.storage_quota_in_gb * 100.0, 0)
        c.bar_class = helpers.get_progress_bar_class_name(c.storage_percent_used)
        c.showing = "mine"

        return render("model_run/catalogue.html")

    def published(self):
        """
        Controller providing access to the catalogue of published model runs
        :return: Rendered catalogue page
        """
        c.user = self.current_user
        c.model_runs = self._model_run_service.get_published_models()
        c.showing = "published"
        return render("model_run/catalogue.html")

    def publish(self, id):
        """
        Controller allowing existing model runs to be published
        :param id: ID of model run to publish
        :return: redirect to the page you came from
        """
        if request.POST:
            self._model_run_service.publish_model(self.current_user, id)
            came_from = request.params['came_from']
            if came_from == 'catalogue':
                redirect(url(controller='model_run', action='index'))
            elif came_from == 'summary':
                redirect(url(controller='model_run', action='summary', id=id))

    def delete(self, id):
        """
        Action to delete a model run for a user or admin
        :param id: the id of the model to delete
        :return: redirect to catalgue with flash message
        """

        if not request.method == 'POST':
            helpers.error_flash("Model run deletion must be a post")
            redirect(url(controller='model_run', action='index'))

        try:
            model_run_name = self._model_run_service.delete_run_model(int(id), self.current_user)
            helpers.success_flash("Model run %s deleted" % model_run_name)
        except ValueError:
            helpers.error_flash("Model run id not a number can not delete it")
        except NoResultFound:
            helpers.error_flash("Model run can not be deleted, it does not exist")
        except ModelPublished:
            helpers.error_flash("The model run you are trying to delete has been published. "
                                "Only admins can delete published model runs.")
        except ServiceException, ex:
            helpers.error_flash("Model run can not be deleted: {}".format(ex.message))
            log.exception("Problem deleting model run %s" % id)

        redirect(url(controller='model_run', action='index'))

    def summary(self, id):
        """
        Controller providing a detailed summary of a single model run
        :param id: the id of the model run to display
        :return: Rendered summary page of requested model run
        """
        c.user = self.current_user
        c.model_run = self._model_run_service.get_model_by_id(self.current_user, id)
        return render("model_run/summary.html")

    def pre_create(self):
        """
        Controller for directing the creation of a new run
        If user is over quota redirects to index with error
        If model created redirects to last viewed page otherwise redirects to create page
        """
        self._model_run_controller_helper.check_user_quota(self.current_user)
        model = self._model_run_service.get_model_run_being_created_or_default(self.current_user)

        if self.current_user.model_run_creation_action and model.id is not None:
            helpers.success_flash("Continuing with the creation of your model run")
            redirect(url(controller='model_run', action=self.current_user.model_run_creation_action))
        helpers.success_flash("Creating a new model run")
        redirect(url(controller='model_run', action='create'))

    @validate(schema=ModelRunCreateFirst(), form='create', post_only=False, on_get=False, prefix_error=False,
              auto_error_formatter=BaseController.error_formatter)
    def create(self):
        """
        Controller for creating a new run
        """

        scientific_configurations = self._model_run_service.get_scientific_configurations()

        values = dict(request.params)
        errors = None
        if request.POST:
            try:
                self._model_run_service.update_model_run(
                    self.current_user,
                    self.form_result['name'],
                    self.form_result['science_configuration'],
                    self.form_result['description'])
                self._model_run_controller_helper.check_user_quota(self.current_user)
                redirect(url(controller='model_run', action='driving_data'))
            except NoResultFound:
                errors = {'science_configuration': 'Configuration is not recognised'}
            except DuplicateName:
                errors = {'name': 'Name can not be the same as another model run'}
        else:
            self._user_service.set_current_model_run_creation_action(self.current_user, "create")
            model = self._model_run_service.get_model_run_being_created_or_default(self.current_user)
            values['name'] = model.name
            values['science_configuration'] = model.science_configuration_id
            values['description'] = model.description

        c.scientific_configurations = scientific_configurations

        html = render('model_run/create.html')
        return htmlfill.render(
            html,
            defaults=values,
            errors=errors,
            auto_error_formatter=BaseController.error_formatter)

    def driving_data(self):
        """
        Select a driving data set
        """
        driving_data_controller_helper = DrivingDataControllerHelper()

        model_run = None
        try:
            model_run = \
                self._model_run_service.get_model_being_created_with_non_default_parameter_values(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before you can choose a driving data set")
            redirect(url(controller='model_run', action='create'))

        driving_datasets = self._dataset_service.get_driving_datasets()
        user_upload_ds_id = self._dataset_service.get_id_for_user_upload_driving_dataset()
        errors = {}

        c.driving_datasets = driving_datasets
        c.user_upload_ds_id = user_upload_ds_id
        c.driving_data_rows = model_run.driving_data_rows

        if not request.POST:
            self._user_service.set_current_model_run_creation_action(self.current_user, "driving_data")

            values = driving_data_controller_helper.create_values_dict_from_database(model_run)

            if len(driving_datasets) == 0:
                abort_with_error("There are no driving datasets available - cannot create a new model run")

            # If the chosen driving dataset value is None, set it to the first in the list
            if values['driving_dataset'] is None:
                values['driving_dataset'] = driving_datasets[0].id

            c.errors = errors
            html = render('model_run/driving_data.html')
            return htmlfill.render(
                html,
                defaults=values,
                errors=errors,
                auto_error_formatter=BaseController.error_formatter)
        else:
            # This is a post
            values = dict(request.params)

            # Get the action to perform and remove it from the dictionary
            action = values['submit']
            del values['submit']

            old_driving_dataset = None
            if model_run.driving_dataset_id is not None:
                old_driving_dataset = find_by_id(driving_datasets, model_run.driving_dataset_id)

            if action == u'Upload':
                # This is a request to to upload a driving data file
                try:
                    driving_data_controller_helper.save_uploaded_driving_data(values, errors,
                                                                              self._model_run_service,
                                                                              old_driving_dataset,
                                                                              self.current_user)
                    if len(errors) == 0:
                        # Reload the current page
                        helpers.success_flash("Your driving data file has been successfully uploaded.")
                        redirect(url(controller='model_run', action='driving_data'))
                        return
                    else:
                        c.errors = errors
                        html = render('model_run/driving_data.html')
                        return htmlfill.render(
                            html,
                            defaults=values,
                            errors=errors,
                            auto_error_formatter=BaseController.error_formatter)
                except ServiceException as e:
                    helpers.error_flash(e.message)
                    redirect(url(controller='model_run', action='driving_data'))
            elif action == u'Download':
                # This is a request to to download driving data
                try:
                    file_generator = driving_data_controller_helper.download_driving_data(values, errors, response)

                    if len(errors) > 0:
                        c.errors = errors
                        return htmlfill.render(
                            render('model_run/driving_data.html'),
                            defaults=values,
                            errors=errors,
                            auto_error_formatter=BaseController.error_formatter)
                    # This will stream the file to the browser without loading it all in memory
                    # BUT only if the .ini file does not have 'debug=true' enabled
                    return file_generator
                except ServiceException as e:
                    helpers.error_flash("Couldn't download data: %s." % e.message)
                    redirect(url(controller='model_run', action='driving_data'))
            else:

                try:
                    driving_dataset = find_by_id(driving_datasets, int(values['driving_dataset']))
                except (KeyNotFound, KeyError):
                    errors['driving_dataset'] = 'Driving data not recognised'
                    html = render('model_run/driving_data.html')
                    return htmlfill.render(
                        html,
                        defaults=values,
                        errors=errors,
                        auto_error_formatter=BaseController.error_formatter)
                # If the new selected driving dataset is NOT a user uploaded dataset:
                if driving_dataset.id != user_upload_ds_id:
                    # If the previous driving dataset was a user uploaded driving dataset we need to create an uploaded
                    # driving dataset so that the parameters are removed:
                    if old_driving_dataset is not None:
                        if old_driving_dataset.id == user_upload_ds_id:
                            old_driving_dataset = driving_data_controller_helper. \
                                _create_uploaded_driving_dataset(None, None, None, None, self._model_run_service)
                    self._model_run_service.save_driving_dataset_for_new_model(
                        driving_dataset,
                        old_driving_dataset,
                        self.current_user)
                else:
                    # If the selected driving dataset is the user uploaded dataset we can't proceed if the driving
                    # data has not already been uploaded:
                    if not model_run.driving_data_rows:
                        errors['driving-file'] = 'You must upload a driving data file'
                        c.errors = errors
                        html = render('model_run/driving_data.html')
                        return htmlfill.render(
                            html,
                            defaults=values,
                            errors=errors,
                            auto_error_formatter=BaseController.error_formatter)

                        # If the chosen ds_id is 'upload' and they have already uploaded data then we need do nothing

                self._model_run_controller_helper.check_user_quota(self.current_user)

                if action == u'Next':
                    redirect(url(controller='model_run', action='extents'))
                else:
                    redirect(url(controller='model_run', action='create'))

    @validate(schema=ModelRunExtentSchema(), form='extents', post_only=False, on_get=False, prefix_error=False,
              auto_error_formatter=BaseController.error_formatter)
    def extents(self):
        """
        Specify the spatial and temporal extents of the model
        """
        extents_controller_helper = ExtentsControllerHelper()

        # First we need to check that we are allowed to be on this page
        model_run = self.get_model_run_being_created_or_redirect(self._model_run_service)
        c.model_run = model_run
        c.dataset = driving_data = model_run.driving_dataset
        if driving_data is None:
            helpers.error_flash(u"You must select a driving data set before you can set the extents")
            redirect(url(controller='model_run', action='driving_data'))
        errors = {}

        if not request.POST:
            self._user_service.set_current_model_run_creation_action(self.current_user, "extents")
            values = extents_controller_helper.create_values_dict_from_database(model_run, driving_data)
            extents_controller_helper.set_template_context_fields(c, model_run, driving_data)

            # We need to check that saved values for user selected spatial extent are consistent with the chosen
            # driving data (e.g. in case the user has gone back and changed their driving data).
            extents_controller_helper.validate_extents_form_values(values, model_run, driving_data, errors)

            # Finally in our GET we render the page with any errors and values we have
            return htmlfill.render(
                render('model_run/extents.html'),
                defaults=values,
                errors=errors,
                auto_error_formatter=BaseController.error_formatter)

        # This is a POST
        else:
            values = self.form_result
            extents_controller_helper.set_template_context_fields(c, model_run, driving_data)

            extents_controller_helper.validate_extents_form_values(values, model_run, driving_data, errors)

            if len(errors) > 0:
                return htmlfill.render(
                    render('model_run/extents.html'),
                    defaults=values,
                    errors=errors,
                    auto_error_formatter=BaseController.error_formatter)

            extents_controller_helper.save_extents_against_model_run(values, driving_data, model_run,
                                                                     self._parameter_service, self.current_user)
            # Get the action to perform
            self._model_run_controller_helper.check_user_quota(self.current_user)
            try:
                action = values['submit']
            except KeyError:
                action = None
            if action == u'Next':
                redirect(url(controller='model_run', action='land_cover'))
            else:
                redirect(url(controller='model_run', action='driving_data'))

    def land_cover(self):
        """
        Set the land cover options
        """
        model_run = self.get_model_run_being_created_or_redirect(self._model_run_service)
        values = dict(request.params)
        errors = {}
        multicell = model_run.get_python_parameter_value(constants.JULES_PARAM_LATLON_REGION) \
            and not 'fractional_cover' in values

        if multicell:
            return self._land_cover(model_run, values, errors)
        else:
            latlon = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE, is_list=True)
            if latlon is None:
                helpers.error_flash(u"You must set model run extents set before you can edit the land cover")
                redirect(url(controller='model_run', action='extents'))
            return self._single_cell_land_cover(model_run, values, errors)

    def _land_cover(self, model_run, values, errors):
        land_cover_controller_helper = LandCoverControllerHelper()
        if not request.POST:
            self._user_service.set_current_model_run_creation_action(self.current_user, "land_cover")
            land_cover_controller_helper.add_land_covers_to_context(c, errors, model_run)
            if len(errors) > 0:
                helpers.error_flash(errors['land_cover_actions'])
            return render('model_run/land_cover.html')

        else:
            land_cover_controller_helper.save_land_cover_actions(values, errors, model_run)
            if len(errors) > 0:
                helpers.error_flash(errors['land_cover_actions'])
                return render('model_run/land_cover.html')
            else:
                # Get the action to perform
                self._model_run_controller_helper.check_user_quota(self.current_user)
                try:
                    action = values['submit']
                except KeyError:
                    action = None
                if action == u'Next':
                    redirect(url(controller='model_run', action='output'))
                else:
                    redirect(url(controller='model_run', action='extents'))

    def _single_cell_land_cover(self, model_run, values, errors):
        land_cover_controller_helper = LandCoverControllerHelper()
        if not request.POST:
            self._user_service.set_current_model_run_creation_action(self.current_user, "land_cover")
            land_cover_controller_helper.add_fractional_land_cover_to_context(c, errors, model_run)
            return render('model_run/fractional_land_cover.html')
        else:
            land_cover_controller_helper.save_fractional_land_cover(values, errors, model_run)
            if len(errors) > 0:
                if 'land_cover_frac' in errors:
                    helpers.error_flash(errors['land_cover_frac'])
                land_cover_controller_helper.add_fractional_land_cover_to_context(c, errors, model_run)
                c.land_cover_values = values
                del values['submit']
                html = render('model_run/fractional_land_cover.html')
                return htmlfill.render(
                    html,
                    defaults=values,
                    errors=errors,
                    auto_error_formatter=BaseController.error_formatter
                )
            else:
                self._model_run_controller_helper.check_user_quota(self.current_user)
                try:
                    action = values['submit']
                except KeyError:
                    action = None
                if action == u'Next':
                    redirect(url(controller='model_run', action='output'))
                else:
                    redirect(url(controller='model_run', action='extents'))

    def output(self):
        """
        Select output parameters
        """
        # First we need to check that we are allowed to be on this page
        model_run = self.get_model_run_being_created_or_redirect(self._model_run_service)

        if not request.POST:
            self._user_service.set_current_model_run_creation_action(self.current_user, "output")
            # We need to not show the output variables which are dependent on JULES_MODEL_LEVELS::nsmax if nsmax is 0
            jules_param_nsmax = model_run.get_python_parameter_value(constants.JULES_PARAM_NSMAX)
            c.output_variables = self._model_run_service.get_output_variables(
                include_depends_on_nsmax=jules_param_nsmax > 0)

            # We want to pass the renderer a list of which output variables are already selected and for which time
            # periods so that we can render these onto the page as selected
            output_controller_helper.add_selected_outputs_to_template_context(c, model_run)

            return render("model_run/output.html")
        else:
            values = dict(request.params)

            # Identify the requested output variables and save the appropriate parameters
            output_variable_groups = output_controller_helper.create_output_variable_groups(values,
                                                                                            self._model_run_service,
                                                                                            model_run)

            self._model_run_service.set_output_variables_for_model_being_created(output_variable_groups,
                                                                                 self.current_user)
            # Get the action to perform
            self._model_run_controller_helper.check_user_quota(self.current_user)
            try:
                action = values['submit']
            except KeyError:
                action = None
            if action == u'Next':
                redirect(url(controller='model_run', action='submit'))
            else:
                redirect(url(controller='model_run', action='land_cover'))

    def parameters(self):
        """
        Define parameters for the current new run being created
        """

        try:
            c.parameters = self._model_run_service.get_parameters_for_model_being_created(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before any parameters can be set")
            redirect(url(controller='model_run', action='create'))

        if not request.POST:
            html = render('model_run/parameters.html')
            parameter_values = {}
            for parameter in c.parameters:
                if parameter.parameter_values:
                    parameter_values[PARAMETER_NAME_PREFIX + str(parameter.id)] = parameter.parameter_values[0].value
            return htmlfill.render(
                html,
                defaults=parameter_values,
                errors={},
                auto_error_formatter=BaseController.error_formatter
            )
        else:

            # get the action to perform and remove it from the dictionary
            action = request.params.getone('submit')

            if action == u'Next':
                redirect(url(controller='model_run', action='submit'))
            else:
                redirect(url(controller='model_run', action='output'))

    def submit(self):
        """
        Page to submit the model un
        """
        model_run = None
        try:
            model_run = \
                self._model_run_service.get_model_being_created_with_non_default_parameter_values(self.current_user)
        except NoResultFound:
            helpers.error_flash(u"You must create a model run before submitting the model run")
            redirect(url(controller='model_run', action='create'))

        if not request.POST:
            self._user_service.set_current_model_run_creation_action(self.current_user, "submit")
            c.model_run = model_run
            driving_data = model_run.driving_dataset
            c.science_config = self._model_run_service.get_science_configuration_by_id(
                model_run.science_configuration_id)

            extents_controller_helper = ExtentsControllerHelper()
            c.extents_values = extents_controller_helper.create_values_dict_from_database(model_run, driving_data)

            c.driving_data_name = model_run.driving_dataset.name

            land_cover_service = LandCoverService()
            c.land_cover_actions = land_cover_service.get_land_cover_actions_for_model(model_run)

            land_cover_helper = LandCoverControllerHelper()
            try:
                land_cover_helper.add_fractional_land_cover_to_context(c, {}, model_run)
            except ServiceException:
                pass

            output_variables = self._model_run_service.get_output_variables()
            output_variable_dict = dict((x.name, x.description) for x in output_variables)
            selected_vars = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_VAR)
            selected_output_periods = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PERIOD)

            outputs = {}

            # Each group contains one output variable and one output period
            for selected_var in selected_vars:
                var_name = output_variable_dict[selected_var.get_value_as_python()]
                if var_name not in outputs:
                    outputs[var_name] = []
                for output_period in selected_output_periods:
                    if output_period.group_id == selected_var.group_id:
                        period = output_period.get_value_as_python()
                        if period == constants.JULES_YEARLY_PERIOD:
                            outputs[var_name].append('Yearly')
                        elif period == constants.JULES_MONTHLY_PERIOD:
                            outputs[var_name].append('Monthly')
                        elif period == constants.JULES_DAILY_PERIOD:
                            outputs[var_name].append('Daily')
                        else:
                            outputs[var_name].append('Hourly')
            c.outputs = []
            for output in outputs:
                c.outputs.append(output + ' - ' + ', '.join(map(str, outputs[output])) + '')
            c.outputs.sort()

        else:
            self._model_run_controller_helper.check_user_quota(self.current_user)
            if request.params.getone('submit') == u'Submit':
                status, message = self._model_run_service.submit_model_run(self.current_user)
                if status.name == constants.MODEL_RUN_STATUS_SUBMITTED:
                    helpers.success_flash(message)
                else:
                    helpers.error_flash(message)

                redirect(url(controller='model_run', action='index'))
            else:
                redirect(url(controller='model_run', action='output'))

        return render('model_run/submit.html')

    @jsonify
    def bng_to_latlon(self):
        """
        Allows AJAX call to convert BNG coordinates to lat / lon coordinates
        :return: JSON lat/lon dictionary
        """
        bng_easting = request.params['bng_easting']
        bng_northing = request.params['bng_northing']
        json_response = {}
        try:
            lat, lon = OSGB36toWGS84(float(bng_easting), float(bng_northing))
            json_response['lat'] = lat
            json_response['lon'] = lon
        except Exception:
            json_response['is_error'] = True
        return json_response
