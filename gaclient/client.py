
import datetime
import itertools
import logging

from .request import Request

class GoogleAnalyticsClient (object):
    ''' Google Analytics Client.

    :param service: An initialized Google Analytics service object, are a
                    callable that returns one.
    :param profile: Google Analytics profile id.
    :param dimensions: A list of dimensions to download.
    :param metrics: A list of metrics to download.
    :param logger: Optional logger to use, if set to None no messages will
                   be logged.
    :param filters: Optional list of filter predicates.
    :param limit: The maximum number of results per request, defaults to
                  10000 which is GAs maximum.
    :param sort: Optional list of sort keys.
    :param request_type: The class to use for GA requests, defaults to
                         :class:`gaclient.Request`.
    '''

    def __init__ (self, service, profile, dimensions, metrics,
            logger=None, filters=None, limit=10000, sort=None, request_type=None):
        self.profile = profile
        self.dimensions = dimensions
        self.metrics = metrics
        self.filters = filters
        self.limit = limit
        self.sort = sort
        self.log = logger or logging.getLogger('gaclient')

        if hasattr(service, '__call__'):
            self.service = service()
        else:
            self.service = service

        self._request_type = request_type or Request

    def download_date_range (self, start_date=None, end_date=None,
                days_per_request=1, limit=None, sort=None, auto_advance=True):
        ''' Download a range of data between `start_date` and `end_date`
            (inclusive).

        :param start_date: Optional date of first record to download.
        :param end_date: Optional date of last record to download.
        :param days_per_request: Number of days to download in each request,
                                 If the resultset is too large GA will
                                 return sampled data, lowering days_per_request
                                 might prevent this behaviour. Default: 1.
        :param limit: Optional limit for this request, defaults to
                      `self.limit`.
        :param sort: Optional sort predicate, defaults to `self.sort`.
        :param auto_advance: If True requests will be issued until no
                             more resulst are available, even is the result
                             set is larger then `limit` results.

        :returns: A generator over all records in this result. The records
                  are returned as :class:`collections.namedtuple`
                  instances.

        `start_date` and `end_date` both default to yesterday, and accept
        either :class:`datetime.date` or :class:`datetime.datetime` or a
        string formatted as 'yyyy-mm-dd` as input.
        '''
        if days_per_request < 1:
            raise ValueError('days_per_request should be at least 1.')

        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        start_date = parse_date(start_date, yesterday)
        end_date = parse_date(end_date, yesterday)

        daystep = datetime.timedelta(days=days_per_request)

        # Date ranges are inclusive, so decrease days_per_request by 1 to
        # make sure data gets download once.
        dayspan = datetime.timedelta(days=days_per_request - 1)

        limit = limit or self.limit
        sort = sort or self.sort

        requests = []
        current_start_date = start_date

        while current_start_date <= end_date:
            current_end_date = current_start_date + dayspan
            if current_end_date > end_date:
                current_end_date = end_date

            requests.append(self._request_type(self.service, self.profile,
                current_start_date, current_end_date, self.dimensions,
                self.metrics, self.filters, sort, limit, auto_advance))

            current_start_date += daystep

        return itertools.chain(*requests)

def parse_date (date, default=None):
    ''' Parse `date` and return a :class:`datetime.date` object.

    :param date: A string in 'yyyy-mm-dd' format or a
                 :class:`datetime.date` object or
                 :class:`datetime.datetime` object.
    :param default: Optional default value, if `date` is None `default`
                    is returned.

    :returns: A :class:`datetime.date` object or `default`.
    '''
    rv = default

    if date is None:
        rv = default

    elif isinstance(date, basestring):
        parts = date.lower().strip().split('-')
        if len(parts) != 3:
            raise ValueError('Datestring incorrectly formatted, '
                             'expected "yyyy-mm-dd" format.')

        int_parts = [int(part) for part in parts]
        rv = datetime.date(*int_parts)

    elif isinstance(date, datetime.datetime):
        rv = date.date()

    elif isinstance(date, datetime.date):
        rv = date

    else:
        raise TypeError('Cannot convert {} to date.'.format(type(date)))

    return rv
