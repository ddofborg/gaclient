'''
    A client for google analytics.
'''

__version__ = '0.3'

import logging

from . import client
from . import request
from . import util

from .client import GoogleAnalyticsClient
from .request import Request

__all__ = [
    'client',
    'request',
    'util',
    
    'GoogleAnalyticsClient',
    'Request',
]

# Setup logging with NullHandler in case no other logger is registered
logging.getLogger('gaclient').addHandler(logging.NullHandler())
