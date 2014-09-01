"""
header
"""
import logging
from netCDF4 import Dataset
import numpy as np
import os
import shutil
from job_runner.utils import constants
from job_runner.services.service_exception import ServiceException
from job_runner.utils.netcdf_utils import NetCdfHelper

log = logging.getLogger(__name__)


class LandCoverEditor(object):
    """
    Edits land cover files
    """

    def __init__(self):
        self.nc_helper = NetCdfHelper()

    def apply_land_cover_action(self, base_file_path, mask_file_path, value, key='frac'):
        """
        Apply a land cover action to a base land cover file.
        :param base_file_path: Path of the base land cover file to edit
        :param mask_file_path: Path of the mask file for the region to apply the action over
        :param value: Land cover value to set the region to
        :param key: The name of the fractional cover variable in the land cover file
        :return:
        """
        log.info("Editing land cover map using mask '%s'- setting land cover value to %s" % (mask_file_path, value))
        base = Dataset(base_file_path, 'r+')
        base_frac = base.variables[key]
        base_frac_array = base_frac[:, :, :]
        base_mask = base_frac[:, :, :].mask

        region = Dataset(mask_file_path, 'r')
        region_frac = region.variables[key]
        region_mask = region_frac[:, :]

        if not base_frac.shape[1:] == region_frac.shape:
            log.exception("Could not apply land cover edit: the mask file '%s' "
                          "was the wrong shape for the land cover map." % mask_file_path)
            raise ServiceException("Could not apply land cover edit: the mask file was the wrong "
                                   "shape for the land cover map.")
        combined_mask = base_mask | region_mask
        base_frac_array.mask = combined_mask
        base_frac_array.harden_mask()

        n_pseudo = base_frac.shape[0]
        for pseudo in np.arange(n_pseudo):
            if pseudo == value - 1:
                base_frac_array[pseudo, :, :] = 1.0
            else:
                base_frac_array[pseudo, :, :] = 0.0
        base_frac_array.soften_mask()
        base_frac_array.mask = base_mask
        base_frac[:, :, :] = base_frac_array

        region.close()
        base.close()

    def apply_single_point_fractional_cover(self, base_file_path, fractional_cover, lat, lon, key='frac'):
        """
        Change the fractional land cover at a single point in the file
        :param base_file_path: Path of the base land cover file to edit
        :param fractional_cover: List of fractional cover values to set the point to
        :param lat: Latitude of point to edit
        :param lon: Longitude of point to edit
        :param key: The name of the fractional cover variable in the land cover file
        :raise ServiceException:
        """
        base = Dataset(base_file_path, 'r+')
        base_frac = base.variables[key]
        base_frac_array = base_frac[:, :, :]

        # Get the indices of the latitude and longitude position
        lat_key = self.nc_helper.look_for_key(base.variables.keys(), constants.NETCDF_LATITUDE)
        lon_key = self.nc_helper.look_for_key(base.variables.keys(), constants.NETCDF_LONGITUDE)
        if lat_key is None or lon_key is None:
            log.exception("Could not apply land cover edit: could not identify latitude and longitude variables")
            raise ServiceException("Could not apply land cover edit: could not identify "
                                   "latitude and longitude variables")
        lat_index = self.nc_helper.get_closest_value_index(base.variables[lat_key][:], lat)
        lon_index = self.nc_helper.get_closest_value_index(base.variables[lon_key][:], lon)

        n_pseudo = base_frac.shape[0]
        if n_pseudo != len(fractional_cover):
            log.exception("Could not apply land cover edit: the number of fractional values supplied did not match "
                          "the number of types in the netCDF file.")
            raise ServiceException("Could not apply land cover edit: the number of fractional values supplied did not "
                                   "match the number of types in the netCDF file.")
        for pseudo in np.arange(n_pseudo):
            base_frac_array[pseudo, lat_index, lon_index] = fractional_cover[pseudo]
        base_frac[:, :, :] = base_frac_array
        base.close()

    def copy_land_cover_base_map(self, base_file_name, run_directory):
        """
        Create a copy of the base land cover map in the run directory
        :param base_file_name: the filename of the base land cover map
        :param run_directory: The run directory
        :return: The path of the copied file
        """
        base_file_path = os.path.join(run_directory, base_file_name)
        dest_file_path = os.path.join(run_directory, constants.USER_EDITED_FRACTIONAL_FILENAME)
        shutil.copyfile(base_file_path, dest_file_path)
        return dest_file_path