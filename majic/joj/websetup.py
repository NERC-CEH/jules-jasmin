#header

import datetime
import os
import pylons.test
from joj.config.environment import load_environment
from joj.model import session_scope, DatasetType, Dataset, Analysis, User, AnalysisCoverageDataset, \
    AnalysisCoverageDatasetColumn, Model, UserLevel, Parameter, ModelRunStatus, NamelistFile, Namelist, CodeVersion
from joj.model.meta import Base, Session
from joj.utils import constants
from websetup_jules_parameters import JulesParameterParser
from websetup_science_configurations import JulesNamelistParser


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
        user.name = 'Phil Jenkins'
        user.first_name = 'Phil'
        user.last_name = 'Jenkins'
        user.username = 'philip.jenkins@tessella.com'
        user.email = 'philip.jenkins@tessella.com'
        user.access_level = "Admin"

        session.add(user)

        user2 = User()
        user2.name = 'Mike Wilson'
        user2.first_name = 'Mike'
        user2.last_name = 'Wilson'
        user2.username = 'mw'
        user2.email = 'mw@ceh.ac.uk'
        user2.access_level = "Admin"

        session.add(user2)

        core_user = User()
        core_user.name = 'core'
        core_user.first_name = 'Core'
        core_user.last_name = ''
        core_user.username = constants.CORE_USERNAME
        core_user.email = ''

        session.add(core_user)

        pointDst = DatasetType()
        pointDst.type = 'Point'

        coverDst = DatasetType()
        coverDst.type = 'Coverage'

        resultDst = DatasetType()
        resultDst.type = 'Result'

        session.add(pointDst)
        session.add(coverDst)
        session.add(resultDst)

        # Sample land coverage map

        # CEH
        ds = Dataset()
        ds.dataset_type = coverDst
        ds.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/wms/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds.name = 'Land Cover Map 2007'
        ds.netcdf_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/LCM2007_25mAggregation/DetailWholeDataset.ncml'
        ds.low_res_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/fileServer/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc'

        # LOCAL
        # ds = Dataset()
        # ds.dataset_type = coverDst
        # ds.wms_url = 'http://localhost:8080/thredds/wms/testAll/LCM2007_GB_1K_DOM_TAR.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        # ds.name = 'Land Cover Map 2007'
        # ds.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc'
        # ds.low_res_url = 'http://localhost:8080/thredds/fileServer/testAll/LCM2007_GB_1K_DOM_TAR.nc'

        session.add(ds)

        # CEH Chess Data
        # chess = Dataset()
        # chess.name = 'CHESS Annual Precipitation'
        # chess.dataset_type = coverDst
        # chess.netcdf_url = 'http://tds-dev1.nerc-lancaster.ac.uk/thredds/dodsC/CHESSDetail/CHESSAnnualTotalPrecip.nc'
        # chess.low_res_url = 'http://tds-dev1.nerc-lancaster.ac.uk/thredds/fileServer/CHESSDetail/CHESSAnnualTotalPrecip.nc'
        # chess.wms_url = 'http://tds-dev1.nerc-lancaster.ac.uk/thredds/wms/CHESSDetail/CHESSAnnualTotalPrecip.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        #

        chess = Dataset()
        chess.name = 'CHESS Annual Precipitation'
        chess.dataset_type = coverDst
        chess.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/CHESSAnnualTotalPrecip.nc'
        chess.low_res_url = 'http://localhost:8080/thredds/fileServer/testAll/CHESSAnnualTotalPrecip.nc'
        chess.wms_url = 'http://localhost:8080/thredds/wms/testAll/CHESSAnnualTotalPrecip.nc?service=WMS&version=1.3.0&request=GetCapabilities'


        session.add(chess)

        # Model that provides the interface to the R code
        model = Model()
        model.name = "LCM Thredds Model"
        model.id = 1
        model.description = "LCM Thredds model written in R"
        model.code_path = "code_root"

        session.add(model)

        # CEH
        ds2 = Dataset()
        ds2.dataset_type = pointDst
        ds2.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/wms/ECOMAPSDetail/ECOMAPSInputLOI01.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds2.netcdf_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc'
        ds2.name = 'Example Point dataset'

        # LOCAL
        # ds2 = Dataset()
        # ds2.dataset_type = pointDst
        # ds2.wms_url = 'http://localhost:8080/thredds/dodsC/testAll/ECOMAPSInputLOI01.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        # ds2.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/ECOMAPSInputLOI01.nc'
        # ds2.name = 'Example Point dataset'

        session.add(ds2)

        level = UserLevel()
        level.name = 'Beginner'
        session.add(level)

        status_created = ModelRunStatus(constants.MODEL_RUN_STATUS_CREATED)
        statuses = [status_created,
                    ModelRunStatus(constants.MODEL_RUN_STATUS_SUBMITTED),
                    ModelRunStatus(constants.MODEL_RUN_STATUS_PENDING),
                    ModelRunStatus(constants.MODEL_RUN_STATUS_RUNNING),
                    ModelRunStatus(constants.MODEL_RUN_STATUS_COMPLETED),
                    ModelRunStatus(constants.MODEL_RUN_STATUS_PUBLISHED),
                    ModelRunStatus(constants.MODEL_RUN_STATUS_FAILED),
                    ModelRunStatus(constants.MODEL_RUN_STATUS_SUBMIT_FAILED)]
        map(session.add, statuses)

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

        jules_parameter_parser = JulesParameterParser()
        namelist_files = jules_parameter_parser.parse_all("docs/Jules/user_guide/html/namelists/", code_version)

        jules_config_parser = JulesNamelistParser()
        jules_config_parser.parse_all(
            "configuration/Jules/scientific_configurations/",
            namelist_files,
            core_user,
            code_version,
            status_created)

        for namelist_file in namelist_files:
            session.add(namelist_file)
