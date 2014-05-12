"""
Usage logger

@author: rwilkinson
"""
import logging
from ecomaps.lib.base import request

log = logging.getLogger(__name__)

def getUsageLogger(request):
    addrStr = request.remote_addr if request.remote_addr is not None else '-'
    userStr = request.remote_user if request.remote_user is not None else '-'
    return logging.LoggerAdapter(logging.getLogger('usage'), {'ip': addrStr, 'user': userStr})
