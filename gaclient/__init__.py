'''
    A client for google analytics.
'''

__version__ = '0.2.1'

import logging

from . import client
from . import request
from .client import GoogleAnalyticsClient
from .request import Request

__all__ = [
    'client',
    'request',
    'GoogleAnalyticsClient',
    'Request',
]

# Setup logging with NullHandler in case no other logger is registered
logging.getLogger('gaclient').addHandler(logging.NullHandler())
