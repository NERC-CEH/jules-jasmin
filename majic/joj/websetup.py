# header

import datetime
from joj.model.model_run import ModelRun
import os
import pylons.test
from joj.config.environment import load_environment
from joj.model import session_scope, DatasetType, Dataset, Analysis, User, AnalysisCoverageDataset, \
    AnalysisCoverageDatasetColumn, Model, UserLevel, Parameter, ModelRunStatus, NamelistFile, Namelist, CodeVersion
from joj.model.meta import Base, Session
from joj.utils import constants


def _get_result_image():
    example_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'example_image.txt')

    with open(example_path, 'r') as image_file:
        return image_file.read()


def setup_app(command, conf, vars):
    """Place any commands to setup joj here - currently creating db tables"""

    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    Base.metadata.drop_all(bind=Session.bind)
    Base.metadata.create_all(bind=Session.bind)

    with session_scope(Session) as session:
        user = User()
        user.name = 'John Holt'
        user.first_name = 'John'
        user.last_name = 'Holt'
        user.username = 'johhol'
        user.email = 'john.holt@tessella.com'
        user.access_level = "Admin"

        session.add(user)

        user2 = User()
        user2.name = 'Matt Kendall'
        user2.first_name = 'Matt'
        user2.last_name = 'Kendall'
        user2.username = 'matken'
        user2.email = 'matthew.kendall@tessella.com'
        user2.access_level = "Admin"

        session.add(user2)

        pointDst = DatasetType()
        pointDst.type = 'Point'
        coverDst = DatasetType()
        coverDst.type = 'Coverage'
        coverDst = DatasetType()
        coverDst.type = 'Result'

        session.add(pointDst)
        session.add(coverDst)
        session.add(coverDst)


        level = UserLevel()
        level.name = 'Beginner'
        session.add(level)

        stat_created = ModelRunStatus(constants.MODEL_RUN_STATUS_CREATED)
        stat_submitted = ModelRunStatus(constants.MODEL_RUN_STATUS_SUBMITTED)
        stat_pending = ModelRunStatus(constants.MODEL_RUN_STATUS_PENDING)
        stat_running = ModelRunStatus(constants.MODEL_RUN_STATUS_RUNNING)
        stat_completed = ModelRunStatus(constants.MODEL_RUN_STATUS_COMPLETED)
        stat_published = ModelRunStatus(constants.MODEL_RUN_STATUS_PUBLISHED)
        stat_failed = ModelRunStatus(constants.MODEL_RUN_STATUS_FAILED)
        stat_submit_failed = ModelRunStatus(constants.MODEL_RUN_STATUS_SUBMIT_FAILED)

        map(session.add, [stat_created, stat_submitted, stat_pending, stat_running, stat_completed, stat_published,
                          stat_failed, stat_submit_failed])

        default_code_version = CodeVersion()
        default_code_version.name = conf.local_conf['default_code_version']
        default_code_version.url_base = 'http://www.jchmr.org/jules/documentation/user_guide/vn3.4/'
        default_code_version.is_default = True
        session.add(default_code_version)

        code_version = CodeVersion()
        code_version.name = 'Jules Not Versioned'
        code_version.url_base = 'http://www.jchmr.org/jules/documentation/user_guide/blah'
        code_version.is_default = False
        session.add(code_version)

        timesteps_namelist_file = NamelistFile()
        timesteps_namelist_file.filename = 'timesteps.nml'
        session.add(timesteps_namelist_file)

        timesteps_namelist = Namelist()
        timesteps_namelist.name = 'JULES_TIME'
        timesteps_namelist.namelist_file = timesteps_namelist_file
        session.add(timesteps_namelist)

        parameter = Parameter()
        parameter.default_value = 'None'
        parameter.name = 'timestep_len'
        parameter.name_list_url = 'namelists/timesteps.nml.html#JULES_TIME::timestep_len'
        parameter.type = 'integer'
        parameter.min = 1
        parameter.user_level = level
        parameter.required = True
        parameter.code_versions = [default_code_version]
        parameter.namelist = timesteps_namelist

        session.add(parameter)
        
        ## Add some model runs with datasets

        ds1 = Dataset()
        ds1.name = "Land Cover Map 2007"
        ds1.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/LCM2007_GB_1K_DOM_TAR.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds1.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/LCM2007_GB_1K_DOM_TAR.nc"
        ds1.data_range_from = 1
        ds1.data_range_to = 30
        ds1.is_categorical = 0
        ds1.deleted = 0
        ds1.dataset_type = coverDst
        ds1.is_input = 0
        
        ds2 = Dataset()
        ds2.name = "Surface incident longwave radiation"
        ds2.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/LWdown_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds2.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/LWdown_TEST_190101.nc"
        ds2.data_range_from = 230
        ds2.data_range_to = 350
        ds2.is_categorical = 0
        ds2.deleted = 0
        ds2.dataset_type = coverDst
        ds2.is_input = 1

        mr1 = ModelRun()
        mr1.name = "Nobel-prize winning run"
        mr1.description = "This is a description for a run which is going to win me the nobel prize. I have compared " \
                          "variable X with variable Y and found that..."
        mr1.user = user
        mr1.date_created = datetime.datetime(2014, 2, 5, 16, 51, 12)
        mr1.date_submitted = datetime.datetime(2014, 2, 5, 17, 8, 12)
        mr1.date_started = datetime.datetime(2014, 2, 5, 19, 11, 54)
        mr1.last_status_change = datetime.datetime(2014, 2, 6, 9, 17, 12)
        mr1.status = stat_completed
        mr1.datasets = [ds1, ds2]

        session.add(mr1)

        ## Another Model Run - no datasets needed since failed

        mr2 = ModelRun()
        mr2.name = "Model run for publication in Nature"
        mr2.description = "This is a description for a run which is going to be published in Nature. I have compared " \
                          "variable X with variable Y and found that..."
        mr2.user = user
        mr2.date_created = datetime.datetime(2014, 3, 5, 16, 51, 12)
        mr2.date_submitted = datetime.datetime(2014, 3, 5, 18, 9, 2)
        mr2.date_started = datetime.datetime(2014, 3, 5, 18, 11, 12)
        mr2.last_status_change = datetime.datetime(2014, 3, 6, 1, 9, 2)
        mr2.status = stat_failed

        session.add(mr2)

        mr3 = ModelRun()
        mr3.name = "Model run comparing X and Y"
        mr3.description = "In this model I have done lots of clever science using the data published by"
        mr3.user = user
        mr3.date_created = datetime.datetime(2013, 12, 25, 16, 51, 12)
        mr3.date_submitted = datetime.datetime(2013, 12, 26, 9, 12, 31)
        mr3.date_started = datetime.datetime(2013, 12, 27, 17, 9, 12)
        mr3.last_status_change = datetime.datetime(2013, 12, 27, 17, 9, 12)
        mr3.status = stat_running

        session.add(mr3)

        ## Add another model run with datasets 
        
        ds3 = Dataset()
        ds3.name = "Surface pressure"
        ds3.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/PSurf_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds3.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/PSurf_TEST_190101.nc"
        ds3.data_range_from = 75000
        ds3.data_range_to = 100000
        ds3.is_categorical = 0
        ds3.deleted = 0
        ds3.dataset_type = coverDst
        ds3.is_input = 1
    
        ds4 = Dataset()
        ds4.name = "Near surface specific humidity"
        ds4.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/Qair_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds4.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/Qair_TEST_190101.nc"
        ds4.data_range_from = 0.001
        ds4.data_range_to = 0.0055
        ds4.is_categorical = 0
        ds4.deleted = 0
        ds4.dataset_type = coverDst
        ds4.is_input = 0
      
        ds5 = Dataset()
        ds5.name = "Rainfall rate"
        ds5.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/Rainf_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds5.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/Rainf_TEST_190101.nc"
        ds5.data_range_from = 0
        ds5.data_range_to = 0.0001
        ds5.is_categorical = 0
        ds5.deleted = 0
        ds5.dataset_type = coverDst
        ds5.is_input = 1              
        
        mr4 = ModelRun()
        mr4.name = "My Published Model Run"
        mr4.description = "I've published this model run so that everyone else can see it and use the awesome data " \
                          "I generated"
        mr4.user = user
        mr4.date_created = datetime.datetime(2014, 6, 5, 12, 12, 12)
        mr4.date_submitted = datetime.datetime(2014, 6, 5, 15, 49, 14)
        mr4.date_started = datetime.datetime(2014, 6, 6, 11, 11, 18)
        mr4.last_status_change = datetime.datetime(2014, 6, 12, 12, 13, 14)
        mr4.status = stat_published
        mr4.datasets = [ds3, ds4, ds5]

        session.add(mr4)
        
        ## Add another model run with datasets 
        
        ds6 = Dataset()
        ds6.name = "Snowfall rate"
        ds6.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/Snowf_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds6.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/Snowf_TEST_190101.nc"
        ds6.data_range_from = 0
        ds6.data_range_to = 0.003
        ds6.is_categorical = 0
        ds6.deleted = 0
        ds6.dataset_type = coverDst
        ds6.is_input = 0
        
        ds7 = Dataset()
        ds7.name = "Surface incident shortwave radiation"
        ds7.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/SWdown_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds7.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/SWdown_TEST_190101.nc"
        ds7.data_range_from = 0
        ds7.data_range_to = 0.1
        ds7.is_categorical = 0
        ds7.deleted = 0
        ds7.dataset_type = coverDst
        ds7.is_input = 1
        
        ds8 = Dataset()
        ds8.name = "Near surface air temperature"
        ds8.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/Tair_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds8.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/Tair_TEST_190101.nc"
        ds8.data_range_from = 260
        ds8.data_range_to = 290
        ds8.is_categorical = 0
        ds8.deleted = 0
        ds8.dataset_type = coverDst
        ds8.is_input = 1
        
        ds9 = Dataset()
        ds9.name = "Near surface wind speed"
        ds9.wms_url = "http://127.0.0.1:8080/thredds/wms/dev/Wind_TEST_190101.nc?service=WMS&version=1.3.0&request=GetCapabilities"
        ds9.netcdf_url = "http://127.0.0.1:8080/thredds/dodsC/dev/Wind_TEST_190101.nc"
        ds9.data_range_from = 0
        ds9.data_range_to = 20
        ds9.is_categorical = 0
        ds9.deleted = 0
        ds9.dataset_type = coverDst
        ds9.is_input = 0

        mr5 = ModelRun()
        mr5.name = "Another published model run"
        mr5.description = "This is another published model run belonging to a different user"
        mr5.user = user2
        mr5.date_created = datetime.datetime.now()
        mr5.date_submitted = datetime.datetime.now()
        mr5.date_started = datetime.datetime.now()
        mr5.last_status_change = datetime.datetime.now()
        mr5.status = stat_published
        mr5.datasets = [ds6, ds7, ds8, ds9]

        session.add(mr5)