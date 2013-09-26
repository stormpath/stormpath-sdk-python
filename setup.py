#
# Copyright 2012, 2013 Stormpath, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from setuptools import setup, find_packages, Command
import sys
import os
import subprocess

from stormpath import __version__


PY_VERSION = sys.version_info[:2]


class BaseCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(BaseCommand):

    description = "run self-tests"

    def run(self):
        os.chdir('tests')
        ret = subprocess.call(["py.test", "--quiet",
            "--cov-report=term-missing", "--cov", "stormpath",
            "--ignore", "test_live.py"])
        sys.exit(ret)


class LiveTestCommand(BaseCommand):

    description = "run live-tests"

    def run(self):
        os.chdir("tests")
        ret = subprocess.call(["py.test", "--quiet",
            "--cov-report=term-missing", "--cov", "stormpath", "test_live.py"])
        sys.exit(ret)


class TestDepCommand(BaseCommand):

    description = "install test dependencies"

    def run(self):
        cmd = ["pip", "install", "pytest", "pytest-cov", "HTTPretty"]
        if PY_VERSION < (3, 3):
            cmd.append("mock")
        ret = subprocess.call(cmd)
        sys.exit(ret)


class DocCommand(BaseCommand):

    description = "generate documentation"

    def run(self):
        try:
            os.chdir('doc')
            ret = os.system('make html')
            sys.exit(ret)
        except OSError as e:
            print(e)
            sys.exit(-1)

# To install the stormpath library, open a Terminal shell, then run this
# file by typing:
#
# python setup.py install

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 2",
]

setup(
    name="stormpath-sdk",
    version=__version__,
    description="Stormpath SDK used to interact with the Stormpath REST API",
    author="Elder Crisostomo",
    author_email="elder@stormpath.com",
    url="https://github.com/stormpath/stormpath-sdk-python",
    zip_safe=False,
    keywords=["stormpath", "authentication"],
    install_requires=["requests>=1.1.0"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        ].extend(classifiers),
    cmdclass={
        'test': TestCommand,
        'livetest': LiveTestCommand,
        'testdep': TestDepCommand,
        'docs': DocCommand
    },
    long_description="""\
    Stormpath SDK
    -------------

    DESCRIPTION
    The Stormpath Python SDK allows any Python-based application to easily use
    the Stormpath user management service for all authentication and
    access control needs.

    When you make SDK method calls, the calls are translated into HTTPS
    requests to the Stormpath REST+JSON API. The Stormpath Python SDK therefore
    provides a clean object-oriented paradigm natural to Python developers and
    alleviates the need to know how to make REST+JSON requests.

    LICENSE The Stormpath Python SDK is distributed under the
    Apache Software License.
    """)
