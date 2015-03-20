#make logging work in apache
from paste.script.util.logging_config import fileConfig
fileConfig('/var/local/job_runner/jules-jasmin/job_runner/preproduction.ini')

# Add the virtual Python environment site-packages directory to the path
import site
site.addsitedir('/var/local/job_runner/virtual_env/lib/python2.7/site-packages')

# Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
import os
os.environ['PYTHON_EGG_CACHE'] = '/var/local/job_runner/egg-cache'

# Load the Pylons application
from paste.deploy import loadapp
application = loadapp('config:/var/local/job_runner/jules-jasmin/job_runner/preproduction.ini')
