
from distutils.core import setup

import re


def get_current_version ():
    version = 'UNKNOWN'

    with open('gaclient.py', 'r') as fp:
        matches = re.search('__version__ = [\'"](.*)[\'"]\n', fp.read())
        if matches:
            version = matches.group(1)

    return version


setup(name='gaclient',
    version=get_current_version(),
    description='An easy to use interface to Google Analytics.',
    long_description=open('README.rst', 'r').read(),
    author='Tiemo Kieft',
    author_email='t.kieft@gmail.com',
    url='http://www.python-gaclient.org',
    license="Apache 2.0",
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    keywords = ('google analytics'),
    py_modules=['gaclient'],
    install_requires=['requests_oauthlib>=0.4.0'])
