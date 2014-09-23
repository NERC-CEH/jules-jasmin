"""
# header
"""

import datetime

import os
import pylons.test

from joj.model.model_run import ModelRun
from joj.config.environment import load_environment
from joj.model import session_scope, DatasetType, Dataset, User, UserLevel, ModelRunStatus, CodeVersion, \
    DrivingDataset, DrivingDatasetParameterValue, LandCoverValue
from joj.model.meta import Base, Session
from joj.utils import constants
from joj.model.system_alert_email import SystemAlertEmail
from utils.utils import insert_before_file_extension
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
        transects_dst = DatasetType(type=constants.DATASET_TYPE_TRANSECT)
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

        land_cover_file = insert_before_file_extension(WATCH_FRAC_FILE, constants.MODIFIED_FOR_VISUALISATION_EXTENSION)
        ancils = [
            [WATCH_SOIL_PROPS_FILE, 'Soil Properties', 0, 10, soil_prop_dst],
            [land_cover_file, 'Land Cover Fractions', 0, 10, land_cover_frac_dst]
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

    with session_scope(Session) as session:
        watch_driving_data_name = create_watch_driving_data(conf, cover_dst, land_cover_frac_dst, soil_prop_dst)
        chess_driving_data_name = create_chess_driving_data(conf, cover_dst, land_cover_frac_dst, soil_prop_dst)


    with session_scope(Session) as session:

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

        model_run_service = ModelRunService()
        for constant, value in parameters_upload:
            ddpv = DrivingDatasetParameterValue(model_run_service, driving_ds_upload, constant, value)
            driving_ds_upload.parameter_values.append(ddpv)

        session.add(driving_ds_upload)

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
