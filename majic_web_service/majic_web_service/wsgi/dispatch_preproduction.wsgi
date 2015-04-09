#make logging work in apache
from paste.script.util.logging_config import fileConfig
fileConfig('/var/local/majic_ws/jules-jasmin/majic_web_service/preproduction.ini')

# Add the virtual Python environment site-packages directory to the path
import site
site.addsitedir('/var/local/majic_ws/virtual_env/lib/python2.7/site-packages')

# Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
import os
os.environ['PYTHON_EGG_CACHE'] = '/var/local/majic_ws/egg-cache'

# Load the Pylons application
from paste.deploy import loadapp
application = loadapp('config:/var/local/majic_ws/jules-jasmin/majic_web_service/preproduction.ini')