
from distutils.core import setup

import gaclient

setup(name='gaclient',
    version=gaclient.__version__,
    description='A easy to use interface to Google Analytics.',
    long_description='''This package provides an easy to use interface to Google Analytics.''',
    author='Tiemo Kieft',
    author_email='t.kieft@gmail.com',
    url='https://github.com/blubber/gaclient',
    license="Apache 2.0",
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: POSIX'
    ],
    keywords = ('google analytics'),
    packages=['gaclient'],
    install_requires=['google-api-python-client'])
