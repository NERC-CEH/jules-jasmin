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

    def convert(self, in_path, out_path, variable_prefix='Land Cover Fraction'):
        """
        Convert a netCDF file to have multiple variables (rather than a pseudo dimension)
        :param in_path: File to convert
        :param out_path: Path to output to
        :param variable_prefix: Prefix for created variables
        :return:
        """

        if os.path.exists(out_path):
            os.remove(out_path)
        ds_in = Dataset(in_path, 'r')
        ds_out = Dataset(out_path, 'w')

        # Copy across the latitude, longitude dimensions
        for key, dim in ds_in.dimensions.iteritems():
            dim_len = len(dim)
            ds_out.createDimension(key, dim_len)

        for var_name, variable in ds_in.variables.iteritems():
            if variable.ndim == 3:
                # Now split the layer we need and copy it over
                long_name = '%s - Index %s'
                var_to_split = ds_in.variables[var_name]
                dims_to_keep = var_to_split.dimensions[1:]
                datatype = self._get_datatype_string(var_to_split)
                for layer_index in range(len(var_to_split)):
                    layer_name = long_name % (variable_prefix, str(layer_index + 1))
                    layer = ds_out.createVariable(layer_name, datatype, dims_to_keep)
                    self._copy_attrs(variable, layer)
                    layer.long_name = layer_name
                    layer[:] = var_to_split[layer_index]

            else:
                datatype = self._get_datatype_string(variable)
                copied_variable = ds_out.createVariable(var_name, datatype, variable.dimensions)
                self._copy_attrs(variable, copied_variable)
                copied_variable[:] = variable[:]

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
            else:
                print "File already exists and has been converted"
        else:
            print "File does not exist: %s " % file_path
        exit(0)
    except Exception as e:
        print e.message
        pass
    exit(-1)