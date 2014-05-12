import logging
from pylons.controllers.util import redirect
import formencode
from pylons.decorators import jsonify
from ecomaps.analysis.run import AnalysisRunner

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.analysis import AnalysisService
from ecomaps.services.model import ModelService
from ecomaps.services.netcdf import NetCdfService
from ecomaps.services.user import UserService
from ecomaps.services.dataset import DatasetService
from pylons import tmpl_context as c, url
from ecomaps.model.configure_analysis_form import ConfigureAnalysisForm
from formencode import htmlfill
import tempfile
from paste.fileapp import FileApp
import os
import urlparse

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class AnalysisController(BaseController):
    """Provides operations for analysis page actions"""

    _user_service = None
    _analysis_service = None
    _dataset_service = None
    _netcdf_service = None
    _model_service = None

    def __init__(self, user_service=UserService(), analysis_service=AnalysisService(),
                 dataset_service=DatasetService(), netcdf_service=NetCdfService(),
                 model_service=ModelService()):
        """Constructor for the analysis controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(AnalysisController, self).__init__(user_service)

        self._analysis_service = analysis_service
        self._dataset_service = dataset_service
        self._netcdf_service = netcdf_service
        self._model_service = model_service

    def index(self):
        """Default action for the analysis controller"""

        # Who am I?
        user = self.current_user

        # Grab the analyses...
        c.private_analyses = self._analysis_service.get_analyses_for_user(user.id)
        c.public_analyses = self._analysis_service.get_public_analyses()

        #Get the model variables - used to populate the filter dropdown
        c.all_model_variables = self._analysis_service.get_all_model_variables()

        return render('analysis_list.html')

    def sort_and_filter(self):
        """Action for sorting the analysis table using a particular column. Also responsible for filtering the table
        based on the model variable.
        """
        user = self.current_user
        query_string = request.query_string
        params = urlparse.parse_qs(query_string)

        column = get_parameter_value(params,'column')
        order = get_parameter_value(params,'order')
        filter_variable = get_parameter_value(params,'filter_variable')
        is_public = get_parameter_value(params,'is_public')

        c.order = order
        c.sorting_column = column
        c.filter_variable = filter_variable

        if is_public == "true":
            c.public_analyses = self._analysis_service.sort_and_filter_public_analyses_by_column(column,order,filter_variable)

            if not c.public_analyses:
                c.empty_public_table = "true"

            return render('public_analyses_table.html')
        else:
            c.private_analyses = self._analysis_service.sort_and_filter_private_analyses_by_column(user.id,column,order,filter_variable)

            if not c.private_analyses:
                c.empty_private_table = "true"

            return render('private_analyses_table.html')


    def create(self):
        """ Creates the configure analysis page"""

        user_id = self.current_user.id

        c.all_models = self._model_service.get_all_models()

        c.point_datasets = self._dataset_service.get_datasets_for_user(user_id,'Point')

        coverage_datasets = self._dataset_service.get_datasets_for_user(user_id, 'Coverage')

        for ds in coverage_datasets:

            ds.column_names = self._netcdf_service.get_variable_column_names(ds.netcdf_url)

        c.coverage_datasets = coverage_datasets

        if not request.POST:

            unit_of_time = None
            random_group = None
            model_variable = None
            data_type = None

            return render('configure_analysis.html',
                          extra_vars={'unit_of_time': unit_of_time,
                                      'random_group': random_group,
                                      'model_variable': model_variable,
                                      'data_type': data_type})

        else:
            schema = ConfigureAnalysisForm()
            c.form_errors = {}

            try:
                c.form_result = schema.to_python(request.params)

            except formencode.Invalid, error:
                c.form_result = error.value
                c.form_errors = error.error_dict or {}

            #    If coverage_dataset_ids is not populated on the form
            #    the validation doesn't throw an error, but instead returns an empty
            #    array. Hence we have to do the error-handling ourselves
            if not c.form_result.get('coverage_dataset_ids'):
                c.form_errors = dict(c.form_errors.items() + {
                    'coverage_dataset_ids': 'Please select at least one coverage dataset'
                }.items())

            if c.form_errors:
                html = render('configure_analysis.html')

                return htmlfill.render(html,
                                       defaults=c.form_result,
                                       errors=c.form_errors,
                                       auto_error_formatter=custom_formatter)
            else:

                # OK, the form has been processed successfully, now
                # to see if this combination of inputs has been used
                # before
                hash = get_hash_for_inputs(c.form_result, ['point_dataset_id',
                                                           'coverage_dataset_ids',
                                                           'unit_of_time',
                                                           'random_group',
                                                           'model_variable',
                                                           'data_type',
                                                           'model_id',
                                                           'analysis_description'])


                # Almost ready to create, although first we need to create a collection of
                # time point indicies based on any temporal datasets we may have chosen

                time_indicies = {}

                for column in c.form_result.get('coverage_dataset_ids'):

                    # Is there a time selection field for this coverage ds column ?
                    # If so, it'll have been given a name starting with 'time' - see dataset_time_values.html
                    if c.form_result.get('time_%s' % column):
                        time_indicies[column] = int(c.form_result.get('time_%s' % column))

                test_analysis = self._analysis_service.get_public_analyses_with_identical_input(hash)

                if test_analysis and not any(time_indicies):
                    return redirect(url(controller='analysis', action='view', id=test_analysis.id))


                analysis_id = self._analysis_service.create(c.form_result.get('analysis_name'),
                            c.form_result.get('point_dataset_id'),
                            c.form_result.get('coverage_dataset_ids'),
                            user_id,
                            c.form_result.get('unit_of_time'),
                            c.form_result.get('random_group'),
                            c.form_result.get('model_variable'),
                            c.form_result.get('data_type'),
                            c.form_result.get('model_id'),
                            c.form_result.get('analysis_description'),
                            hash,
                            time_indicies)

                c.analysis_id = analysis_id

                analysis_to_run = self._analysis_service.get_analysis_by_id(analysis_id, user_id)

                model = self._model_service.get_model_by_id(analysis_to_run.model_id)

                # The path to the code may need to be made dynamic
                # if we start running multiple analyses
                runner = AnalysisRunner(model.code_path)
                runner.run_async(analysis_to_run)

                return render('analysis_progress.html')

    def view(self, id):
        """Action for looking in detail at a single analysis
            id - ID of the analysis to look at
        """

        user_obj = self.current_user

        analysis = self._analysis_service.get_analysis_by_id(id, user_obj.id)
        c.run_by_user = analysis.run_by_user.name

        if analysis:
            if analysis.result_dataset:
                # Get the result attributes from the NetCDF file associated with the result dataset
                analysis.attributes = self._netcdf_service.get_attributes(analysis.result_dataset.netcdf_url)

            c.analysis = analysis

            if 'compact' in request.params:
                return render('analysis_compact.html')
            else:
                return render('analysis_view.html', extra_vars={'added_successfully': None})
        else:
            c.object_type = 'analysis'
            return render('not_found.html')

    def publish(self):
        """Action for publishing a set of results
        """

        if request.POST:

            analysis_id = request.params.get('analysis_id')

            user_obj = self.current_user
            c.username = user_obj.name

            analysis = self._analysis_service.get_analysis_by_id(analysis_id, user_obj.id)

            if analysis:
                if analysis.result_dataset:
                    # Get the result attributes from the NetCDF file associated with the result dataset
                    analysis.attributes = self._netcdf_service.get_attributes(analysis.result_dataset.netcdf_url)
                c.analysis = analysis

                try:
                    c.form_result = request.params
                except:
                    added_successfully = False
                else:
                    self._analysis_service.publish_analysis(int(analysis_id))
                    added_successfully = True

                return render('analysis_view.html', extra_vars={'added_successfully': added_successfully})
            else:
                return render('not_found.html')
        else:
            return render('not_found.html')


    def rerun(self, id):
        """Action for re-running a particular analysis with same parameters as before
            id - ID of the analysis to look at
        """

        user_id = self.current_user.id
        c.point_datasets = self._dataset_service.get_datasets_for_user(user_id,'Point')
        coverage_datasets = self._dataset_service.get_datasets_for_user(user_id, 'Coverage')

        # Be sure to populate the column names for each coverage dataset, this
        # will populate the list correctly
        for ds in coverage_datasets:
            ds.column_names = self._netcdf_service.get_variable_column_names(ds.netcdf_url)

        c.coverage_datasets = coverage_datasets
        c.all_models = self._model_service.get_all_models()

        current_analysis = self._analysis_service.get_analysis_by_id(id, user_id)
        point_dataset_id = current_analysis.point_data_dataset_id
        model_id = current_analysis.model_id

        # For each coverage dataset that was linked to the original analysis, there
        # will be a number of column names chosen...
        cds = current_analysis.coverage_datasets
        coverage_dataset_ids = []

        # So create the right type of "ID" based on the convention we're using
        # which is <id>_<column-name>
        for dataset in cds:
            coverage_dataset_ids.extend(["%s_%s" % (dataset.dataset_id, col.column) for col in dataset.columns])

        unit_of_time = current_analysis.unit_of_time
        random_group = current_analysis.random_group
        model_variable = current_analysis.model_variable
        data_type = current_analysis.data_type

        return render('configure_analysis.html',
                              extra_vars={'current_model_id': model_id,
                                          'current_point_dataset_id': point_dataset_id,
                                          'current_coverage_dataset_ids': coverage_dataset_ids,
                                          'unit_of_time': unit_of_time,
                                          'random_group': random_group,
                                          'model_variable': model_variable,
                                          'data_type': data_type})

    @jsonify
    def progress(self, id):
        """Gets a progress message from the analysis with the supplied ID
            Params:
                id: ID of analysis to get progress message for
        """

        analysis = self._analysis_service.get_analysis_by_id(id, self.current_user.id)

        return {
            'complete': analysis.complete,
            'message': analysis.progress_message
        }

    def test(self, id):

        c.analysis_id = id
        return render('analysis_progress.html')

    def download(self,id):
        '''Action that allows the user to download a results dataset
        '''

        user_id = self.current_user.id

        current_analysis = self._analysis_service.get_analysis_by_id(id, user_id)
        result_dataset_id = current_analysis.result_dataset_id
        result_dataset = self._dataset_service.get_dataset_by_id(result_dataset_id, user_id=user_id)
        url = result_dataset.netcdf_url

        data_file = self._analysis_service.get_netcdf_file(url)
        with tempfile.NamedTemporaryFile(suffix=".ncdf") as temp_file:
            temp_file.write(data_file.read())

            file_size = os.path.getsize(temp_file.name)

            headers = [('Content-Disposition', 'attachment; '
                       'filename=\"' + temp_file.name + '\"'),
                        ('Content-Type', 'text/plain'),
                        ('Content-Length', str(file_size))]

            fapp = FileApp(temp_file.name, headers=headers)

            return fapp(request.environ, self.start_response)

    def delete(self, id):
        """Action for when user wants to delete a private analysis"""
        if request.POST:

            analysis_id = request.params.get('analysis_id') or id

            # Check user has access to the analysis before deleting
            analysis = self._analysis_service.get_analysis_by_id(analysis_id, self.current_user.id)
            if analysis:
                self._analysis_service.delete_private_analysis(analysis_id)

                # Also soft-delete the result dataset to keep the
                # list tidy
                if analysis.result_dataset_id:
                    self._dataset_service.delete(analysis.result_dataset_id, self.current_user.id)

                return redirect(url(controller='analysis', action='index'))


def custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )

def get_hash_for_inputs(input_dict, keys=None):
    """ Returns a hash based on the dict passed in, or a subset of its keys

    @param input_dict: Dictionary to get a hash code for
    @param keys: List of keys to subselect
    """

    sub_dict = {}
    if keys:

        # Create a subset
        for key in keys:

            try:
                assert isinstance(input_dict[key], list)
                sub_dict[key] = "".join(input_dict[key])
            except AssertionError:
                sub_dict[key] = input_dict[key]
    else:
        sub_dict = input_dict

    return hash(frozenset(sub_dict.items()))

def get_parameter_value(dictionary, name):

    try:
        return dictionary[name][0]
    except:
        return None
