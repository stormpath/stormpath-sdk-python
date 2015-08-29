from setuptools import setup, find_packages, Command
import sys
import os
import subprocess

from stormpath import __version__


PY_VERSION = sys.version_info[:2]


class BaseCommand(Command):
    user_options = []

    def pytest(self, *args):
        ret = subprocess.call(["py.test", "--quiet",
            "--cov-report=term-missing", "--cov", "stormpath"] + list(args))
        sys.exit(ret)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(BaseCommand):

    description = "run self-tests"

    def run(self):
        self.pytest('--ignore', 'tests/live', 'tests')


class LiveTestCommand(BaseCommand):

    description = "run live-tests"

    def run(self):
        self.pytest('tests/live')


class TestDepCommand(BaseCommand):

    description = "install test dependencies"

    def run(self):
        cmd = [
            "pip", "install", "pytest", "pytest-cov", "mock",
            "python-dateutil"]
        ret = subprocess.call(cmd)
        sys.exit(ret)


class DocCommand(BaseCommand):

    description = "generate documentation"

    def run(self):
        try:
            os.chdir('docs')
            ret = os.system('make html')
            sys.exit(ret)
        except OSError as e:
            print(e)
            sys.exit(-1)

# To install the stormpath library, open a Terminal shell, then run this
# file by typing:
#
# python setup.py install

setup(
    name = 'stormpath',
    version = __version__,
    description = 'Official Stormpath SDK, used to interact with the Stormpath REST API.',
    author = 'Stormpath, Inc.',
    author_email = 'python@stormpath.com',
    url = 'https://github.com/stormpath/stormpath-sdk-python',
    zip_safe = False,
    keywords = ['stormpath', 'authentication', 'users', 'security'],
    install_requires = [
        'PyJWT>=1.0.0',
        'oauthlib>=0.6.3',
        'requests>=2.4.3',
        'six>=1.6.1',
        'python-dateutil>=2.4.0',
        'pydispatcher>=2.0.5',
        'isodate'>='0.5.4'
    ],
    packages = find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
    ],
    cmdclass = {
        'test': TestCommand,
        'livetest': LiveTestCommand,
        'testdep': TestDepCommand,
        'docs': DocCommand,
    },
    long_description="""\
    Stormpath SDK
    -------------

    DESCRIPTION

    The Stormpath Python SDK allows any Python-based application to easily use
    the Stormpath user management service for all authentication and
    access control needs.

    When you make SDK method calls, the calls are translated into HTTPS
    requests to the Stormpath REST+JSON API. The Stormpath Python SDK provides
    a clean object-oriented paradigm natural to Python developers and
    alleviates the need to know how to make REST+JSON requests.

    LICENSE

    The Stormpath Python SDK is distributed under the Apache Software License.
    """,
)
