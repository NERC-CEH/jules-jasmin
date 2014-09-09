"""
# header
"""

import datetime

import os
import pylons.test

from joj.model.model_run import ModelRun
from joj.config.environment import load_environment
from joj.model import session_scope, DatasetType, Dataset, User, UserLevel, ModelRunStatus, CodeVersion, \
    DrivingDataset, DrivingDatasetParameterValue, DrivingDatasetLocation, LandCoverValue, LandCoverRegionCategory, \
    LandCoverRegion
from joj.model.meta import Base, Session
from joj.utils import constants
from joj.model.system_alert_email import SystemAlertEmail
from websetup_chess_driving_dataset import create_chess_driving_data
from websetup_watch_driving_dataset import create_watch_driving_data, WATCH_DRIVING_DATA, WATCH_SOIL_PROPS_FILE, \
    WATCH_FRAC_FILE
from websetup_jules_output_variables import JulesOutputVariableParser
from websetup_jules_parameters import JulesParameterParser
from websetup_science_configurations import JulesNamelistParser
from joj.services.model_run_service import ModelRunService


def _get_result_image():
    example_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'example_image.txt')

    with open(example_path, 'r') as image_file:
        return image_file.read()


def setup_app(command, conf, vars):
    """
    Place any commands to setup joj here - currently creating db tables
    :param command:
    :param conf:
    :param vars:
    :return:
    """

    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    Base.metadata.drop_all(bind=Session.bind)
    Base.metadata.create_all(bind=Session.bind)

    jules_config_parser = JulesNamelistParser()

    with session_scope(Session) as session:
        user = User()
        user.name = 'John Holt'
        user.first_name = 'John'
        user.last_name = 'Holt'
        user.username = 'johhol'
        user.email = 'john.holt@tessella.com'
        user.access_level = "Admin"
        user.storage_quota_in_gb = conf['storage_quota_admin_GB']

        session.add(user)

        user2 = User()
        user2.name = 'Matt Kendall'
        user2.first_name = 'Matt'
        user2.last_name = 'Kendall'
        user2.username = 'matken'
        user2.email = 'matthew.kendall@tessella.com'
        user2.access_level = "Admin"
        user2.storage_quota_in_gb = conf['storage_quota_admin_GB']

        session.add(user2)

        user3 = User()
        user3.name = 'Matt Fry'
        user3.first_name = 'Matt'
        user3.last_name = 'Fry'
        user3.username = 'mfry'
        user3.email = 'mfry@ceh.ac.uk'
        user3.access_level = "Admin"
        user3.storage_quota_in_gb = conf['storage_quota_admin_GB']

        session.add(user3)

        user4 = User()
        user4.name = 'Eleanor Blyth'
        user4.first_name = 'Eleanor'
        user4.last_name = 'Blyth'
        user4.username = 'emb'
        user4.email = 'emb@ceh.ac.uk'
        user4.access_level = "Admin"
        user4.storage_quota_in_gb = conf['storage_quota_admin_GB']

        session.add(user4)

        user5 = User()
        user5.name = 'Sandeep Kaur'
        user5.first_name = 'Sandeep'
        user5.last_name = 'Kaur'
        user5.username = 'sankau'
        user5.email = 'Sandeep.Kaur@tessella.com'
        user5.access_level = "Admin"
        user5.storage_quota_in_gb = conf['storage_quota_admin_GB']

        session.add(user5)

        core_user = User()
        core_user.name = 'System'
        core_user.first_name = 'The'
        core_user.last_name = 'System'
        core_user.username = constants.CORE_USERNAME
        core_user.email = ''
        core_user.storage_quota_in_gb = conf['storage_quota_total_GB']  # Total storage for the group workspace

        session.add(core_user)

        cover_dst = DatasetType(type=constants.DATASET_TYPE_COVERAGE)
        session.add(cover_dst)
        land_cover_frac_dst = DatasetType(type=constants.DATASET_TYPE_LAND_COVER_FRAC)
        session.add(land_cover_frac_dst)
        soil_prop_dst = DatasetType(type=constants.DATASET_TYPE_SOIL_PROP)
        session.add(soil_prop_dst)
        single_cell_dst = DatasetType(type=constants.DATASET_TYPE_SINGLE_CELL)
        session.add(single_cell_dst)
        transects_dst = DatasetType(type=constants.DATASET_TYPE_TRANSECTS)
        session.add(transects_dst)

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
        stat_unknown = ModelRunStatus(constants.MODEL_RUN_STATUS_UNKNOWN)

        map(session.add, [stat_created, stat_submitted, stat_pending, stat_running, stat_completed, stat_published,
                          stat_failed, stat_submit_failed, stat_unknown])

        session.add(SystemAlertEmail(
            code=SystemAlertEmail.GROUP_SPACE_FULL_ALERT,
            sent_frequency_in_s=conf['alert_email_frequency_in_s']))

        default_code_version = CodeVersion()
        default_code_version.name = conf.local_conf['default_code_version']
        default_code_version.url_base = 'http://www.jchmr.org/jules/documentation/user_guide/vn3.4/'
        default_code_version.is_default = True
        session.add(default_code_version)

        #Namelists from docs
        jules_parameter_parser = JulesParameterParser()
        namelist_files = jules_parameter_parser.parse_all("docs/Jules/user_guide/html/namelists/", default_code_version)
        for namelist_file in namelist_files:
            session.add(namelist_file)

        #Output variable from docs
        jules_output_variables_parser = JulesOutputVariableParser()
        output_variables = jules_output_variables_parser.parse("docs/Jules/user_guide/html/output-variables.html")
        session.add_all(output_variables)

        ## Add WATCH 100 Years run
        watch_model_run = jules_config_parser.parse_namelist_files_to_create_a_model_run(
            default_code_version,
            "Watch data run over the length of the data",
            "configuration/Jules/watch",
            "Watch 100 Years Data",
            namelist_files,
            stat_published,
            core_user)
        watch_model_run.date_created = datetime.datetime(2014, 8, 26, 16, 00, 00)
        watch_model_run.date_submitted = datetime.datetime(2014, 8, 26, 16, 00, 00)
        watch_model_run.date_started = datetime.datetime(2014, 8, 26, 16, 00, 00)
        watch_model_run.last_status_change = datetime.datetime(2014, 8, 26, 16, 00, 00)
        watch_model_run.storage_in_mb = 1000

        ancils = [
            [WATCH_SOIL_PROPS_FILE, 'Soil Properties (ancil)', 0, 10, soil_prop_dst],
            [WATCH_FRAC_FILE, 'Land cover map  (ancil)', 0, 10, land_cover_frac_dst]
        ]

        for path, var, name, min, max in WATCH_DRIVING_DATA:
            ds = Dataset()
            ds.name = name
            ds.wms_url = conf.local_conf['thredds.server_url'] \
                          + "wms/model_runs/run1/data/WATCH_2D/driving/" + path + ".ncml"\
                            "?service=WMS&version=1.3.0&request=GetCapabilities"
            ds.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/model_runs/run1/data/WATCH_2D/driving/" + path + ".ncml"
            ds.data_range_from = min
            ds.data_range_to = max
            ds.is_categorical = 0
            ds.deleted = 0
            ds.dataset_type = cover_dst
            ds.is_input = True
            ds.model_run = watch_model_run

        for path, name, min, max, dataset_type in ancils:
            ds = Dataset()
            ds.name = name
            ds.wms_url = conf.local_conf['thredds.server_url'] \
                          + "wms/model_runs/run1/" + path + \
                            "?service=WMS&version=1.3.0&request=GetCapabilities"
            ds.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/model_runs/run1/" + path
            ds.data_range_from = min
            ds.data_range_to = max
            ds.is_categorical = 0
            ds.deleted = 0
            ds.dataset_type = dataset_type
            ds.is_input = True
            ds.model_run = watch_model_run

        outputs = [
            ['gpp_gb_monthly', 'Gridbox gross primary productivity (Monthly)', 0, 100],
            ['rad_net_monthly', 'Surface net radiation of land points (Monthly)', 0, 100],
            ['resp_p_gb_monthly', 'Gridbox plant respiration (Monthly)', 0, 100],
            ['smc_tot_monthly', 'Gridbox total soil moisture in column (Monthly)', 0, 100],
            ['sub_surf_roff_monthly', 'Gridbox sub-surface runoff (Monthly)', 0, 100],
            ['surf_roff_monthly', 'Gridbox surface runoff (Monthly)', 0, 100],
            ['swet_liq_tot_monthly', 'Gridbox unfrozen soil moisture as fraction of saturation (Monthly)', 0, 100]]

        for path, name, min, max in outputs:
            ds = Dataset()
            ds.name = name
            ds.wms_url = conf.local_conf['thredds.server_url'] \
                          + "wms/model_runs/run1/output/majic." + path + ".ncml" + \
                            "?service=WMS&version=1.3.0&request=GetCapabilities"
            ds.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/model_runs/run1/output/majic." + path + ".ncml"
            ds.data_range_from = min
            ds.data_range_to = max
            ds.is_categorical = 0
            ds.deleted = 0
            ds.dataset_type = cover_dst
            ds.is_input = False
            ds.model_run = watch_model_run

        session.add(watch_model_run)

        jules_config_parser.parse_all(
            "configuration/Jules/scientific_configurations/",
            namelist_files,
            core_user,
            default_code_version,
            stat_created)

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
        mr2.error_message = 'Parameters are not correct'
        mr2.storage_in_mb = 100

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
        ds3.wms_url = conf.local_conf['thredds.server_url'] \
                      + "wms/dev/PSurf_TEST_190101.nc" \
                        "?service=WMS&version=1.3.0&request=GetCapabilities"
        ds3.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/dev/PSurf_TEST_190101.nc"
        ds3.data_range_from = 75000
        ds3.data_range_to = 100000
        ds3.is_categorical = 0
        ds3.deleted = 0
        ds3.dataset_type = cover_dst
        ds3.is_input = 1

        ds4 = Dataset()
        ds4.name = "Near surface specific humidity"
        ds4.wms_url = conf.local_conf['thredds.server_url'] \
                      + "wms/dev/Qair_TEST_190101.nc" \
                        "?service=WMS&version=1.3.0&request=GetCapabilities"
        ds4.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/dev/Qair_TEST_190101.nc"
        ds4.data_range_from = 0.001
        ds4.data_range_to = 0.0055
        ds4.is_categorical = 0
        ds4.deleted = 0
        ds4.dataset_type = cover_dst
        ds4.is_input = 0

        ds5 = Dataset()
        ds5.name = "Rainfall rate"
        ds5.wms_url = conf.local_conf['thredds.server_url'] \
                      + "wms/dev/Rainf_TEST_190101.nc" \
                        "?service=WMS&version=1.3.0&request=GetCapabilities"
        ds5.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/dev/Rainf_TEST_190101.nc"
        ds5.data_range_from = 0
        ds5.data_range_to = 0.0001
        ds5.is_categorical = 0
        ds5.deleted = 0
        ds5.dataset_type = cover_dst
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
        mr4.storage_in_mb = 61000

        session.add(mr4)

        ## Add another model run with datasets 

        ds6 = Dataset()
        ds6.name = "Snowfall rate"
        ds6.wms_url = conf.local_conf['thredds.server_url'] \
                      + "wms/dev/Snowf_TEST_190101.nc" \
                        "?service=WMS&version=1.3.0&request=GetCapabilities"
        ds6.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/dev/Snowf_TEST_190101.nc"
        ds6.data_range_from = 0
        ds6.data_range_to = 0.003
        ds6.is_categorical = 0
        ds6.deleted = 0
        ds6.dataset_type = cover_dst
        ds6.is_input = 0

        ds7 = Dataset()
        ds7.name = "Surface incident shortwave radiation"
        ds7.wms_url = conf.local_conf['thredds.server_url'] \
                      + "wms/dev/SWdown_TEST_190101.nc" \
                        "?service=WMS&version=1.3.0&request=GetCapabilities"
        ds7.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/dev/SWdown_TEST_190101.nc"
        ds7.data_range_from = 0
        ds7.data_range_to = 0.1
        ds7.is_categorical = 0
        ds7.deleted = 0
        ds7.dataset_type = cover_dst
        ds7.is_input = 1

        ds8 = Dataset()
        ds8.name = "Near surface air temperature"
        ds8.wms_url = conf.local_conf['thredds.server_url'] \
                      + "wms/dev/Tair_TEST_190101.nc" \
                        "?service=WMS&version=1.3.0&request=GetCapabilities"
        ds8.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/dev/Tair_TEST_190101.nc"
        ds8.data_range_from = 260
        ds8.data_range_to = 290
        ds8.is_categorical = 0
        ds8.deleted = 0
        ds8.dataset_type = cover_dst
        ds8.is_input = 1

        ds9 = Dataset()
        ds9.name = "Near surface wind speed"
        ds9.wms_url = conf.local_conf['thredds.server_url'] \
                      + "wms/dev/Wind_TEST_190101.nc" \
                        "?service=WMS&version=1.3.0&request=GetCapabilities"
        ds9.netcdf_url = conf.local_conf['thredds.server_url'] + "dodsC/dev/Wind_TEST_190101.nc"
        ds9.data_range_from = 0
        ds9.data_range_to = 20
        ds9.is_categorical = 0
        ds9.deleted = 0
        ds9.dataset_type = cover_dst
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
        mr4.storage_in_mb = 1000
        mr5.datasets = [ds6, ds7, ds8, ds9]

        session.add(mr5)

    with session_scope(Session) as session:
        watch_driving_data_name = create_watch_driving_data(conf, cover_dst, land_cover_frac_dst, soil_prop_dst)
        chess_driving_data_name = create_chess_driving_data(conf, cover_dst, land_cover_frac_dst, soil_prop_dst)


    with session_scope(Session) as session:

        driving_ds_3 = DrivingDataset()
        driving_ds_3.name = "QA Driving Data set"
        driving_ds_3.description = "Driving data set used for QA"
        driving_ds_3.geographic_region = 'Global'
        driving_ds_3.temporal_resolution = '3 Hours'
        driving_ds_3.spatial_resolution = 'Half degree'
        driving_ds_3.boundary_lat_north = 90
        driving_ds_3.boundary_lat_south = -90
        driving_ds_3.boundary_lon_west = -180
        driving_ds_3.boundary_lon_east = 180
        driving_ds_3.time_start = datetime.datetime(1979, 1, 1, 0, 0, 0)
        driving_ds_3.time_end = datetime.datetime(1979, 3, 1, 0, 0, 0)
        driving_ds_3.view_order_index = 300
        driving_ds_3.usage_order_index = 100
        driving_ds_3.is_restricted_to_admins = True


        parameters3 = [
            [constants.JULES_PARAM_DRIVE_DATA_START, "'1979-01-01 00:00:00'"],
            [constants.JULES_PARAM_DRIVE_DATA_END, "'2009-12-31 21:00:00'"],
            [constants.JULES_PARAM_DRIVE_DATA_PERIOD, "10800"],
            [constants.JULES_PARAM_DRIVE_FILE, "'data/met_data/driving/%vv_%y4%m2.nc'"],
            [constants.JULES_PARAM_DRIVE_NVARS, "8"],
            [constants.JULES_PARAM_DRIVE_VAR,
             "'pstar'      't'         'q'         'wind'      'lw_down'     'sw_down'     "
             "'tot_rain'        'tot_snow'"],
            [constants.JULES_PARAM_DRIVE_VAR_NAME, "'PSurf'      'Tair'      'Qair'      'Wind'      'LWdown'      "
                                                   "'SWdown'      'Rainf'           'Snowf'"],
            [constants.JULES_PARAM_DRIVE_TPL_NAME, "'PSurf_WFDEI_land'      'Tair_WFDEI_land'      "
                                                   "'Qair_WFDEI_land'      'Wind_WFDEI_land'      'LWdown_WFDEI_land'      'SWdown_WFDEI_land'      "
                                                   "'Rainf_WFDEI_GPCC_land'           'Snowf_WFDEI_land'"],
            [constants.JULES_PARAM_DRIVE_INTERP,
             "'i'          'i'         'i'         'i'         'nb'          'nb'          'nb'              'nb'"],
            [constants.JULES_PARAM_DRIVE_Z1_TQ_IN, "2.0"],
            [constants.JULES_PARAM_DRIVE_Z1_UV_IN, "10.0"],

            [constants.JULES_PARAM_INPUT_GRID_IS_1D, ".true."],
            [constants.JULES_PARAM_INPUT_GRID_DIM_NAME, "'land'"],
            [constants.JULES_PARAM_INPUT_NPOINTS, "67209"],
            [constants.JULES_PARAM_INPUT_TIME_DIM_NAME, "'tstep'"],
            [constants.JULES_PARAM_INPUT_TYPE_DIM_NAME, "'pseudo'"],

            [constants.JULES_PARAM_LATLON_FILE, "'data/met_data/ancils/EI-Halfdeg-land-elevation.nc'"],
            [constants.JULES_PARAM_LATLON_LAT_NAME, "'latitude'"],
            [constants.JULES_PARAM_LATLON_LON_NAME, "'longitude'"],
            [constants.JULES_PARAM_LAND_FRAC_FILE, "'data/met_data/ancils/land_frac.nc'"],
            [constants.JULES_PARAM_LAND_FRAC_LAND_FRAC_NAME, "'land_frac'"],
            [constants.JULES_PARAM_SURF_HGT_ZERO_HEIGHT, ".true."],

            [constants.JULES_PARAM_FRAC_FILE, "'data/met_data/ancils/frac_igbp_watch_0p5deg_capUM6.6_WFDEI.nc'"],
            [constants.JULES_PARAM_FRAC_NAME, "'frac'"],

            [constants.JULES_PARAM_SOIL_PROPS_CONST_Z, ".true."],
            [constants.JULES_PARAM_SOIL_PROPS_FILE,
             "'data/met_data/ancils/soil_igbp_bc_watch_0p5deg_capUM6.6_WFDEI.nc'"],
            [constants.JULES_PARAM_SOIL_PROPS_NVARS, "9"],
            [constants.JULES_PARAM_SOIL_PROPS_VAR,
             "'b'       'sathh'  'satcon'  'sm_sat'  'sm_crit'  'sm_wilt'  'hcap'      'hcon'   'albsoil'"],
            [constants.JULES_PARAM_SOIL_PROPS_VAR_NAME,
             "'bexp'    'sathh'  'satcon'  'vsat'    'vcrit'    'vwilt'    'hcap'      'hcon'   'albsoil'"],

            [constants.JULES_PARAM_INITIAL_NVARS, "8"],
            [constants.JULES_PARAM_INITIAL_VAR,
             "'sthuf' 'canopy' 'snow_tile' 'rgrain' 'tstar_tile' 't_soil' 'cs' 'gs'"],
            [constants.JULES_PARAM_INITIAL_USE_FILE,
             ".false.  .false.  .false.  .false.  .false.  .false.  .false.  .false."],
            [constants.JULES_PARAM_INITIAL_CONST_VAL,
             "0.9     0.0      0.0         50.0     275.0        278.0    10.0 0.0"],
        ]

        model_run_service = ModelRunService()

        for constant, value in parameters3:
            ddpv = DrivingDatasetParameterValue(model_run_service, driving_ds_3, constant, value)
            driving_ds_3.parameter_values.append(ddpv)

        file_template = 'data/met_data/driving/{}.ncml'

        for name in ['PSurf_WFDEI_land', 'Tair_WFDEI_land', 'Qair_WFDEI_land', 'Wind_WFDEI_land', 'LWdown_WFDEI_land',
                     'SWdown_WFDEI_land', 'Rainf_WFDEI_GPCC_land', 'Snowf_WFDEI_land']:
            location = DrivingDatasetLocation()
            location.base_url = file_template.format(name)
            location.dataset_type = cover_dst
            location.driving_dataset = driving_ds_3

        driving_ds_upload = DrivingDataset()
        driving_ds_upload.name = constants.USER_UPLOAD_DRIVING_DATASET_NAME
        driving_ds_upload.description = "Choose this option if you wish to use your own uploaded driving data for a " \
                                        "single cell site"
        driving_ds_upload.view_order_index = 1000
        driving_ds_upload.is_restricted_to_admins = False

        parameters_upload = [

            [constants.JULES_PARAM_INPUT_GRID_NX, "1"],
            [constants.JULES_PARAM_INPUT_GRID_NY, "1"],

            # Default soil properties, hopefully overridden in the background when the user sets the land cover.
            [constants.JULES_PARAM_SOIL_PROPS_NVARS, "9"],
            [constants.JULES_PARAM_SOIL_PROPS_VAR,
             "'b'       'sathh'  'satcon'  'sm_sat'  'sm_crit'  'sm_wilt'  'hcap'      'hcon'   'albsoil'"],
            [constants.JULES_PARAM_SOIL_PROPS_USE_FILE, ".false. .false. .false. .false. .false. .false. .false. "
                                                  ".false. .false."],
            [constants.JULES_PARAM_SOIL_PROPS_CONST_VAL,
             "0.9     0.0      0.0         50.0     275.0        278.0    10.0 0.0"],

            [constants.JULES_PARAM_INITIAL_NVARS, "8"],
            [constants.JULES_PARAM_INITIAL_VAR,
             "'sthuf' 'canopy' 'snow_tile' 'rgrain' 'tstar_tile' 't_soil' 'cs' 'gs'"],
            [constants.JULES_PARAM_INITIAL_USE_FILE,
             ".false.  .false.  .false.  .false.  .false.  .false.  .false.  .false."],
            [constants.JULES_PARAM_INITIAL_CONST_VAL,
             "0.9     0.0      0.0         50.0     275.0        278.0    10.0 0.0"],
        ]

        for constant, value in parameters_upload:
            ddpv = DrivingDatasetParameterValue(model_run_service, driving_ds_upload, constant, value)
            driving_ds_upload.parameter_values.append(ddpv)

        session.add_all([driving_ds_3, driving_ds_upload])

        land_cover_types = {1: 'Broad-leaved Tree', 2: 'Needle-leaved Tree', 3: 'C3 Grass', 4: 'C4 Grass', 5: 'Shrub',
                            6: 'Urban', 7: 'Lake', 8: 'Soil', 9: constants.FRACTIONAL_ICE_NAME}
        for index in land_cover_types:
            land_cover_type = LandCoverValue()
            land_cover_type.index = index
            land_cover_type.name = land_cover_types[index]
            session.add(land_cover_type)

    with session_scope() as session:
        watch_model = session.query(ModelRun).filter(ModelRun.name == watch_model_run.name).one()
        science_config = session.query(ModelRun).filter(ModelRun.name == "EURO4").one()
        driving_dataset = session.query(DrivingDataset).filter(DrivingDataset.name == watch_driving_data_name).one()

        watch_model.science_configuration_id = science_config.id
        watch_model.driving_dataset_id = driving_dataset.id
