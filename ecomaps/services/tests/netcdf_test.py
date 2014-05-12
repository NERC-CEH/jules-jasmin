import unittest
from paste.deploy import appconfig
from ecomaps.config.environment import load_environment
from ecomaps.services.netcdf import EcoMapsNetCdfFile, NetCdfService

__author__ = 'Phil Jenkins (Tessella)'


class EcoMapsNetCdfFileTest(unittest.TestCase):

    def test_coverage_file_can_be_read(self):

        file = EcoMapsNetCdfFile("http://localhost:8080/thredds/dodsC/testAll/Test-New-R-Code-2_2014-02-18T11:05:13.802146.nc")
        self.assertNotEqual(None, file.attributes)
        self.assertNotEqual(None, file.columns)

    def test_result_file_can_be_read(self):

        file = EcoMapsNetCdfFile("http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc")
        self.assertNotEqual(None, file.attributes)
        self.assertNotEqual(None, file.columns)

    def test_service_can_filter_attributes(self):

        cols = ["title", "description"]

        s = NetCdfService()
        attributes = s.get_attributes("http://localhost:8080/thredds/dodsC/testAll/Test-New-R-Code-2_2014-02-18T11:05:13.802146.nc", cols)

        self.assertEqual(len(attributes.keys()), 2)

    def test_get_column_names_returns_expected_names(self):

        s = NetCdfService()
        columns = s.get_variable_column_names("http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc")

        self.assertEqual(columns, ['LandCover'])

    def test_temporal_dataset(self):

        f = EcoMapsNetCdfFile('http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc')
        g=0

    def test_overlay_point_data(self):

        conf = appconfig('config:test.ini', relative_to='.')
        test_conf = load_environment(conf.global_conf, conf.local_conf)

        s= NetCdfService(config=test_conf)
        self.assertNotEqual(None, s.overlay_point_data('http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc'))