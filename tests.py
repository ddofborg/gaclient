
import datetime
import json

from nose.tools import ok_, eq_, assert_raises, raises

import gaclient as gc



class MockSession (object):

    def __init__ (self, data):
        self.data = data


    def get (self, *args, **kwargs):
        return self


    def json (self):
        return self.data



def test_parse_date ():
    d = datetime.date(2012, 1, 1)

    eq_(d, gc.parse_date(d))
    eq_(d, gc.parse_date(datetime.datetime(2012, 1, 1)))
    eq_(d, gc.parse_date('2012-01-01'))
    eq_(d, gc.parse_date('20120101'))

    assert_raises(ValueError, gc.parse_date, 42)
    assert_raises(ValueError, gc.parse_date, None)

    assert_raises(ValueError, gc.parse_date, 'abc')
    assert_raises(ValueError, gc.parse_date, '01-01-20012')


def test_add_ga_prefix ():
    eq_('ga:date', gc.add_ga_prefix('ga:date'))
    eq_('ga:date', gc.add_ga_prefix('date'))
    eq_(None, gc.add_ga_prefix(None))
    eq_(None, gc.add_ga_prefix(42))

    eq_(['ga:foo', 'ga:bar'], gc.add_ga_prefix(('foo', 'bar')))
    eq_(['ga:foo', 'ga:bar'], gc.add_ga_prefix(['foo', 'bar']))
    eq_(None, gc.add_ga_prefix([]))


def test_remove_ga_prefix ():
    eq_('date', gc.remove_ga_prefix('date'))
    eq_('date', gc.remove_ga_prefix('ga:date'))

    assert_raises(AssertionError, gc.remove_ga_prefix, None)
    assert_raises(AssertionError, gc.remove_ga_prefix, 42)


class TestExecuteRequest (object):

    def test_valid_json (self):
        session = MockSession({'foo': 'bar'})
        rv = gc.execute_request(session, 'http://example.com')
        eq_(rv, {'foo': 'bar'})


    def test_error_response (self):
        session = MockSession({'error': {
            'message': 'error_message',
            'code': 42,
            'errors': {'foo': 'bar'}
        }})

        try:
            gc.execute_request(session, '')

        except gc.AnalyticsError as ex:
            eq_(ex.code, 42)
            eq_(ex.message, 'error_message')
            eq_(ex.errors, {'foo': 'bar'})

        else:
            ok_(False)


    @raises(ValueError)
    def test_invalid_json (self):
        session = MockSession('foo')
        session.json = lambda: json.loads('foobar')
        gc.execute_request(session, '')



class TestBuildDataQuery (object):

    @raises(AssertionError)
    def test_invalid_metrics (self):
        gc.build_data_query('', '', '', 'foobar')

    @raises(AssertionError)
    def test_invalid_dimensions (self):
        gc.build_data_query('', '', '', ['ga:visits'], dimensions='foobar')

    @raises(AssertionError)
    def test_invalid_sort (self):
        gc.build_data_query('', '', '', ['ga:visits'], sort='foobar')

    @raises(AssertionError)
    def test_invalid_filters (self):
        gc.build_data_query('', '', '', ['ga:visits'], filters='foobar')

    @raises(ValueError)
    def test_non_numeric_max_results (self):
        gc.build_data_query('', '', '', ['ga:visits'], max_results='foobar')

    @raises(AssertionError)
    def test_zero_max_results (self):
        gc.build_data_query('', '', '', ['ga:visits'], max_results=0)

    @raises(AssertionError)
    def test_negative_max_results (self):
        gc.build_data_query('', '', '', ['ga:visits'], max_results=-42)

    @raises(AssertionError)
    def test_max_results_gt_10k (self):
        gc.build_data_query('', '', '', ['ga:visits'], max_results=10001)

    def test_non_int_but_valid_max_results (self):
        R = {
            'end-date': '2012-01-01',
            'ids': 'ga:profile_id',
            'metrics': 'ga:visits',
            'max-results': 42,
            'start-date': '2012-01-01'
        }

        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results='42'))
        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results=42.0))

    def test_max_results_at_limits (self):
        R = {
            'end-date': '2012-01-01',
            'ids': 'ga:profile_id',
            'metrics': 'ga:visits',
            'max-results': 1,
            'start-date': '2012-01-01'
        }
        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results=1))
        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results='1'))
        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results=1.0))

        R = {
            'end-date': '2012-01-01',
            'ids': 'ga:profile_id',
            'metrics': 'ga:visits',
            'max-results': 10000,
            'start-date': '2012-01-01'
        }
        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results=10000))
        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results='10000'))
        eq_(R, gc.build_data_query('profile_id', '2012-01-01', '2012-01-01', ['ga:visits'], max_results=10000.0))


    @raises(gc.InvalidDateRange)
    def test_start_date_too_early (self):
        gc.build_data_query('profile_id', '2004-01-01', '2012-01-01', ['ga:visits'])

    @raises(gc.InvalidDateRange)
    def test_start_date_gt_end_date (self):
        gc.build_data_query('profile_id', '2013-01-01', '2012-01-01', ['ga:visits'])

    @raises(gc.InvalidDateRange)
    def test_end_date_passed_today (self):
        gc.build_data_query('profile_id', '2013-01-01', '2042-01-01', ['ga:visits'])

    def test_all_params_valid (self):
        R = {
            'start-date': '2012-01-01',
            'end-date': '2013-01-01',
            'ids': 'ga:123456',
            'metrics': 'ga:visits,ga:bounces',
            'dimensions': 'ga:date,ga:keyword',
            'sort': '-ga:date,ga:bounces',
            'filters': 'ga:bounces==1,ga:visits<10',
            'max-results': 5,
        }

        eq_(R, gc.build_data_query('123456', '2012-01-01', '20130101', ['ga:visits', 'bounces'],
            ['date', 'ga:keyword'], ['-date', 'ga:bounces'], ['bounces==1', 'ga:visits<10'],
            5))

