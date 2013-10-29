# -*- coding: utf-8 -*-
'''
    gaclient is a small library that implements an easy to use API
    for consuming Google Analytics APIs.

    Assuming you have already obtained a **refresh token** from the
    user, retrieving metrics is as simple as::

        >>> import gaclient
        >>> session = gaclient.build_session(CLIENT_ID, CLIENT_SECRET,
            {'refresh_token': REFRESH_TOKEN})
        >>> it = gaclient.Cursor(session, PROFILE_ID,
            '2012-01-01', '2012-01-01', ['visits'], ['date'])
        >>> list(it)
        [{'visits': 12345, 'date': datetime.date(2012, 1, 1)}]

    For complete step-by-step guide on how to obtain a user's
    consent please refer to the
    `User Guide <http://www.python-gaclient.org/0.3/guide.html>`_.


    Features
    --------

        * Transparently queries Google Analytics for additional results
          if any are available;
        * Selecting any valid combination of dimensions and metrics;
        * Server-side filtering;
        * Server-side sorting;
        * Data is returned in native Python types, parsed and
          ready for you consumption.


'''

__author__ = 'Tiemo Kieft'
__version__ = '0.3b2'
__license__ = 'Apache 2.0'

import datetime
import functools
import itertools
import logging
import sys
import random
import time

from requests.exceptions import ConnectionError, Timeout
from ssl import SSLError

PY3 = (sys.version_info.major == 3)

if PY3:
    from urllib.parse import urlencode

    basestring = str
    unicode = str
else:
    from urllib import urlencode

from requests_oauthlib import OAuth2Session


# Google OAuth2 token refresh url.
REFRESH_URL = 'https://accounts.google.com/o/oauth2/token'

#: Baseurls for each type of request
BASEURLS = {
    'data': 'https://www.googleapis.com/analytics/v3/data/ga',
}

#: Google Analytics OAuth2 scopes.
SCOPES = {
    'read-only': 'https://www.googleapis.com/auth/analytics.readonly',
}


#: Conversions from Google Analytics data types to Python types.
DATATYPES = {
    'STRING': unicode,
    'INTEGER': int,
    'CURRENCY': float,
    'FLOAT': float,
}

LOG = logging.getLogger('gaclient')
LOG.addHandler(logging.NullHandler())


class Error (Exception):
    ''' General error class. '''

class InvalidDateRange (Error):
    ''' Raised when an invalid date range is specified. '''

class InvalidResponse (Error):
    ''' Raised when Analytics returns an unexpected result. '''

class UnsupportedDataType (Error):
    ''' Raised when Analytics data of an unsupported type. '''

class AnalyticsError (Error):
    ''' Raised when Google Analytics returns an error response. '''

    def __init__ (self, code, message, errors):
        super(AnalyticsError, self).__init__(message)
        self.code = code
        self.message = message
        self.errors = errors


class Cursor (object):
    ''' Wraps a single request against the Google Analytics data API.

    :param session: An authorized OAuth2 session, see :func:`build_session`.
    :param \*args: Passed to :func:`build_data_query`.
    :param \*\*kwargs: Arguments that are not listed below are passed to
                       :func:`build_data_query`.

    Optional keyword arguments:
        `attempts`: Each cursor will make at most `attempts` attempts to
                    execute its requet. Defaults to 5.
    '''

    def __init__ (self, session, *args, **kwargs):
        self.session = session

        self.args = args
        self.kwargs = kwargs

        self.attempts = kwargs.pop('attempts', 5)

        assert self.attempts is None or self.attempts > 0

        if self.attempts is None:
            self.attempts = 1

        self.params = build_data_query(*args, **kwargs)

        self._next_link = u'{}?{}'.format(
            BASEURLS['data'], urlencode(self.params))

        self._row_buffer = []
        self._len = None
        self._columns = []

        #: True if the resultset contains sampled data. Sampling can
        #: be prevented in most cases by sharding requests by date.
        self.sampled = None


    @property
    def next_cursor (self):
        ''' Returns a :class:`Cursor` instance for the next page of
            results, if any.
        '''
        self.execute()
        if self._next_link:
            kwargs = dict(self.kwargs,
                start_index=self.params['start-index'] + self.params['max-results'])

            next_cursor = Cursor(self.session, *self.args, **kwargs)

            return next_cursor


    def execute (self):
        ''' Execute the request and store it's results. This method
            is automatically called when iterating over the object.
        '''

        def wait (attempt):
            delay = (2 ** attempt) + random.random()

            LOG.info('An error occured, retry in {} seconds'.format(
                delay))

            time.sleep(delay)


        if self._len is None:
            for attempt in range(self.attempts):

                try:
                    self._row_buffer = self._download_next_link()

                except (ConnectionError, Timeout, SSLError, ValueError) :
                    if attempt == self.attempts - 1:
                        raise

                    wait(attempt)

                except AnalyticsError as ex:
                    if not (500 <= ex.code < 600) or\
                            attempt == self.attempts - 1:
                        raise

                    wait(attempt)

                else:
                    break


    def _download_next_link (self):
        LOG.info('Downloading data.')
        response = execute_request(self.session, self._next_link)
        
        if not response['kind'] == 'analytics#gaData':
            raise InvalidResponse('Expected data response.')

        self._len = response['totalResults']
        self._set_columns_from_response(response)
        self._next_link = response.get('nextLink')

        self.sampled = self.sampled or response['containsSampledData']

        if self._len == 0:
            retval = []
        else:
            retval = [self._parse_row(row) for row in response['rows']]

        return retval


    def _parse_row (self, row):
        return {k: t(row[i]) for i, (k, t) in enumerate(self._columns)}


    def _set_columns_from_response (self, response):
        headers = response['columnHeaders']
        self._columns = [self._parse_header(h) for h in headers]


    def _parse_header (self, header):
        type_ = header['dataType']
        name = header['name']
        
        try:
            parser = DATATYPES[type_]
        except KeyError:
            raise UnsupportedDataType(type_)

        if name == 'ga:date':
            parser = parse_date

        return (remove_ga_prefix(name), parser)


    def __iter__ (self):
        self.execute()
        for row in self._row_buffer:
            yield row

    def __len__ (self):
        self.execute()
        return self._len


