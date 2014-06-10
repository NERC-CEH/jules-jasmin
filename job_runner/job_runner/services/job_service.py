# Header
import glob

import os
from pylons import config
import subprocess
import re
from job_runner.utils.constants import *


class ServiceError(Exception):
    """
    Exception class for when the service has a problem
    """
    pass


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

    def submit(self, model_run):
        """
        submit a job to the lsf framework
        :param model_run: the model run to submit
        :return: job id
        :exception ServiceError: if there is a problem submitting the job
        """
        #ensure that the model id is a number so it can not possible contain path elements
        model_run_id_dir = model_run[JSON_MODEL_RUN_ID].strip()
        assert(model_run_id_dir.isdigit())

        run_directory = os.path.join(config['run_dir'], 'run%s' % model_run_id_dir)

        #create run directory
        os.mkdir(run_directory)

        #create softlinks
        for src in glob.glob(os.path.join(config['jules_files_to_softlink_dir'], '*')):
            os.symlink(src, os.path.join(run_directory, os.path.basename(src)))

        #TODO remove when full name lists availiable
        jules_time_nml = model_run[JSON_MODEL_NAMELIST_FILES][0][JSON_MODEL_NAMELISTS][0][JSON_MODEL_PARAMETERS]
        jules_time_nml['main_run_start'] = "'1996-12-31 23:00:00'"
        jules_time_nml['main_run_end'] = "'1997-12-31 23:00:00'"
        jules_time_nml['print_step'] = '48'

        model_run[JSON_MODEL_NAMELIST_FILES][0][JSON_MODEL_NAMELISTS].append(
            {
                'name': 'JULES_SPINUP',
                'parameters' : {'max_spinup_cycles': '0'}
            }
        )

        for namelist_file in model_run[JSON_MODEL_NAMELIST_FILES]:
            self._create_namelist_file(namelist_file, run_directory)

        return self._submit_job(model_run[JSON_MODEL_CODE_VERSION], run_directory)

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

        for namelist in namelist_file[JSON_MODEL_NAMELISTS]:
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


