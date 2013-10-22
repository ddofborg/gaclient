
from distutils.core import setup

import gaclient

setup(name='gaclient',
    version=gaclient.__version__,
    description='A easy to use interface to Google Analytics.',
    long_description=gaclient.__doc__,
    author=gaclient.__author__,
    author_email='t.kieft@gmail.com',
    url='http://www.python-gaclient.org',
    license="Apache 2.0",
    platform='any',
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
    install_requires=['requests', 'requests_oauthlib'])