class ResponseIterator (object):
    ''' Automatically iterates over all pages of a Cursor.

    :param cursor: A :class:`Cursor` instance.
    :param limit: Optional limit on the number of results that are
                  yielded.
    '''

    def __init__ (self, cursor, limit=None):
        self.cursor = cursor
        self.limit = limit
        self._index = 0

        LOG.info('Initialize ResponseIterator with limit={}'.format(
            self.limit))


    def _raise_on_limit (self):
        self._index += 1
        if self.limit and self._index > self.limit:
            LOG.info('ResponseIterator limit reached.')
            raise StopIteration()


    def __iter__ (self):
        while self.cursor:
            for row in self.cursor:
                self._raise_on_limit()
                yield row

            self.cursor = self.cursor.next_cursor


def build_data_query (profile_id, start_date, end_date, metrics,
        dimensions=None, sort=None, filters=None, max_results=10000,
        start_index=1):
    ''' Build the parameters dictionary for a data query.

    :param profile_id: The Google Analytics profile id to query.
    :param start_date: Start date of the request.
    :param end_date: End date of the request.
    :param metrics: A list of metrics to download.
    :param dimensions: Optional list of dimensions.
    :param sort: Optional list of sort predicates.
    :param filters: Optional list of filter predicates.
    :param max_results: Maximum number of results.
    :param start_index: The index of the first element to retrieve.

    `start_date` and `end_date` should be :class:`datetime.datetime` or
    :class:`datetime.date` objects, or strings in ``yyyy-mm-dd`` or
    ``yyyymmdd`` format.

    .. note:: The range of data that is downloaded from the data api
              includes both dates.

    :returns: A dictionary of query parameters.

    :raises: A :class:`InvalidDateRange` is raised if the specified data
             range is invalid.
    '''
    assert isinstance(metrics, list)
    assert dimensions is None or isinstance(dimensions, list)
    assert sort is None or isinstance(sort, list)
    assert filters is None or isinstance(filters, list)
    assert 0 < int(max_results) <= 10000
    assert int(start_index) > 0
    
    profile_id = add_ga_prefix(profile_id)
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    metrics = add_ga_prefix(metrics)
    dimensions = add_ga_prefix(dimensions)
    sort = add_ga_prefix(sort)
    filters = add_ga_prefix(filters)
    max_results = int(max_results)
    start_index = int(start_index)

    if start_date > end_date:
        raise InvalidDateRange('{} > {}'.format(start_date, end_date))

    if start_date < datetime.date(2008, 1, 1):
        raise InvalidDateRange('Cannot query dates prior to 2008-01-01')

    if end_date > datetime.date.today():
        raise InvalidDateRange('Cannot query dates after today.')

    params = {
        'ids': profile_id,
        'start-date': str(start_date),
        'end-date': str(end_date),
        'metrics': u','.join(metrics),
        'max-results': max_results,
        'start-index': start_index,
    }

    if dimensions:
        params['dimensions'] = u','.join(dimensions)

    if sort:
        params['sort'] = u','.join(sort)

    if filters:
        params['filters'] = u','.join(filters)

    return params


