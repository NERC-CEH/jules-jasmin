"""
header

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
