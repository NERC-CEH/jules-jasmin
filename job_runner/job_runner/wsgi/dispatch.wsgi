#make loging work in apache

from paste.script.util.logging_config import fileConfig
fileConfig('/group_workspaces/jasmin2/jules_bd/job_runner/jules-jasmin/job_runner/production.ini')

# Add the virtual Python environment site-packages directory to the path
import site
site.addsitedir('/group_workspaces/jasmin2/jules_bd/job_runner/virtual_env/lib/python2.7/site-packages')

# Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
import os
os.environ['PYTHON_EGG_CACHE'] = '/group_workspaces/jasmin2/jules_bd/job_runner/egg-cache'

# Load the Pylons application
from paste.deploy import loadapp
application = loadapp('config:/group_workspaces/jasmin2/jules_bd/job_runner/jules-jasmin/job_runner/production.ini')
