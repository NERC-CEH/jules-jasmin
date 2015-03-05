"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

This is a work in progress it has not run all the way through
"""
import os
from find_points import create_points_file
from combine import combine
from CHESSoutput_add_metadata_and_varCRS_4subset import lastPostProcessCHESS

def convert1Din2DChess(inputFolder, outputFolder, inputFileName, verbose=False):
    """
    Convert 1D data into a 2D grid
    :param inputFolder: folder in which original file is stored
    :param outputFolder:  folder to output new file to
    :param inputFileName: filename of the file
    :param verbose: True to print more information on convert
    :return: nothing
    """

    infile_path = os.path.join(inputFolder, inputFileName)
    output_file_path = os.path.join(outputFolder, inputFileName)
    maskfile = 'data/CHESS/ancils/chess_lat_lon.nc'
    points_file = 'points_' + inputFileName + ".txt"
    remapped_outfile = os.path.join(outputFolder, inputFileName + "mapped")
    create_points_file(infile_path, maskfile, points_file)

    combine(infile_path, points_file, remapped_outfile, 1057, 656)

    lastPostProcessCHESS(remapped_outfile, output_file_path)

if __name__ == '__main__':
    run_dir="/home/matken/PycharmProjects/majic/jules-jasmin/job_runner/job_runner_test/run/chess_run"
    os.chdir(run_dir)
    inputFolder = os.path.join(run_dir, "output")
    outputFolder = os.path.join(run_dir, "processed")
    inputFileName = "majic.ftl_gb_hourly.1961.nc"


    convert1Din2DChess(inputFolder, outputFolder, inputFileName, verbose=False)
