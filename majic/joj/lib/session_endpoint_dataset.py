"""
Contains definitions for the special user session endpoints 'dataset'.

@author: rwilkinson
"""
# ID for the outline layer
SESSION_ENDPOINTS_ID = 'ds:session_endpoints'
NEW_ENDPOINT_ID = 'ep:new_session_endpoint'

# Information for the dataset tree for the session endpoints dataset
sessionEndpointsTreeInfo = {
    'id': SESSION_ENDPOINTS_ID,
    'text': 'Temporary Map Services',
    'qtip': 'User defined map services for this session',
    'cls': 'folder',
    'leaf': False
    }

newEndpointTreeInfo = {
    'id': NEW_ENDPOINT_ID,
    'text': 'Add map service ...',
    'qtip': 'Add a map service for this session',
    'cls': 'file',
    'iconCls': 'vd-new-endpoint-icon',
    'leaf': True
    }
