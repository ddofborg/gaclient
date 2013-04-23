
import datetime

from nose.tools import ok_, raises, assert_raises

from gaclient import client
from test import stub

def test_parse_date_none ():
    default = object()
    ok_(default is client.parse_date(None, default))
    ok_(None is client.parse_date(None))

def test_parse_date_string ():
    d = datetime.date(2013, 02, 01)
    ok_(d == client.parse_date('2013-02-01'))
    ok_(d == client.parse_date(' 2013-02-01'))
    ok_(d == client.parse_date('2013-02-01 '))
    ok_(d == client.parse_date(' 2013-02-01 '))

def test_parse_date_datetime ():
    d = datetime.date.today()
    t = datetime.datetime.now()
    ok_(d == client.parse_date(t))

def test_parse_date_date ():
    d = datetime.date.today()
    ok_(d == client.parse_date(d))

def test_parse_date_invalid_string ():
    assert_raises(ValueError, client.parse_date, '123')

@raises(TypeError)
def test_parse_date_invalid_type ():
    client.parse_date([])


class TestGoogleAnalyticsClient (object):

    def setUp (self):
        self.client = client.GoogleAnalyticsClient(stub.Service(), 'abc123', ['ga_keyword'],
            ['ga:visits'])

    @raises(ValueError)
    def test_invalid_days_per_request (self):
        self.client.download_date_range(days_per_request=0)

    def test_iteration (self):
        ok_(len(list(self.client.download_date_range())) == 18    )
