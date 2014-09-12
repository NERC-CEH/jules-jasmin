"""
header
"""
import urllib
import datetime

from decorator import decorator
from hamcrest import *
from pylons import config

from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.tests import TestController


@decorator
def skip_if_thredds_down(func, self, *args, **kwargs):
    """
    Decorator to skip a method if the THREDDS server is not running
    :param func:
    :param args:
    :param kwargs:
    :return:
"""
    if self.is_thredds_available:
        return func(self, *args, **kwargs)
    else:
        raise self.skipTest("Couldn't connect to THREDDS Server")


class BaseDapClientTest(TestController):
    def __init__(self, *args, **kwargs):
        super(BaseDapClientTest, self).__init__(*args, **kwargs)
        try:
            code = urllib.urlopen(config['thredds.server_url']).getcode()
            self.is_thredds_available = code == 200
        except:
            self.is_thredds_available = False
        self.dap_client_factory = DapClientFactory()

    @classmethod
    def setUpClass(cls):
        config['run_in_test_mode'] = "false"  # Deactivate 'test mode' so we can make real calls to THREDDS
        assert_that(config['run_in_test_mode'], is_("false"))


# noinspection PyArgumentList
class TestBaseDapClientOnWatchData(BaseDapClientTest):
    @skip_if_thredds_down
    def setUp(self):
        test_dataset = "/dodsC/model_runs/data/WATCH_2D/driving/PSurf_WFD/PSurf_WFD_190101.nc"
        url = config['thredds.server_url'] + test_dataset
        self.dap_client = self.dap_client_factory.get_dap_client(url)

    def test_GIVEN_dataset_WHEN_get_longname_THEN_longname_returned(self):
        longname = self.dap_client.get_longname()
        assert_that(longname, is_("Surface pressure"))

    def test_GIVEN_dataset_WHEN_get_data_range_THEN_data_range_returned(self):
        range = self.dap_client.get_data_range()
        assert_that(range, is_([47567.066, 106457.453]))

    def test_GIVEN_dataset_WHEN_get_variable_units_THEN_units_correctly_returned(self):
        units = self.dap_client.get_variable_units()
        assert_that(units, is_("Pa"))

    def test_GIVEN_datetime_exactly_matches_a_datapoint_WHEN_get_time_immediately_after_THEN_that_time_returned(self):
        time = datetime.datetime(1901, 1, 1)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(time))

    def test_GIVEN_datetime_not_a_datapoint_WHEN_get_time_immediately_after_THEN_next_time_returned(self):
        time = datetime.datetime(1901, 1, 1, 13, 14, 15)
        expected_time = datetime.datetime(1901, 1, 1, 15, 0, 0)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(expected_time))

    def test_GIVEN_datetime_before_first_datapoint_WHEN_get_time_immediately_after_THEN_first_time_returned(self):
        #The first data point in this set is at 1901-01-01 00:00
        time = datetime.datetime(1800, 1, 1)
        expected_time = datetime.datetime(1901, 1, 1)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(expected_time))

    def test_GIVEN_datetime_after_last_datapoint_WHEN_get_time_immediately_after_THEN_None_returned(self):
        #The last data point in this set is at 1901-01-31 12:00
        time = datetime.datetime(2000, 1, 1)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(None))

    def test_GIVEN_datetime_exactly_matches_a_datapoint_WHEN_get_time_immediately_before_THEN_that_time_returned(self):
        time = datetime.datetime(1901, 1, 5)
        closest_time = self.dap_client.get_time_immediately_before(time)
        assert_that(closest_time, is_(time))

    def test_GIVEN_datetime_not_a_datapoint_WHEN_get_time_immediately_before_THEN_previous_time_returned(self):
        time = datetime.datetime(1901, 1, 1, 13, 14, 15)
        expected_time = datetime.datetime(1901, 1, 1, 12, 0, 0)
        closest_time = self.dap_client.get_time_immediately_before(time)
        assert_that(closest_time, is_(expected_time))

    def test_GIVEN_datetime_before_first_datapoint_WHEN_get_time_immediately_before_THEN_None_returned(self):
        #The first data point in this set is at 1901-01-01 00:00
        time = datetime.datetime(1800, 1, 1)
        closest_time = self.dap_client.get_time_immediately_before(time)
        assert_that(closest_time, is_(None))

    def test_GIVEN_datetime_after_last_datapoint_WHEN_get_time_immediately_before_THEN_None_returned(self):
        #The last data point in this set is at 1901-01-31 12:00
        time = datetime.datetime(2000, 1, 1)
        expected_time = datetime.datetime(1901, 1, 31, 21, 0, 0)
        closest_time = self.dap_client.get_time_immediately_before(time)
        assert_that(closest_time, is_(expected_time))

    def test_GIVEN_lat_lon_match_datapoint_exactly_WHEN_get_closest_lat_lon_THEN_that_datapoint_returned(self):
        lat, lon = 51.75, -0.25
        returned_lat, returned_lon = self.dap_client.get_closest_lat_lon(lat, lon)
        assert_that(returned_lat, is_(51.75))
        assert_that(returned_lon, is_(-0.25))

    def test_GIVEN_lat_lon_not_a_datapoint_WHEN_get_closest_lat_lon_THEN_closest_datapoint_returned(self):
        lat, lon = 51.99, -0.31
        returned_lat, returned_lon = self.dap_client.get_closest_lat_lon(lat, lon)
        assert_that(returned_lat, is_(51.75))
        assert_that(returned_lon, is_(-0.25))

    def test_GIVEN_lat_lon_outside_of_grid_WHEN_get_closest_lat_lon_THEN_closest_datapoint_in_grid_returned(self):
        lat, lon = 90, 360
        returned_lat, returned_lon = self.dap_client.get_closest_lat_lon(lat, lon)
        assert_that(returned_lat, is_(83.75))
        assert_that(returned_lon, is_(179.75))

    def test_GIVEN_location_and_time_in_grid_WHEN_get_data_at_THEN_correct_data_returned(self):
        lat, lon = 51.75, -0.25
        time = datetime.datetime(1901, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, is_(102080.1875))

    def test_GIVEN_location_outside_grid_WHEN_get_data_at_THEN_missing_value_returned(self):
        lat, lon = 90, 360
        time = datetime.datetime(1901, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, is_(-9999.99))

    def test_GIVEN_time_outside_range_WHEN_get_data_at_THEN_closest_value_returned(self):
        lat, lon = 51.75, -0.25
        time = datetime.datetime(1066, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, is_(102080.1875))

    def test_GIVEN_already_got_data_at_a_point_WHEN_get_data_at_different_point_THEN_new_data_returned(self):
        # Testing that the cache is updated if we have moved lat / lon but not time.
        lat, lon = 51.75, -0.25
        time = datetime.datetime(1901, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, is_(102080.1875))

        lat, lon = 41.75, -0.25
        time = datetime.datetime(1901, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, is_(97743.3984375))

    def test_GIVEN_nothing_WHEN_get_timestamps_THEN_timestamps_returned(self):
        timestamps = self.dap_client.get_timestamps()
        assert_that(len(timestamps), is_(248))
        start_time = datetime.datetime(1901, 1, 1)
        end_time = datetime.datetime(1901, 1, 31, 21, 0)
        assert_that(timestamps[0], is_(start_time))
        assert_that(timestamps[-1], is_(end_time))


