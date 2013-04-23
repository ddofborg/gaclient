
from gaclient import request

results = [
{u'columnHeaders': [{u'columnType': u'DIMENSION',
                     u'dataType': u'STRING',
                     u'name': u'ga:keyword'},
                    {u'columnType': u'METRIC',
                     u'dataType': u'INTEGER',
                     u'name': u'ga:visits'}],
 u'containsSampledData': False,
 u'id': u'https://www.googleapis.com/analytics/v3/data/ga?ids=ga:abc123&dimensions=ga:keyword&metrics=ga:visits&start-date=2010-01-01&end-date=2010-01-01&start-index=1&max-results=10',
 u'itemsPerPage': 10,
 u'kind': u'analytics#gaData',
 u'nextLink': u'https://www.googleapis.com/analytics/v3/data/ga?ids=ga:abc123&dimensions=ga:keyword&metrics=ga:visits&start-date=2010-01-01&end-date=2010-01-01&start-index=11&max-results=10',
 u'profileInfo': {u'accountId': u'1234567',
                  u'internalWebPropertyId': u'1234567',
                  u'profileId': u'abc123',
                  u'profileName': u'www.example.com',
                  u'tableId': u'ga:abc123',
                  u'webPropertyId': u'UA-123456-1'},
 u'query': {u'dimensions': u'ga:keyword',
            u'end-date': u'2010-01-01',
            u'ids': u'ga:abc123',
            u'max-results': 10,
            u'metrics': [u'ga:visits'],
            u'start-date': u'2010-01-01',
            u'start-index': 1},
 u'rows': [[u'keyword1', u'1'],
           [u"keyword2", u'1'],
           [u'keyword3', u'230'],
           [u'keyword4', u'2'],
           [u'keyword5', u'1'],
           [u'keyword6', u'1'],
           [u'keyword7', u'5'],
           [u'keyword8', u'1'],
           [u'keyword9', u'1'],
           [u'keyword10', u'1']],
 u'selfLink': u'https://www.googleapis.com/analytics/v3/data/ga?ids=ga:abc123&dimensions=ga:keyword&metrics=ga:visits&start-date=2010-01-01&end-date=2010-01-01&start-index=1&max-results=10',
 u'totalResults': 18,
 u'totalsForAllResults': {u'ga:visits': u'588'}},

 {u'columnHeaders': [{u'columnType': u'DIMENSION',
                     u'dataType': u'STRING',
                     u'name': u'ga:keyword'},
                    {u'columnType': u'METRIC',
                     u'dataType': u'INTEGER',
                     u'name': u'ga:visits'}],
 u'containsSampledData': False,
 u'id': u'https://www.googleapis.com/analytics/v3/data/ga?ids=ga:abc123&dimensions=ga:keyword&metrics=ga:visits&start-date=2010-01-01&end-date=2010-01-01&start-index=11&max-results=10',
 u'itemsPerPage': 10,
 u'kind': u'analytics#gaData',
 u'previousLink': u'https://www.googleapis.com/analytics/v3/data/ga?ids=ga:abc123&dimensions=ga:keyword&metrics=ga:visits&start-date=2010-01-01&end-date=2010-01-01&start-index=1&max-results=10',
 u'profileInfo': {u'accountId': u'1234567',
                  u'internalWebPropertyId': u'1234567',
                  u'profileId': u'abc123',
                  u'profileName': u'www.example.com',
                  u'tableId': u'ga:abc123',
                  u'webPropertyId': u'UA-123456-1'},
 u'query': {u'dimensions': u'ga:keyword',
            u'end-date': u'2010-01-01',
            u'ids': u'ga:abc123',
            u'max-results': 10,
            u'metrics': [u'ga:visits'],
            u'start-date': u'2010-01-01',
            u'start-index': 11},
 u'rows': [[u'keyword11', u'1'],
           [u'keyword12', u'1'],
           [u'keyword13', u'5'],
           [u'keyword14', u'1'],
           [u'keyword15', u'1'],
           [u'keyword16', u'1'],
           [u'keyword17', u'1'],
           [u'keyword28', u'1']],
 u'selfLink': u'https://www.googleapis.com/analytics/v3/data/ga?ids=ga:abc123&dimensions=ga:keyword&metrics=ga:visits&start-date=2010-01-01&end-date=2010-01-01&start-index=11&max-results=10',
 u'totalResults': 18,
 u'totalsForAllResults': {u'ga:visits': u'588'}}
]


class Service (object):

    def __init__ (self):
        self.iter = iter(results)

    def data (self, *args, **kwargs): return self
    ga = data
    get = data

    def execute (self):
        try:
            return self.iter.next()
        except StopIteration:
            return {}

class StubRequest (request.Request):

    def __init__ (self, *args, **kwargs):
        super(StubRequest, self).__init__(*args, **kwargs)
        self._limit = 10



