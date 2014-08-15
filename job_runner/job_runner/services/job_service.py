"""
# Header
"""
from datetime import datetime
import logging
import os
from pylons import config
import subprocess
import re
from job_runner.utils.constants import *
from job_runner.model.log_file_parser import LogFileParser
from job_runner.model.bjobs_parser import BjobsParser
from job_runner.utils.constants import JULES_PARAM_POINTS_FILE
import shutil

log = logging.getLogger(__name__)


class ServiceException(Exception):
    """
    Exception class for when the service has a problem
    """
    def __init__(self, message):
        super(ServiceException, self).__init__()
        self.message = message


class JobService(object):
    """
    Service for managing job queries
    """

    def __init__(self, valid_code_versions=VALID_CODE_VERSIONS,
                 valid_single_processor_code_version=VALID_SINGLE_PROCESSOR_CODE_VERSIONS):
        """
        Constructor setups up valid code versions

        :param valid_single_processor_code_version: a dictionary of valid code versions and
        script files for single processor runs, defaults to constants
        :param valid_code_versions: a dictionary of valid code versions and script files, defaults to constants
        """
        self._valid_code_version = valid_code_versions
        self._valid_single_processor_code_version = valid_single_processor_code_version

    def exists_run_dir(self, model_run_id):
        """
        Checks that the model run directory exists
        :param model_run_id: the model run id
        :return:true if it exists, false otherwise
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
        if not os.path.exists(file_path):
            return None
        f = open(file_path, 'r')
        id = f.read()
        if id.isdigit():
            log.error("bsub id file for model run is empty. At {}".format(file_path))
            return int(id)
        else:
            return None

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

    def _write_job_log(self, bsub_id, model_run):
        """
        Write the job submitted to the job log
        :param bsub_id: the bsub id used
        :param model_run: the model run
        :return:nothing
        """
        file_path = os.path.join(config['run_dir'], FILENAME_JOBS_RUN_LOG)
        if os.path.exists(file_path):
            f = open(file_path, 'a')
        else:
            f = open(file_path, 'w')
            f.writelines("Time  BsubId  ModelRunId  UserId  UserName  UserEmail\n")

        line = "{time}  {bsub}  {model_run_id}  {user_id}  {user_name}  {user_email}\n".format(
            time=str(datetime.now()),
            bsub=bsub_id,
            model_run_id=model_run[JSON_MODEL_RUN_ID],
            user_id=model_run[JSON_USER_ID],
            user_name=model_run[JSON_USER_NAME],
            user_email=model_run[JSON_USER_EMAIL])
        f.writelines(line)
        f.close()

    def get_output_log_result(self, run_dir):
        """
        Get the result of the Jules by looking at the log
        :param run_dir: the run directory to get the file from
        :return: log file parser
        """
        file_path = os.path.join(run_dir, FILENAME_OUTPUT_LOG)
        if not os.path.exists(file_path):
            raise ServiceException(ERROR_MESSAGE_NO_LOG_FILE)
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
        
        run_directory = self.get_run_dir(model_run[JSON_MODEL_RUN_ID])

        #create run directory
        if not os.path.exists(run_directory):
            os.mkdir(run_directory)

        #create output dir
        os.mkdir(os.path.join(run_directory, OUTPUT_DIR))

        #create softlinks to data
        src = os.path.join(config['jules_run_data_dir'])
        os.symlink(src, os.path.join(run_directory, os.path.basename(src)))

        self._create_parameter_files(run_directory, model_run)

        for namelist_file in model_run[JSON_MODEL_NAMELIST_FILES]:
            self._create_namelist_file(namelist_file, run_directory)

        single_processor = self._is_single_site_run(model_run)

        bsub_id = self._submit_job(model_run[JSON_MODEL_CODE_VERSION], run_directory, single_processor)

        self._write_job_log(bsub_id, model_run)
        self.write_bsub_id(run_directory, bsub_id)

        return bsub_id

    def _submit_job(self, code_version, run_directory, single_processor):
        """
        Submit the job
        :param code_version: the code version
        :param run_directory: the run directory to use
        :param single_processor: true if this is a single processor run
        :return: the job id
        :exception ServiceError: when there is a problem submiting the job
        """
        try:
            script_directory = config['jules_run_script_dir']
            if single_processor:
                script = os.path.join(script_directory, self._valid_single_processor_code_version[code_version])
            else:
                script = os.path.join(script_directory, self._valid_code_version[code_version])
            output = subprocess.check_output([script], stderr=subprocess.STDOUT, cwd=run_directory)
            #Job <337912> is submitted to default queue <lotus>
            match = re.search('Job <(\d*)>', output)
            if match is None:
                raise ServiceException('Problem in job script. "%s"' % output)
            return match.group(1)

        except subprocess.CalledProcessError, ex:
            raise ServiceException('Problem running job script. "%s"' % ex.output)
        except Exception, ex:
            raise ServiceException('Problem submitting job script. "%s"' % ex.message)

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
            raise ServiceException('When getting running jobs, failed with non-zero error code. "%s"' % ex.output)
        except Exception, ex:
            raise ServiceException('Problem getting running jobs. "%s"' % ex.message)

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
            if points_file_namelist is not None and parameter_name[1] in points_file_namelist[JSON_MODEL_PARAMETERS]:
                param_value = points_file_namelist[JSON_MODEL_PARAMETERS][parameter_name[1]]

                # Create the file with the parameter value
                param_file = open(os.path.join(run_directory, filename), 'w')
                param_file.write(param_value)
                param_file.close()

                # Save the filename as the parameter value
                points_file_namelist[JSON_MODEL_PARAMETERS][parameter_name[1]] = "'{}'".format(filename)

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
        return None

    def _is_single_site_run(self, model_run):
        """
        Find out if this is a single site run
        :param model_run: Model run dictionary
        :return: true if it is false otherwise
        """

        points_file_namelist = self._get_namelist(model_run, JULES_PARAM_LATLON_REGION[0])

        if points_file_namelist is not None \
                and JULES_PARAM_LATLON_REGION[1] in points_file_namelist[JSON_MODEL_PARAMETERS]:
            param_value = points_file_namelist[JSON_MODEL_PARAMETERS][JULES_PARAM_LATLON_REGION[1]]

            return str(param_value).lower() == '.false.'

        return False

    def delete(self, model_run_id):
        """
        Delete a model run directory
        :param model_run_id: the model run id
        :return: nothing
        """

        if self.exists_run_dir(model_run_id):
            run_dir = self.get_run_dir(model_run_id)
            try:
                shutil.rmtree(run_dir)
            except OSError, ex:
                log.exception("Error when deleting the model run directory %s" % run_dir)
                raise ServiceException('Can not delete the model run directory - %s' % ex.strerror)

    def create_file(self, model_run_id, filename):
        """
        Create a new file in the model run directory
        :param model_run_id: Model run ID
        :param filename: Filename to create
        :return:
        """
        directory = self.get_run_dir(model_run_id)
        if not os.path.exists(directory):
            os.mkdir(directory)
        path = os.path.join(directory, filename)
        f = open(path, 'w+')
        f.close()

    def delete_file(self, model_run_id, filename):
        """
        Delete a file in the model run directory
        :param model_run_id: Model run ID
        :param filename: Filename to delete
        :return:
        """
        directory = self.get_run_dir(model_run_id)
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            os.remove(path)

    def append_to_file(self, model_run_id, filename, text):
        """
        Append text to an existing file
        :param model_run_id: Model run ID
        :param filename: Filename to append to
        :param text: Text to append
        :return:
        """
        directory = self.get_run_dir(model_run_id)
        path = os.path.join(directory, filename)
        f = open(path, 'a')
        f.write(text)
        f.close()