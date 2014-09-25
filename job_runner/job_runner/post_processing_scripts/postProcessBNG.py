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

This is a work in prgress it has not run all the way through
"""
import os
from find_points import create_points_file
from combine import combine
from CHESSoutput_add_metadata_and_varCRS_4subset import lastPostProcessCHESS

def convert1Din2DChess(inputFolder, outputFolder, inputFileName, verbose=False):
    """
    Convert 1D data into a 2D grid
    :param inputFolder: folder in which orginal file is stored
    :param outputFolder:  folder to output new file to
    :param inputFileName: filename of the file
    :param verbose: True to print more information on convert
    :return: nothing
    """

    infile_path = os.path.join(inputFolder, inputFileName)
    maskfile = 'data/CHESS/ancils/chess_lat_lon.nc'
    points_file = 'points_' + inputFileName + ".txt"
    remapped_outfile = outputFolder + inputFileName + "mapped"
    create_points_file(infile_path, maskfile, points_file)

    combine(infile_path, points_file, remapped_outfile, 1057, 656)

    lastPostProcessCHESS(inputFolder, outputFolder, inputFileName)

if __name__ == '__main__':
    inputFolder = "/home/johhol/project/jules-jasmin/job_runner/job_runner_test/run/run10/output"
    outputFolder = "/home/johhol/project/jules-jasmin/job_runner/job_runner_test/run/run10/processed"
    inputFileName = "majic.surf_roff_daily.nc"


    convert1Din2DChess(inputFolder, outputFolder, inputFileName, verbose=False)
