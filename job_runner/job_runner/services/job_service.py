"""
# Header
"""
import glob

import os
from pylons import config
import subprocess
import re
from job_runner.utils.constants import *
from job_runner.model.log_file_parser import LogFileParser
from job_runner.model.bjobs_parser import BjobsParser
from joj.utils.constants import JULES_PARAM_POINTS_FILE
from joj.utils.f90_helper import python_to_f90_str


class ServiceError(Exception):
    """
    Exception class for when the service has a problem
    """
    def __init__(self, message):
        super(ServiceError, self).__init__()
        self.message = message


class JobService(object):
    """
    Service for managing job queries
    """

    def __init__(self, valid_code_versions=VALID_CODE_VERSIONS):
        """
        Constructor setups up valid code versions

        :param valid_code_versions: a dictionary of valid code versions and script files, defaults to constants
        """
        self._valid_code_version = valid_code_versions

    def exists_run_dir(self, model_run_id):
        """
        Checks that the model run directory exists
        :param model_run_id: the model run id
        :return:treu if it exists, false otherwise
        """
        return os.path.exists(self.get_run_dir(model_run_id))

    def get_run_dir(self, model_run_id):
        """
        Get the run directory
        :param model_run_id: the model run id
        :return: the run directory
        """
        #ensure that the model id is a number so it can not possible contain path elements
        model_run_id_dir = str(model_run_id)
        assert(model_run_id_dir.isdigit())
        run_directory = os.path.join(config['run_dir'], 'run%s' % model_run_id_dir)
        return run_directory

    def get_bsub_id(self, model_run_dir):
        """
        Read the bsub id from the file in the model run directory
        :param model_run_dir: the model run directory
        :return: the id or None if the file can not be read
        """
        file_path = os.path.join(model_run_dir, FILENAME_BSUB_ID)
        f = open(file_path, 'r')
        return int(f.read())

    def write_bsub_id(self, model_run_dir, bsub_id):
        """
        Write the bsub id to the bsub id file in the model run directory
        :param model_run_dir: the model run directory
        :param bsub_id: the do to write
        :return: nothing
        """
        file_path = os.path.join(model_run_dir, FILENAME_BSUB_ID)
        f = open(file_path, 'w')
        f.write(bsub_id)
        f.close()

    def get_output_log_result(self, run_dir):
        """
        Get the result of the Jules by looking at the log
        :param run_dir: the run directory to get the file from
        :return: log file parser
        """
        file_path = os.path.join(run_dir, FILENAME_OUTPUT_LOG)
        if not os.path.exists(file_path):
            raise ServiceError(ERROR_MESSAGE_NO_LOG_FILE)
        f = open(file_path, 'r')
        log_file_parser = LogFileParser(f)
        log_file_parser.parse()
        return log_file_parser

    def submit(self, model_run):
        """
        submit a job to the lsf framework
        :param model_run: the model run to submit
        :return: job id
        :exception ServiceError: if there is a problem submitting the job
        """
        if self.exists_run_dir(model_run[JSON_MODEL_RUN_ID]):
            raise ServiceError("Run directory already exists for model run")

        run_directory = self.get_run_dir(model_run[JSON_MODEL_RUN_ID])

        #create run directory
        os.mkdir(run_directory)

        #create output dir
        os.mkdir(os.path.join(run_directory, OUTPUT_DIR))

        #create softlinks
        for src in glob.glob(os.path.join(config['jules_files_to_softlink_dir'], '*')):
            os.symlink(src, os.path.join(run_directory, os.path.basename(src)))

        self._create_parameter_files(run_directory, model_run)

        for namelist_file in model_run[JSON_MODEL_NAMELIST_FILES]:
            self._create_namelist_file(namelist_file, run_directory)

        bsub_id = self._submit_job(model_run[JSON_MODEL_CODE_VERSION], run_directory)

        self.write_bsub_id(run_directory, bsub_id)

        return bsub_id

    def _submit_job(self, code_version, run_directory):
        """
        Submit the job
        :param code_version: the code version
        :param run_directory: the run directory to use
        :return: the job id
        :exception ServiceError: when there is a problem submiting the job
        """
        try:
            script = os.path.join(run_directory, self._valid_code_version[code_version])
            output = subprocess.check_output([script], stderr=subprocess.STDOUT, cwd=run_directory)
            #Job <337912> is submitted to default queue <lotus>
            match = re.search('Job <(\d*)>', output)
            if match is None:
                raise ServiceError('Problem in job script. "%s"' % output)
            return match.group(1)

        except subprocess.CalledProcessError, ex:
            raise ServiceError('Problem running job script. "%s"' % ex.output)
        except Exception, ex:
            raise ServiceError('Problem submitting job script. "%s"' % ex.message)

    def _create_namelist_file(self, namelist_file, run_directory):
        """
        create the name list file
        :param namelist_file: the name list file to create
        :param run_directory:  the directory to create the file in
        :return: nothing
        """
        f = open(os.path.join(run_directory, namelist_file[JSON_MODEL_NAMELIST_FILE_FILENAME]), 'w')

        for namelist in sorted(
                namelist_file[JSON_MODEL_NAMELISTS],
                key=lambda namelist_to_sort: namelist_to_sort[JSON_MODEL_NAMELIST_INDEX]):
            self._write_namelist(namelist, f)
        f.close()

    def _write_namelist(self, namelist, f):
        """
        Write the name list to the file
        :param namelist: the name list to write
        :param f: the file handle to write to
        :return: nothing
        """
        f.write('&%s\n' % namelist[JSON_MODEL_NAMELIST_NAME])

        lines = []
        for parameter_name, parameter_value in namelist[JSON_MODEL_PARAMETERS].iteritems():
            lines.append('  {name} = {value}'.format(name=parameter_name, value=parameter_value))

        f.write(',\n'.join(lines))

        f.write('\n/\n')

    def queued_jobs_status(self):
        """
        Get the status of jobs in the job queue
        :return: the status
        """
        try:
            output = subprocess.check_output([config['run_bjobs_command']], stderr=subprocess.STDOUT)
            bjobs_parser = BjobsParser(output.splitlines())
            return bjobs_parser.parse()

        except subprocess.CalledProcessError, ex:
            raise ServiceError('When getting running jobs, failed with non-zero error code. "%s"' % ex.output)
        except Exception, ex:
            raise ServiceError('Problem getting running jobs. "%s"' % ex.message)

    def _create_parameter_files(self, run_directory, model_run):
        """
        Create any parameter files needed for the run
        :param run_directory: Directory for the run
        :param model_run: Model run dictionary
        :return:
        """
        parameter_files = [[JULES_PARAM_POINTS_FILE, "points.dat"]]
        for parameter_name, filename in parameter_files:
            points_file_namelist = self._get_namelist(model_run, parameter_name[0])
            param_value = points_file_namelist[JSON_MODEL_PARAMETERS][parameter_name[1]]

            # Create the file with the parameter value
            param_file = open(os.path.join(run_directory, filename), 'w')
            param_file.write(param_value)
            param_file.close()

            # Save the filename as the parameter value
            points_file_namelist[JSON_MODEL_PARAMETERS][parameter_name[1]] = python_to_f90_str(filename)

    def _get_namelist(self, model_run, namelist_name):
        """
        Get a specified namelist dictionary
        :param model_run: Model run dictionary
        :param namelist_name: The name of the namelist to return
        :return: Requested namelist dictionary
        """
        nml_files = model_run[JSON_MODEL_NAMELIST_FILES]
        for nml_file in nml_files:
            namelists = nml_file[JSON_MODEL_NAMELISTS]
            for namelist in namelists:
                if namelist[JSON_MODEL_NAMELIST_NAME] == namelist_name:
                    return namelist