# noinspection PyArgumentList
class TestBaseDapClientOnCHESSData(BaseDapClientTest):
    @skip_if_thredds_down
    def setUp(self):
        test_dataset = "/dodsC/model_runs/data/CHESS/driving/chess_dtr_copy.ncml"
        url = config['thredds.server_url'] + test_dataset
        self.dap_client = self.dap_client_factory.get_dap_client(url)

    def test_GIVEN_dataset_WHEN_get_longname_THEN_longname_returned(self):
        longname = self.dap_client.get_longname()
        assert_that(longname, is_("Daily temperature range"))

    def test_GIVEN_dataset_WHEN_get_variable_units_THEN_units_correctly_returned(self):
        units = self.dap_client.get_variable_units()
        assert_that(units, is_("K"))

    def test_GIVEN_datetime_exactly_matches_a_datapoint_WHEN_get_time_immediately_after_THEN_that_time_returned(self):
        time = datetime.datetime(1961, 1, 1)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(time))

    def test_GIVEN_datetime_not_a_datapoint_WHEN_get_time_immediately_after_THEN_next_time_returned(self):
        time = datetime.datetime(1961, 1, 1, 13, 14, 15)
        expected_time = datetime.datetime(1961, 1, 2, 0, 0, 0)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(expected_time))

    def test_GIVEN_datetime_before_first_datapoint_WHEN_get_time_immediately_after_THEN_first_time_returned(self):
        #The first data point in this set is at 1901-01-01 00:00
        time = datetime.datetime(1800, 1, 1)
        expected_time = datetime.datetime(1961, 1, 1)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(expected_time))

    def test_GIVEN_datetime_after_last_datapoint_WHEN_get_time_immediately_after_THEN_None_returned(self):
        #The last data point in this set is at 1901-01-31 12:00
        time = datetime.datetime(2000, 1, 1)
        closest_time = self.dap_client.get_time_immediately_after(time)
        assert_that(closest_time, is_(None))

    def test_GIVEN_datetime_exactly_matches_a_datapoint_WHEN_get_time_immediately_before_THEN_that_time_returned(self):
        time = datetime.datetime(1961, 1, 5)
        closest_time = self.dap_client.get_time_immediately_before(time)
        assert_that(closest_time, is_(time))

    def test_GIVEN_lat_lon_match_datapoint_exactly_WHEN_get_closest_lat_lon_THEN_that_datapoint_returned(self):
        lat, lon = 50.273550469933824, -6.211878376550269
        returned_lat, returned_lon = self.dap_client.get_closest_lat_lon(lat, lon)
        assert_that(returned_lat, is_(50.273550469933824))
        assert_that(returned_lon, is_(-6.211878376550269))

    def test_GIVEN_lat_lon_not_a_datapoint_WHEN_get_closest_lat_lon_THEN_closest_datapoint_returned(self):
        lat, lon = 50.2738, -6.2117
        returned_lat, returned_lon = self.dap_client.get_closest_lat_lon(lat, lon)
        assert_that(returned_lat, is_(50.273550469933824))
        assert_that(returned_lon, is_(-6.211878376550269))

    def test_GIVEN_lat_lon_outside_of_grid_WHEN_get_closest_lat_lon_THEN_closest_datapoint_in_grid_returned(self):
        lat, lon = 0, -40
        returned_lat, returned_lon = self.dap_client.get_closest_lat_lon(lat, lon)
        assert_that(returned_lat, is_(49.76680723189604))
        assert_that(returned_lon, is_(-7.557159842082696))

    def test_GIVEN_location_and_time_in_grid_WHEN_get_data_at_THEN_correct_data_returned(self):
        # point at (60, 200)
        lat, lon = 50.405754059495266, -4.815923234749663
        time = datetime.datetime(1961, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, close_to(5.2, 0.001))

    def test_GIVEN_location_outside_grid_WHEN_get_data_at_THEN_missing_value_returned(self):
        lat, lon = 90, 360
        time = datetime.datetime(1961, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, close_to(-99999.0, 0.001))

    def test_GIVEN_time_outside_range_WHEN_get_data_at_THEN_closest_value_returned(self):
        lat, lon = 50.405754059495266, -4.815923234749663
        time = datetime.datetime(1066, 1, 1)
        data = self.dap_client.get_data_at(lat, lon, time)
        assert_that(data, close_to(5.2, 0.001))

