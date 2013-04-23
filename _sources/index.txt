
.. automodule:: gaclient

Google Analytics Client
~~~~~~~~~~~~~~~~~~~~~~~
Google Analytics Client is a wrapper for the google-api-python-client package
to make using Google Analytics easier. The library automatically downloads
more result pages if available, and converts string data into Python types.

The main interface is :ref:`GoogleAnalyticsClient`, the file `sample.py` contains
a working example.

Contents
--------
* :ref:`license`
* :ref:`reference`
    * :ref:`GoogleAnalyticsClient`
    * :ref:`Request`
    * :ref:`utilities`

.. _license:

License and Copyright
---------------------
Copyright (C) 2013 Tiemo Kieft <t.kieft@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
You may not use this module except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

.. _reference:

Reference
---------

.. _GoogleAnalyticsClient:

GoogleAnalyticsClient
_____________________

.. autoclass:: GoogleAnalyticsClient
    :members:

.. _Request:

Request
_______

.. autoclass:: Request
    :members:

.. _utilities:

Utility Functions
_________________

.. autofunction:: gaclient.client.parse_date
