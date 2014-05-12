import logging

from ecomaps.lib.base import *
from paste.request import parse_querystring
import urllib2

log = logging.getLogger(__name__)

class SecurityloginController(BaseController):
    def index(self):
        if 'ndg.security.auth' in request.cookies.keys():
            return '<html><head></head><body onload="window.close()"></body></html>'
        else:
            #get login credentials
            inputs=dict(parse_querystring(request.environ))
            securedResource=inputs['endpoint']
            try:
                u=urllib2.urlopen(securedResource)
            except urllib2.HTTPError, e:
                if e.code == 401:
		    #replace the redirection part of the url with a link to a controller which closes the login window (rather than accessing the WXS resource
                    serverurl=config['app_conf']['serverurl'] 
                    loggedinurl='%s/loggedin'%serverurl
                    c.redirecturl = '%s=%s'%(e.url.split('=')[0],loggedinurl)
                    #i.e. c.redirecturl="https://ndg3beta.badc.rl.ac.uk/verify?ndg.security.r=http%253A%252F%252Flocalhost:5005%252Floggedin"
                    return render('redirecting.html')