# noinspection PyArgumentList
class TestGraphingDapClient(BaseDapClientTest):

    @skip_if_thredds_down
    def setUp(self):
        test_dataset = "/dodsC/model_runs/data/WATCH_2D/driving/PSurf_WFD/PSurf_WFD_190101.nc"
        url = config['thredds.server_url'] + test_dataset
        self.dap_client = self.dap_client_factory.get_graphing_dap_client(url)

    def test_GIVEN_data_at_latlon_WHEN_get_graph_data_THEN_correct_data_dictionary_returned(self):
        lat, lon = 51.75, -0.25  # 215, 359
        time = datetime.datetime(1901, 1, 1)
        data = self.dap_client.get_graph_data(lat, lon, time)
        assert_that(data['lat'], is_(lat))
        assert_that(data['lon'], is_(lon))
        assert_that(data['label'], is_("Surface pressure (Pa) @ 51.75, -0.25"))
        assert_that(data['xmin'], is_(-2177452800000.0))  # Milliseconds since the UNIX epoch
        assert_that(data['xmax'], is_(-2174785200000.0))  # Milliseconds since the UNIX epoch
        assert_that(data['ymin'], is_(98193.515625))
        assert_that(data['ymax'], is_(102379.203125))
        assert_that(len(data['data']), is_(248))
        assert_that(data['data'][0], is_([-2177452800000, 102080.1875]))
        assert_that(data['data'][247], is_([-2174785200000, 99755.59375]))
        assert_that(data['data'][123], is_([-2176124400000, 99523.140625]))

    def test_GIVEN_missing_values_at_latlon_WHEN_get_graph_data_THEN_nones_returned(self):
        lat, lon = 50, -30  # Sea
        time = datetime.datetime(1901, 1, 1)
        data = self.dap_client.get_graph_data(lat, lon, time)
        assert_that(data['lat'], is_(lat))
        assert_that(data['lon'], is_(lon))
        assert_that(len(data['data']), is_(248))
        for datum in data['data']:
            assert_that(datum[1], is_(None))

    def test_GIVEN_latlon_outside_grid_WHEN_get_graph_data_THEN_nones_returned(self):
        lat, lon = 90, -32.25  # Out of grid (North of greenland)
        time = datetime.datetime(1901, 1, 1)
        data = self.dap_client.get_graph_data(lat, lon, time)
        assert_that(data['lat'], is_(lat))
        assert_that(data['lon'], is_(lon))
        assert_that(len(data['data']), is_(248))
        for datum in data['data']:
            assert_that(datum[1], is_(None))

    def test_GIVEN_npoints_and_time_WHEN_get_graph_data_THEN_subset_of_points_returned(self):
        lat, lon = 51.75, -0.25  # 215, 359
        time = datetime.datetime(1901, 01, 15)
        data = self.dap_client.get_graph_data(lat, lon, time, npoints=10)
        assert_that(len(data['data']), is_(10))
        data_at_time = [self.dap_client._get_millis_since_epoch(3888000.0), 99770.203125]
        assert_that(data['data'][4], is_(data_at_time))
        data_at_start = [self.dap_client._get_millis_since_epoch(3844800.0), 99984.34375]
        assert_that(data['data'][0], is_(data_at_start))
        data_at_end = [self.dap_client._get_millis_since_epoch(3942000.0), 100408.203125]
        assert_that(data['data'][9], is_(data_at_end))

    def test_GIVEN_npoints_and_time_at_start_of_data_WHEN_get_graph_data_THEN_subset_of_points_returned(self):
        lat, lon = 51.75, -0.25  # 215, 359
        time = datetime.datetime(1901, 01, 01)
        data = self.dap_client.get_graph_data(lat, lon, time, npoints=10)
        assert_that(len(data['data']), is_(6))
        data_at_start = [self.dap_client._get_millis_since_epoch(2678400.0), 102080.1875]
        assert_that(data['data'][0], is_(data_at_start))
        data_at_end = [self.dap_client._get_millis_since_epoch(2732400.0), 101583.6875]
        assert_that(data['data'][5], is_(data_at_end))

    def test_GIVEN_npoints_and_time_at_end_of_data_WHEN_get_graph_data_THEN_subset_of_points_returned(self):
        lat, lon = 51.75, -0.25  # 215, 359
        time = datetime.datetime(1901, 01, 31, 21, 0)
        data = self.dap_client.get_graph_data(lat, lon, time, npoints=10)
        assert_that(len(data['data']), is_(5))
        data_at_start = [self.dap_client._get_millis_since_epoch(5302800.0), 99889.390625]
        assert_that(data['data'][0], is_(data_at_start))
        data_at_end = [self.dap_client._get_millis_since_epoch(5346000.0), 99755.59375]
        assert_that(data['data'][4], is_(data_at_end))


