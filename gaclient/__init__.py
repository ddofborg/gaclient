'''
    A client for google analytics.
'''

__author__ = 'Tiemo Kieft <t.kieft@gmail.com>'
__copyright__ = 'Copyright 2013, Tiemo Kieft'
__credits__ = ['Tiemo Kieft']
__license__ = 'Apache'
__version__ = '0.0.1'
__maintainer__ = 'T. Kieft'
__email__ = 't.kieft@gmail.com'
__status__ = 'Development'

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
