"""Python packaging stuff."""


from os import chdir, system
from os.path import abspath, dirname, join, normpath
from subprocess import call
from sys import exit, version_info

from setuptools import setup, find_packages, Command

from stormpath import __version__


PY_VERSION = version_info[:2]


class BaseCommand(Command):
    user_options = []

    def pytest(self, *args):
        ret = call(['py.test', '--quiet', '--cov-report=term-missing', '--cov', 'stormpath'] + list(args))
        exit(ret)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(BaseCommand):

    description = 'run self-tests'

    def run(self):
        self.pytest('--ignore', 'tests/live', 'tests')


class LiveTestCommand(BaseCommand):

    description = 'run live-tests'

    def run(self):
        self.pytest('tests/live')


class DocCommand(BaseCommand):

    description = 'generate documentation'

    def run(self):
        try:
            chdir('docs')
            ret = system('make html')
            exit(ret)
        except OSError as e:
            print(e)
            exit(-1)


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
        'isodate>=0.5.4',
    ],
    extras_require = {
        'test': ['codacy-coverage', 'mock', 'python-coveralls', 'pytest', 'pytest-cov'],
    },
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
        'Programming Language :: Python :: 3.4',
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
        'docs': DocCommand,
    },
    long_description = open(normpath(join(dirname(abspath(__file__)), 'README.rst'))).read(),
)
