'''
    Google Analytics Client code sample
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    The example in this file is somewhat contrived, but it does demonstrate
    the usage of this package. To use this sample you need to have all
    information required to create a
    :class:`oauth2client.client.OAuth2Credentials` object (client id, client
        secret and a refresh or access token), and an active GA profile.

    The example will download at most 50 of yesterday's organic keywords,
    sorted by number of visits, and will then print a short summary.
'''

import httplib2
from apiclient.discovery import build
from oauth2client.client import OAuth2Credentials

import gaclient

PROFILE = 'PROFILE_ID'
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRENT'

# Either one of these tokens should be supplied.
REFRESH_TOKEN = ''
ACCESS_TOKEN = ''

# Create a credentials object
credentials = OAuth2Credentials(
        ACCESS_TOKEN, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, "",
        "https://accounts.google.com/o/oauth2/token",
        "Google Analytics Client example")

# Creates and authorized a HTTP object
http = httplib2.Http()
credentials.authorize(http)

# Create a service object
service = build('analytics', 'v3', http=http)

# Create a client for donwloading keywords, visits and bounces.
client = gaclient.GoogleAnalyticsClient(service, PROFILE, ['ga:keyword'],
    ['ga:visits', 'ga:bounces'], filters=['ga:medium==organic'],
    sort=['-ga:visits'], limit=50)

# Download yestardays top 50 keywords sorted by visits. auto_advance is turned of
# otherwise the client will download all results.
records = client.download_date_range(auto_advance=False)


# Print a short summary of the data.
print('| {0:40s} | {1:8s} | {2:8s} | {3:10s}'.format('keyword', 'visits', 'bounces', 'bouncerate'))
print('|{}+{}+{}+{}|'.format('-' * 42, '-' * 10, '-' * 10, '-' * 12))

total_visits = 0
total_bounces = 0

for record in records:
    brate = record.bounces / float(record.visits) if record.visits > 0 else 'inf'
    print('| {0:40s} | {1:>8d} | {2:>8d} | {3:>10.4f} |'.format(record.keyword[:40], record.visits, record.bounces, brate))
    total_visits += record.visits
    total_bounces += record.bounces

print('|{}+{}+{}+{}|'.format('-' * 42, '-' * 10, '-' * 10, '-' * 12))
print('| {0:40s} | {1:>8d} | {2:>8d} | {3:10s} |'.format('total', total_visits, total_bounces, ''))