# noinspection PyArgumentList
class TestLandCoverDapClient(BaseDapClientTest):

    @skip_if_thredds_down
    def setUp(self):
        test_dataset = "/dodsC/model_runs/data/WATCH_2D/ancils/frac_igbp_watch_0p5deg_capUM6.6_2D.nc"
        url = config['thredds.server_url'] + test_dataset
        self.dap_client = self.dap_client_factory.get_land_cover_dap_client(url, key='frac')

    def test_GIVEN_location_WHEN_get_fractional_cover_THEN_fractional_cover_returned(self):
        lat, lon = 51.75, -0.25  # 215, 359
        expected_cover = [0.010219395160675049, 0.0, 0.4611019790172577, 0.034402914345264435,
                          0.0, 0.36932751536369324, 0.0, 0.12494818866252899, 0.0]
        returned_cover = self.dap_client.get_fractional_cover(lat, lon)
        assert_that(returned_cover, is_(expected_cover))

    def test_GIVEN_location_outside_range_WHEN_get_fractional_cover_THEN_missing_values_returned(self):
        lat, lon = 90, 360  # 215, 359
        expected_cover = 9 * [-9999.99]
        returned_cover = self.dap_client.get_fractional_cover(lat, lon)
        assert_that(returned_cover, is_(expected_cover))


# noinspection PyArgumentList
class TestSoilPropsDapClient(BaseDapClientTest):

    @skip_if_thredds_down
    def setUp(self):
        test_dataset = "/dodsC/model_runs/data/WATCH_2D/ancils/soil_igbp_bc_watch_0p5deg_capUM6.6_2D.nc"
        url = config['thredds.server_url'] + test_dataset
        self.dap_client = self.dap_client_factory.get_soil_properties_dap_client(url)

    def test_GIVEN_location_WHEN_get_soil_properties_THEN_soil_properties_returned(self):
        lat, lon = 51.75, -0.25  # 215, 359
        expected_soil_props = {
            'albsoil': 0.1389661282300949,
            'bexp': 8.749199867248535,
            'csoil': 12.100000381469727,
            'hcap': 1105759.25,
            'hcon': 0.21882377564907074,
            'satcon': 0.0035789860412478447,
            'sathh': 0.1827763468027115,
            'vcrit': 0.3086773455142975,
            'vsat': 0.43060800433158875,
            'vwilt': 0.1995505690574646
        }
        returned_soil_props = self.dap_client.get_soil_properties(lat, lon)
        assert_that(len(returned_soil_props), is_(10))
        assert_that(returned_soil_props, has_entries(expected_soil_props))
