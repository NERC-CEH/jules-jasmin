"""
Main controller for the Viewdata application.

@author: rwilkinson
"""
import logging
import os
from cStringIO import StringIO
import urllib2
from pylons import url
from pylons.decorators import jsonify
from pylons.controllers.util import redirect
from paste.fileapp import FileApp
from ecomaps.lib.base import config, c, request, response, render, session, abort
from ecomaps.lib.build_figure import build_figure
import ecomaps.lib.config_file_parser as config_file_parser
import ecomaps.lib.datasets as datasets
from ecomaps.lib.session_endpoint_data import SessionEndpointData
from ecomaps.lib.status_builder import StatusBuilder
import ecomaps.lib.usage_logger as usage_logger
import ecomaps.lib.viewdataExport as viewdataExport
from ecomaps.controllers.wmsviz import WmsvizController
from ecomaps.services.analysis import AnalysisService
from ecomaps.services.dataset import DatasetService
from ecomaps.services.user import UserService

log = logging.getLogger(__name__)

class ViewdataController(WmsvizController):
    """
    Main controller for the Viewdata application.
    It mainly delegates to the wmsviz controller.
    """
    indexTemplate = "viewdata.html"

    _user_service = None
    _dataset_service = None
    _analysis_service = None

    def __init__(self,
                 user_service=UserService(),
                 dataset_service=DatasetService(),
                 analysis_service=AnalysisService()):

        super(WmsvizController, self).__init__()
        self._user_service = user_service
        self._dataset_service = dataset_service
        self._analysis_service = analysis_service

    def _getConfiguration():
        """ Reads the configuration values.
        """
        statusBuilder = StatusBuilder()
        configuration = statusBuilder.getCurrentStatus('viewdata')
        return configuration

    def _isUserInterfaceFeatureEnabled(configuration, option):
        """ Determines whether one of the user interface configuration options is enabled.
        """
        if configuration['ViewDataUserInterfaceConfig'] is None:
            return False
        else:
            return (('ViewDataUserInterfaceConfig' not in configuration) or
                    (option not in configuration['ViewDataUserInterfaceConfig']) or
                    ('show' not in configuration['ViewDataUserInterfaceConfig'][option]) or
                    configuration['ViewDataUserInterfaceConfig'][option]['show'] == 'true')

    # Get the configuration values (e.g., for server side validation).
    configuration = _getConfiguration()
    enableAddSessionEndpoints = _isUserInterfaceFeatureEnabled(configuration, 'add_session_endpoint')

    def _makeHelpMap():
        """ Reads the help text file and returns it as a dictionary mapping key to help text.
        """
        helpTextConfigParser = config_file_parser.HelpTextConfigParser()
        helpMap = helpTextConfigParser.getHelpText()
        for k, v in helpMap.items():
            log.debug("Help %s=%s" % (k, v))
        return helpMap

    # Read the help text and dataset/endpoint configuration.
    helpMap = _makeHelpMap()
    datasetManager = datasets.createDatasetManager(config, enableAddSessionEndpoints)

    @jsonify
    def get_datasets(self):
        """ In response to an AJAX request, returns the datasets that are children of a specified
        node in the dataset tree.
        """
        try:

            #return self.datasetManager.getDatasets(request, self._get_session_endpoint_data())

            try:
                # Node is purely numeric...will be the root node
                node_id = int(request.params['node'])

                # Initial request for dataset types
                dataset_types = self._dataset_service.get_dataset_types()

                return self.datasetManager.load_dataset_types(dataset_types)

            except ValueError:

                # Request for list of datasets, or endpoint info...
                node = request.params['node']

                if node.startswith('type_'):

                     # Let's trim down to get at the ID value
                    type_id = int(node[len('type_')])
                    username = request.environ['REMOTE_USER']
                    user_obj = self._user_service.get_user_by_username(username)

                    dataset_list = self._dataset_service.get_datasets_for_user(user_obj.id, dataset_type_id=type_id)

                    return self.datasetManager.load_datasets(dataset_list)

                elif node.startswith('ds_'):

                    pass
                    # Get dataset by ID
                    # pass WMS url to

            # 0 = root node
            # if request.params['node'] is not u'0':
            #     # Who's asking for these datasets?
            #     username = request.environ['REMOTE_USER']
            #     user_obj = self._user_service.get_user_by_username(username)
            #
            #     # Now to get the datasets that this user can see
            #     datasets = self._dataset_service.get_datasets_for_user(user_obj.id)


            return self.datasetManager.getDatasets(request, self._get_session_endpoint_data())
        except urllib2.HTTPError, exc:
            log.info("get_datasets request received HTTP error code %d" % exc.code)
            abort(exc.code, 'HTTP error response from WMS server')
        except urllib2.URLError, exc:
            abort(404, exc.reason)

    @jsonify
    def get_layer_data(self):
        """ In response to an AJAX request, returns layer data extracted from the WMS capabilities
        data for the specified layer.
        """

        # Is this a new-style request for a dataset?
        if 'dsid' in request.params or request.params['layerid'].startswith("ds"):

            # Extract the dataset ID
            if 'dsid' in request.params:
                ds_id = request.params['dsid']
            else:
                ds_id = request.params['layerid'][len('ds_'):]

            dataset = self._dataset_service.get_dataset_by_id(ds_id,
                                                              user_id=self.current_user.id)
            return self.get_layers_for_dataset(dataset)

        else:
            # Use the old-style approach
            wmsCapabilities = self.datasetManager.getLayerDataAsDict(request, self._get_session_endpoint_data())
            if wmsCapabilities != None:
                usage_logger.getUsageLogger(request).info('Get WMS capabilities: endpoint "%s" layer "%s"' %
                                                          (wmsCapabilities['getMapUrl'], wmsCapabilities['name']))
            return wmsCapabilities

    def get_layers_for_dataset(self, dataset):
        """ Gets a list of layer information for the given dataset
            @param: dataset- The ecomaps model dataset to get WMS layers for

        """
        layer_list = self.datasetManager.get_ecomaps_layer_data(dataset)

        layer_collection = []

        for layer in layer_list[0]:
            layer_obj = layer.entity.getAsDict()
            layer_obj['data_range_from'] = dataset.data_range_from
            layer_obj['data_range_to'] = dataset.data_range_to
            layer_obj['is_categorical'] = dataset.is_categorical
            layer_collection.append(layer_obj)

        return layer_collection
        #return [layer.entity.getAsDict() for layer in layer_list[0]]

    def layers(self, id):
        """ Returns a view on a dataset's map layers
            @param dataset_id: The ID of the dataset to get the layer data for
        """
        dataset = self._dataset_service.get_dataset_by_id(id,
                                                          user_id=self.current_user.id)

        c.dataset = dataset

        if dataset.dataset_type.type == 'Result':
            c.analysis_id = self._analysis_service.get_analysis_for_result_dataset(dataset.id)

        c.layers = self.get_layers_for_dataset(dataset)

        c.dimensions = []

        # Check for dimensionality
        if c.layers and c.layers[0]['dimensions']:
            c.dimensions = c.layers[0]['dimensions']

        return render('layers.html')

    @jsonify
    def add_session_endpoint(self):
        """ Adds a URL as an endpoint in session scope for the user.
        """
        if self.enableAddSessionEndpoints:
            return self.datasetManager.addSessionEndpoint(request, self._get_session_endpoint_data())
        else:
            redirect(url(controller='viewdata', action='error_window',
                         message='Adding session map services is not enabled.'))

    @jsonify
    def remove_session_endpoint(self):
        """ Removes an endpoint from the user's session scope.
        """
        if self.enableAddSessionEndpoints:
            return self.datasetManager.removeSessionEndpoint(request, self._get_session_endpoint_data())
        else:
            redirect(url(controller='viewdata', action='error_window',
                         message='Removing session map services is not enabled.'))

    @jsonify
    def get_help(self):
        """Returns a help text section.
        """
        if 'help' in request.params:
            section = request.params['help']
            if section in self.helpMap:
                return {'help': self.helpMap[section]}
        return {'help': 'Help not available for this section.'}

    def get_figure(self):
        """Creates and returns a figure.
        """
        log.debug("running viewdata.get_figure")
        
        # Use .copy() on params to get a writeable MultiDict instance
        params = request.params.copy()
        
        log.debug("params = %s" % (params,))
        
        # The response headers must be strings, not unicode, for modwsgi -
        # ensure that the format is a string, omitting any non-ASCII
        # characters.
        format = params.pop('figFormat', 'image/png')
        formatStr = format.encode('ascii', 'ignore')

        # Default to the "viewdata" style for captions.
        if not 'figure-style' in params:
            params['figure-style'] = 'viewdata'

        try:
            finalImage = build_figure(params, self._get_session_endpoint_data())

            buffer = StringIO()
            finalImage.save(buffer, self._pilImageFormats[formatStr])

            response.headers['Content-Type'] = formatStr

            # Remove headers that prevent browser caching, otherwise IE will not
            # allow the image to be saved in its original format.
            if 'Cache-Control' in response.headers:
                del response.headers['Cache-Control']
            if 'Pragma' in response.headers:
                del response.headers['Pragma']

            return buffer.getvalue()
        except Exception, exc:
            response.content_type = 'text/plain'
            return exc.__str__() + '\n'

    @jsonify
    def make_export(self):
        """Generates an export file.
        """
        log.debug("running viewdata.make_export")

        params = request.params.copy()
        if not 'figure-style' in params:
            params['figure-style'] = 'viewdata'

        result = viewdataExport.make_export(params, request.application_url, self.configuration['AnimationOptions'],
                                            self._get_session_endpoint_data())
        if result.success:
            return {'success': True, 'url': request.application_url + '/viewdata/download?file=' + result.fileName}
        else:
            return  {'success': False, 'errorMessage': result.errorMessage}
    
    def get_export(self):
        """Generates and returns an export file.
        """
        log.debug("running viewdata.get_export")

        params = request.params.copy()
        if not 'figure-style' in params:
            params['figure-style'] = 'viewdata'

        result = viewdataExport.make_export(params, request.application_url, status['AnimationOptions'],
                                            self._get_session_endpoint_data())
        if result.success:
            redirect(url(controller='viewdata', action='download', file = result.fileName))
        else:
            response.content_type = 'text/plain'
            return result.errorMessage + '\n'

    def download(self):
        """Downloads a previously generated file.
        """
        log.debug("running viewdata.download")
        if 'file' in request.params:
            return self._send_file_response(request.params['file'])
        else:
            response.content_type = 'text/plain'
            return 'No file to download has been specified.\n'

    def _send_file_response(self, filename):
        """Returns a file's contents as a response.
        Sets a MIME type according to the file extension.
        """
        filepath = os.path.join(viewdataExport.getExportDir(), filename)
        if not os.path.exists(filepath):
            redirect(url(controller='viewdata', action='error_window',
                         message='The file you tried to download is no longer available.'))
        (base, sep, fileExtension) = filename.rpartition('.')
        fileSize = os.path.getsize(filepath)

        mimeTypeMap = {
            'avi': 'video/x-msvideo',
            'flv': 'video/x-flv',
            'mp4': 'video/mp4',
            'mpeg': 'video/mpeg',
            'nc': 'application/cf-netcdf',
            'ogg': 'application/ogg',
            'mov': 'video/quicktime',
            'swf': 'application/x-shockwave-flash',
            'kml': 'application/vnd.google-earth.kml+xml',
            'xml': 'text/xml'}
        mimeType = mimeTypeMap.get(fileExtension, 'application/octet-stream')

        # The response headers must be strings, not unicode, for modwsgi -
        # ensure that the filename is a string, omitting any non-ASCII
        # characters. The name of the file to be downloaded should already
        # conform to this restriction, so this should have no effect other than
        # changing the variable type to str.
        filenameStr = filename.encode('ascii', 'ignore')
        headers = [('Content-Disposition', 'attachment; filename=\"' + filenameStr + '\"'),
                   ('Content-Type', mimeType),
                   ('Content-Length', str(fileSize))]

        fapp = FileApp(filepath, headers=headers)

        return fapp(request.environ, self.start_response)

    def error_window(self):
        """Renders a page containing an error window with a specified message.
        """
        log.debug("running viewdata.error_window")
        if 'message' in request.params:
            c.message = request.params['message']
        else:
            c.message = 'Unknown error'
        return render('viewdata_error.html')

    def _get_session_endpoint_data(self):
        """Finds or creates the session endpoint data object for the user's session.
        """
        try:
            # Check that the session data is accessible.
            session.get('test', None)
            return SessionEndpointData(session)
        except Exception, exc:
            log.error("Error accessing session data: %s" % exc.__str__())
            return None
