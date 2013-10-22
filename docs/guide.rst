
.. _guide:

Installation
============

The following section describes the installation of gaclient.


Pip and Distribute
------------------
The easiest way to install gaclient is through either pip (recommended)
or easy_install::

    $ pip install gaclient
    # or
    $ easy_install gaclient


From Source
-----------

You can clone gaclient's source from `Github <https://github.com/blubber/gaclient>`_::

    $ git clone https://github.com/blubber/gaclient.git

then install the package with::

    $ python setup.py install

Make sure you install the dependencies first, the following packages
are required, you can use pip or easy_install to install them:

    * requests
    * requests_oauthlib


.. _registration:

Application Registration
========================

In order to download data from Google Analytics you need to register
your application with Googles `Cloud Console <https://cloud.google.com/console#/project>`_.
If you haven't already, use the **Create Project** button to create a new project.

Next, on the left hand side select ``APIs & auth > Registered apps`` and click the
``REGISTER APP`` button. Fill out the form and select ``Web application`` as ``Platform``.

Your ``CLIENT_ID`` and ``CLIENT_SECRET`` are listed under the ``OAuth 2.0 Client ID``
tab. Make sure you keep your ``CLIENT_SECRET`` secret!

Fill in the appropriate values in the ``Web Origin`` and ``Redirect URI`` sections.

You are now ready to start using the Analytics API.


Workflow
========

The following section describes the complete workflow from getting
the user's consent to downloading data from Google Analytics.

In order to use the Google Analytics API your application needs to be
registered in Google's Cloud Console, see :ref:`registration` for
instructions on how to do that.

OAuth 2.0
---------
Google uses a system called OAuth 2.0 to authenticate and authorize
your requests to their service.

In order to use access a Google Analytics account you first must ask
the user's consent. After the user agrees Google redirects them to
a URI on your webserver called the **redirect uri**. The call to the
redirect URI contains a **refresh token** which can be used to acquire
an **access token**, this access token can be used to access the user's
Analytics data.

Access tokens expire after one hour, however, a refresh token will not expire
at all. It is therefore recommended that you store the refresh token in your
database for continue use. This allows you to access the data without asking
the user for consent each time. Users can however revoke your refresh token.

For more information on using OAuth 2.0 to access Google Analytics please
read `Using OAuth 2.0 to Access Google APIs <https://developers.google.com/accounts/docs/OAuth2>`_.


Quickstart
==========
This section contains a step-by-step guide on how to access Analytics data once
your application is registered.

Acquiring tokens
----------------
Although gaclient can generate an appropriate consent URI for you using the
:func:`gaclient.generate_consent_url` function. After the users gives consent
and Google redirects them to your redirect URI you will have to acquire the
refresh token yourself, refer to
`Using OAuth 2.0 to Access Google APIs <https://developers.google.com/accounts/docs/OAuth2>`_
for more information and examples on how to achieve this.

From this point on it is assumed that the following variables exist in your namespace
and that they are appropriately initialized:

  * CLIENT_ID: your application's client id;
  * CLIENT_SECRET: your application's client secret;
  * PROFILE_ID: The id of the Google Analytics profile you whish to access;
  * REFRESH_TOKEN: The refresh token to use.


Getting Started
---------------
In this section we are going to build a simple script to download some
data from the user's Analytics profile. Let's start out with some
boilerplate::

    import gaclient

    CLIENT_ID = ' ... '
    CLIENT_SECRET = ' ... '
    PROFILE_ID = 'ga:...'
    REFRESH_TOKEN = ' ... '


To do any request against Google Analytics we first need an outhorized
OAuth 2.0 session. We can build one with the :func:`gaclient.build_session`
utility. The returned session is tied to a specific user::

    session = gaclient.build_session(CLIENT_ID, CLIENT_SECRET,
        {'refresh_token': REFRESH_TOKEN})

This ``session`` object is tied to the user's account, but not to a
specific Google Analytics profile.

We are now ready to query some data, we use a :class:`gaclient.Cursor`
to download some data from analytics. The Cursor instance will download
a single page of data.

When we create the Cursor instance we need to supply it with an 
OAuth 2 session and any argument we wish to pass into
:func:`build_data_query`, for example::

    cursor = gaclient.Cursor(session, PROFILE_ID,
        '2012-01-01', '2012-01-01',    # Date range (inclusive)
        ['visits', 'bounces'],         # List of metrics to download
        ['keyword'],                   # List of dimensions
        sort=['-visits'],              # Order by visits in descending order
        max_results=25
    )

    print('The query contained{} sampled data!'.format('' if cursor.sampled else ' no'))
    print('keyword              visits bounces bouncerate')

    for row in cursor:
        br = 100.0 * row['bounces'] / row['visits']
        print('{0:20s} {1:6d} {2:7d} {3:3.2f}%'.format(
            row['keyword'][:20], row['visits'], row['bounces'], br))


Upon executing this code gaclient will download at most 25 rows from Google
Analytics sorted by visits, in **descending** order.

If we want to download more data then fits in a single request then we can
either use `next_cursor` property of :class:`gaclient.Cursor` to build the
next cursor object. But it is easier to just use a :class:`ResponseIterator`
to loop over the results::

    it = gaclient.ResponseIterator(cursor, limit=30)

    print('The query contained{} sampled data!'.format('' if cursor.sampled else ' no'))
    print('keyword              visits bounces bouncerate')

    for row in it:
        br = 100.0 * row['bounces'] / row['visits']
        print('{0:20s} {1:6d} {2:7d} {3:3.2f}%'.format(
            row['keyword'][:20], row['visits'], row['bounces'], br))

Because we specified a `limit` value of 30 the client will now download
at most 30 rows of data from Google Analytics and print them on the screen.

By turning on :ref:`logging` you can get some more insight into the
requests that are executed.
