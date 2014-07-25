#make loging work in apache

#from paste.script.util.logging_config import fileConfig
#fileConfig('/home/matken/deployed/majic/development.ini')

# Add the virtual Python environment site-packages directory to the path
import site
site.addsitedir('/home/matken/projectenv/lib/python2.7/site-packages')

# Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
import os
os.environ['PYTHON_EGG_CACHE'] = '/home/matken/deployed/majic/deployed/egg-cache'

# Load the Pylons application
from paste.deploy import loadapp
application = loadapp('config:/home/matken/deployed/majic/development.ini')

