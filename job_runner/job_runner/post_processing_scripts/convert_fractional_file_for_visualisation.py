"""
header
"""
from netCDF4 import Dataset
import os
from sys import argv


class VariableSplitter(object):
    """
    Takes a netCDF file with a variable which has a pseudo dimension
    and splits that variable into an equivalent number of single layer variables.
    """

    def convert(self, in_path, out_path, variable_to_split='frac', variable_prefix='Land Cover Fraction'):
        """
        Convert a netCDF file to have multiple variables (rather than a pseudo dimension)
        :param in_path: File to convert
        :param out_path: Path to output to
        :param variable_to_split: Name of variable to split
        :param variable_prefix: Prefix for created variables
        :return:
        """

        if os.path.exists(out_path):
            os.remove(out_path)
        ds_in = Dataset(in_path, 'r')
        ds_out = Dataset(out_path, 'w')

        # Copy across the latitude, longitude dimensions
        len_lat = len(ds_in.dimensions['Latitude'])
        len_lon = len(ds_in.dimensions['Longitude'])
        ds_out.createDimension('Latitude', len_lat)
        ds_out.createDimension('Longitude', len_lon)

        # Now copy the latitude, longitude variables
        lat_in = ds_in.variables['Latitude']
        datatype = self._get_datatype_string(lat_in)
        latitude = ds_out.createVariable('Latitude', datatype, ('Latitude',))
        latitude[:] = lat_in[:]
        self._copy_attrs(lat_in, latitude)

        lon_in = ds_in.variables['Longitude']
        datatype = self._get_datatype_string(lat_in)
        longitude = ds_out.createVariable('Longitude', datatype, ('Longitude',))
        longitude[:] = lon_in[:]
        self._copy_attrs(lon_in, longitude)

        # Now split the layer we need and copy it over
        long_name = '%s - Index %s'
        var_to_split = ds_in.variables[variable_to_split]
        dims_to_keep = var_to_split.dimensions[1:]
        datatype = self._get_datatype_string(var_to_split)
        for layer_index in range(len(var_to_split)):
            layer_name = long_name % (variable_prefix, str(layer_index + 1))
            layer = ds_out.createVariable(layer_name, datatype, dims_to_keep)
            layer.long_name = layer_name
            layer.missing_value = var_to_split.missing_value
            values = var_to_split[layer_index]
            layer[:] = values

        # Copy across the attributes
        self._copy_attrs(ds_in, ds_out)

    def _copy_attrs(self, cp_from, cp_to):
        for attr in cp_from.ncattrs():
            value = cp_from.getncattr(attr)
            cp_to.setncattr(attr, value)
        return cp_from

    def _get_datatype_string(self, variable):
        return "".join((variable.datatype.kind, str(variable.datatype.itemsize)))


def insert_before_file_extension(path, string):
    """
    Add a string to a path immediately before the file extension
    :param path: File path to modify
    :param string: String to add
    :return:
    """
    file_extens_idx = path.rfind('.')
    return "".join((path[0:file_extens_idx], string, path[file_extens_idx:]))


if __name__ == '__main__':
    USER_EDITED_FRACTIONAL_FILENAME = 'user_edited_land_cover_fractional_file.nc'
    MODIFIED_FOR_VISUALISATION_EXTENSION = '_MODIFIED_FOR_VISUALISATION'
    try:
        file_path = USER_EDITED_FRACTIONAL_FILENAME  # Default is to try to find a user edited file
        if len(argv) > 1:
            file_path = str(argv[1])

        if os.path.exists(file_path):
            vis_path = insert_before_file_extension(file_path, MODIFIED_FOR_VISUALISATION_EXTENSION)
            if not os.path.exists(vis_path):
                frac_converter = VariableSplitter()
                frac_converter.convert(file_path, vis_path)
        exit(0)
    except Exception as e:
        pass
    exit(-1)