def execute_request (session, url):
    ''' Execute a ``GET`` request against `url` within the context
        of `session`.

    :param session: An authorized OAuth2 session, see :func:`build_session`.
    :param url: The URL to ``GET``.

    :returns: A dictionary of data returned by the API if valid JSON data
              was returned.

    :raises: A :class:`ValueError` is raised in case the returned data
             was not valid JSON. If the API returns an error then a
             :class:`AnalyticsError` is raised.
    '''
    LOG.debug('Executing request url="{}".'.format(url))
    try:
        data = session.get(url).json()

    except Exception as ex:
        LOG.exception('request url={}'.format(url))
        raise

    e = data.get('error')
    if e:
        LOG.error('Analytics reported an error: code={}, message={}.'.format(
            e.get('code'), e.get('message')))

        raise AnalyticsError(int(e['code']), e['message'], e['errors'])

    return data


def remove_ga_prefix (val):
    ''' Returns `val` with it's ``ga:`` prefix stripped of, if present. '''
    assert isinstance(val, basestring)

    if val.startswith('ga:'):
        val = val[3:]

    return val


def add_ga_prefix (val_or_vals):
    ''' Adds ``ga:`` prefix to `val_or_vals` if it is a string or to
        its elements if it is a list or tuple.

    :param val_or_vals: A string, list or tuple.

    :returns: A string if `val_or_vals` is a string, or a list if
              `val_or_vals` was a list or tuple. If `val_or_vals` is
              ``None`` then ``None`` is returned.
    '''
    is_list = isinstance(val_or_vals, (tuple, list))
    rv = None

    if is_list and len(val_or_vals) > 0:
        rv = [add_ga_prefix(v) for v in val_or_vals]

    elif isinstance(val_or_vals, basestring):
        neg = val_or_vals[0] == '-'

        if neg:
            prefix = '-'
            val_or_vals = val_or_vals[1:]
        else:
            prefix = ''

        if val_or_vals.startswith('ga:'):
            rv = u'{}{}'.format(prefix, val_or_vals)
        else:
            rv = u'{}ga:{}'.format(prefix, val_or_vals)

    return rv


def parse_date (date):
    ''' Parses a date and returns a :class:`datetime.date`.

    :param date: A `str`, :class:`datetime.datetime` or 
                 :class:`datetime.date`.

    :returns: A :class:`datetime.date` instance is returned.

    If `data` is a string then it is interpreted as either ``yyyy-mm-dd``
    format or ``yyyymmdd`` format, the latter is returned by Google Analytics.
    '''
    rv = None

    if isinstance(date, datetime.datetime):
        rv = date.date()

    elif isinstance(date, basestring):
        try:
            rv = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        except ValueError as ex:
            try:
                rv = datetime.datetime.strptime(date, '%Y%m%d').date()

            except ValueError as ex:
                raise ValueError('Cannot parse date : {}'.format(date))

    elif not isinstance(date, datetime.date):
        raise ValueError('date must be str, datetime.date or datetime.datetime')

    else:
        rv = date

    return rv


def build_session (client_id, client_secret, token, update_token=None):
    ''' Build an auto-refreshing OAuth2 Session.

    :param client_id: The application's client id.
    :param client_secret: The application's client secret.
    :param token: A token dictionary, which should at the very least
                  contain a ``refresh_token`` with an optional
                  ``access_token``.
    :param update_token: Optiona callback that is called upon token
                         refresh. It should take a single argument, the
                         new token.

    :returns: An OAuth2 session.
    '''
    orig_token = token.copy()

    LOG.debug('Creating OAuth 2.0 session.')

    def token_updater (token):
        LOG.debug('Call token_updater')
        if update_token:
            update_token(token)

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    session = OAuth2Session(client_id, token=token,
        auto_refresh_url=REFRESH_URL, auto_refresh_kwargs=extra,
        token_updater=token_updater)

    if token.get('access_token') is None:
        token = session.refresh_token(REFRESH_URL, **extra)
        token_updater(token)

    return session


def generate_consent_url (client_id, redirect_uri, scope='read-only'):
    ''' Generate and return a consent URL. Use this URL to direct the user
        to Google's consent page.

    :param client_id: The client id of the application.
    :param redirect_uri: The URI the user is redirected to after she
                         accepts or rejects the consent form presented
                         by Google.
    :param scope: The scope of the request. Currently only ``read-only``
                  is supported.

    :returns: A URI.
    '''
    scope_ = [SCOPES[scope]]

    session = OAuth2Session(client_id, redirect_uri=redirect_uri,
        scope=scope_)

    authorization_url, state = session.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        access_type="offline", approval_prompt="force")

    return authorization_url


