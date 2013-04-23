
import datetime

from nose.tools import ok_, raises

from test import stub


class TestRequestData (object):

    def __init__ (self):
        self.date = datetime.date(2010, 1, 1)
        self.request_data = {
            'service': None,
            'profile': 'abc123',
            'start_date': self.date,
            'end_date': self.date,
            'dimensions': ['ga:keyword', 'ga:date'],
            'metrics': ['ga:visits', 'ga:visitors'],
            'auto_advance': True,
            'limit': 10,
            'sort': None,
            'filters': None,
        }

    def test_join (self):
        request = stub.StubRequest(**self.request_data)
        request_data = request._request_data

        ok_('ga:visits,ga:visitors' == request_data['metrics'])
        ok_('ga:keyword,ga:date' == request_data['dimensions'])

    def test_no_filters_no_sort (self):
        self.request_data['filters'] = None
        self.request_data['sort'] = None
        request = stub.StubRequest(**self.request_data)

        ok_(not 'filters' in request._request_data)
        ok_(not 'sort' in request._request_data)

        self.request_data['filters'] = []
        self.request_data['sort'] = []
        request = stub.StubRequest(**self.request_data)

        ok_(not 'filters' in request._request_data)
        ok_(not 'sort' in request._request_data)

    def test_filters (self):
        self.request_data['filters'] = ['ga:medium==organic']
        request = stub.StubRequest(**self.request_data)

        ok_('ga:medium==organic' == request._request_data['filters'])

        self.request_data['filters'] = ['ga:medium==organic,ga:visits>1']
        request = stub.StubRequest(**self.request_data)

        ok_('ga:medium==organic,ga:visits>1' == request._request_data['filters'])

    def test_sort (self):
        self.request_data['sort'] = ['ga:date']
        request = stub.StubRequest(**self.request_data)
        ok_('ga:date' == request._request_data['sort'])

        self.request_data['sort'] = ['-ga:date']
        request = stub.StubRequest(**self.request_data)
        ok_('-ga:date' == request._request_data['sort'])

        self.request_data['sort'] = ['-ga:date', 'ga:visits']
        request = stub.StubRequest(**self.request_data)
        ok_('-ga:date,ga:visits' == request._request_data['sort'])

class TestParseHeader (object):

    def setUp (self):
        service = stub.Service()
        self.request = stub.StubRequest(service, 'abc123',
            datetime.date.today(), datetime.date.today(),
            ['ga:keyword'], ['ga:visits'], None, None, 10, True)

    def test_parse_headers (self):
        column_headers = [
            {'dataType': 'STRING', 'name': 'ga:date'},
            {'dataType': 'STRING', 'name': 'ga:keyword'},
            {'dataType': 'INTEGER', 'name': 'ga:visits'},
        ]

        parsed_headers = self.request._parse_headers(column_headers)
        ok_(('keyword', unicode) in parsed_headers)
        ok_(('date', self.request._parse_date) in parsed_headers)
        ok_(('visits', int) in parsed_headers)

    def test_create_record_type (self):
        column_headers = [
            {'dataType': 'STRING', 'name': 'ga:date'},
            {'dataType': 'STRING', 'name': 'ga:keyword'},
            {'dataType': 'INTEGER', 'name': 'ga:visits'},
        ]

        parsed_headers = self.request._parse_headers(column_headers)
        rtype = self.request._create_record_type(parsed_headers)

        ok_(hasattr(rtype, 'keyword'))
        ok_(hasattr(rtype, 'date'))
        ok_(hasattr(rtype, 'visits'))

    @raises(TypeError)
    def test_unknown_type (self):
        self.request._parse_headers([{'dataType': 'foobar', 'name': 'foobar'}])


class TestUtilities (object):

    def setUp (self):
        self.request = stub.StubRequest(stub.Service(), 'abc123',
            datetime.date.today(), datetime.date.today(),
            ['ga:keyword'], ['ga:visits'], None, None, 10, True)

    def test_parse_date (self):
        today = datetime.date.today()
        datestr = today.strftime('%Y%m%d')
        ok_(self.request._parse_date(datestr) == today)

    def test_remove_prefix (self):
        ok_('keyword' == self.request._remove_prefix('keyword'))
        ok_('keyword' == self.request._remove_prefix('ga:keyword'))

class TestNextRequest (object):

    def setUp (self):
        self.request = stub.StubRequest(stub.Service(), 'abc123',
            datetime.date.today(), datetime.date.today(),
            ['ga:keyword'], ['ga:visits'], None, None, 10, True)

    def test_next_request (self):
        ok_(stub.results[0] == self.request._next_request())
        ok_(stub.results[1] == self.request._next_request())
        ok_(None is self.request._next_request())

    def test_iterator (self):
        for record in self.request:
            ok_(hasattr(record, 'keyword'))
            ok_(hasattr(record, 'visits'))


class TestAutoAdvance (object):

    def test_with_advance (self):
        request = stub.StubRequest(stub.Service(), 'abc123',
            datetime.date.today(), datetime.date.today(),
            ['ga:keyword'], ['ga:visits'], None, None, 10, True)

        ok_(len(list(request)) == 18)

    def test_without_advance (self):
        request = stub.StubRequest(stub.Service(), 'abc123',
            datetime.date.today(), datetime.date.today(),
            ['ga:keyword'], ['ga:visits'], None, None, 10, False)

        ok_(len(list(request)) == 10)
