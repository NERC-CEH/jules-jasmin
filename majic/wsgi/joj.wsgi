#import site

#site.addsitedir('/usr/local/jenp_cows/env/lib/python2.6/site-packages')
#
#import sys
#raise Exception(sys.path)

ALLDIRS = ['/usr/local/jenp_cows/env/lib/python2.6/site-packages']

import sys 
import site 

# Remember original sys.path.
prev_sys_path = list(sys.path) 

 # Add each new site-packages directory.
for directory in ALLDIRS:
   site.addsitedir(directory)

   # Reorder sys.path so new directories at the front.
   new_sys_path = [] 
   for item in list(sys.path): 
       if item not in prev_sys_path: 
               new_sys_path.append(item) 
               sys.path.remove(item) 
sys.path[:0] = new_sys_path

import os

sys.path.append('/usr/local/jenp_cows/dev/ecomaps')

#raise Exception(sys.path)

os.environ['PYTHON_EGG_CACHE'] = '/tmp/apache-eggs'

from paste.deploy import loadapp

application = loadapp('config:/usr/local/jenp_cows/dev/ecomaps/development.ini')
