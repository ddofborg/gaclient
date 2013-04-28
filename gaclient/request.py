
import collections
import datetime
import itertools
import logging
import time

class Request (object):
    ''' A wrapper for Google Analytics requests that supports
        auto-advancing. The wrapper will continue to send requests
        as long as more data is available and `auto_advance` is True.

    :param service: An initialized Google Analytics service object.
    :param profile: GA profile id.
    :param start_date: Date of first record retrieved.
    :param end_date: Date of last record retrieved.
    :param dimensions: A list of dimenions.
    :param metrics: A list of metrics.
    :param filters: List of filters or None.
    :param sort: Sort predicate or None.
    :param limit: Max number of results per request, of `auto_advance`
                  is True then requests will be made until no more
                  results are available.
    :param auto_advance: see `limit`.

    Note: objects of this type are lazy generators over their entire
    resultset.
    '''

    def __init__ (self, service, profile, start_date, end_date,
            dimensions, metrics, filters, sort, limit,
            auto_advance, logger=logging.getLogger('gaclient')):

        self._auto_advance = auto_advance
        self._limit = limit
        self._service = service
        self.log = logger

        if not profile.startswith('ga'):
            profile = 'ga:{}'.format(profile)

        self._start_index = 1
        self._request_data = {
            'ids': profile,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'dimensions': ','.join(dimensions),
            'metrics': ','.join(metrics),
            'max_results': self._limit,
            'start_index': self._start_index
        }

        if sort:
            self._request_data['sort'] = ','.join(sort)

        if filters:
            self._request_data['filters'] = ','.join(filters)

    def records (self):
        ''' Returns a generator over all records. '''
        results = self._next_request()
        headers = self._parse_headers(results['columnHeaders'])
        record_type = self._create_record_type(headers)

        while results:

            for row in results['rows']:
                row_data = [func(val) for (_, func), val in itertools.izip(headers, row)]
                yield record_type(*row_data)

            if not self._auto_advance or not 'nextLink' in results:
                break

            results = self._next_request()

    def _create_record_type (self, headers):
        ''' Returns a namedtuple class. '''
        return collections.namedtuple('Record',
            [header[0] for header in headers])

    def _parse_headers (self, header_info):
        ''' Returns a list of tuples: (column, type), where `column`
            is a name of a column, and `type` is a function parsing
            that column data into a Python type.
        '''
        headers = []

        for header in header_info:
            header_name = self._remove_prefix(header['name'])
            data_type = header['dataType']

            if data_type == 'INTEGER':
                headers.append((header_name, int))

            elif data_type == 'CURRENCY' or data_type == 'DOUBLE':
                headers.append((header_name, float))

            elif data_type == 'STRING':
                if header_name == 'date':
                    headers.append((header_name, self._parse_date))
                else:
                    headers.append((header_name, unicode))

            else:
                raise TypeError('Unknown column type {}.'.format(data_type))

        return headers

    def _parse_date (self, date):
        ''' Parses a GA datestring (%Y%m%d) into a :class:`datetime.date`. '''
        timestruct = time.strptime(date, '%Y%m%d')
        timestamp = time.mktime(timestruct)
        return datetime.date.fromtimestamp(timestamp)

    def _remove_prefix (self, name):
        ''' Removes the `ga:` prefix from metrics and dimneions. '''
        if name.startswith('ga:'):
            return name[3:]
        else:
            return name

    def _next_request (self):
        ''' Execute a single GA request and return raw results. '''
        results = self._service.data().ga().get(**self._request_data).execute()
        self._request_data['start_index'] += self._limit

        if not 'rows' in results:
            return None

        return results

    def __iter__ (self):
        return self.records()

