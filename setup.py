__author__ = 'ecrisostomo'

from distutils.core import setup
from pkgutil import walk_packages

import stormpath


def find_packages(path='.', prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, is_pkg in walk_packages(path, prefix):
        if is_pkg:
            yield name


# To install the stormpath library, open a Terminal shell, then run this
# file by typing:
#
# python setup.py install
REQUIRES = ["httplib2 (>= 0.7)", "unittest2py3k", "PyYAML (>= 3.10)"]

setup(
    name = "stormpath-sdk",
    version = stormpath.__version__,
    description = "Stormpath SDK used to interact with the Stormpath REST API",
    author = "Elder Crisostomo",
    author_email = "elder@stormpath.com",
    url = "https://github.com/stormpath/stormpath-sdk-python",
    keywords = ["stormpath","authentication"],
    requires = REQUIRES,
    packages = list(find_packages(stormpath.__path__, stormpath.__name__)),
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
        "Programming Language :: Python :: 3.2",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        ],
    long_description = """\
    Stormpath SDK
    -------------

    DESCRIPTION
    The Stormpath Python SDK allows any Python-based application to easily use the
    Stormpath user management service for all authentication and access control needs.

    When you make SDK method calls, the calls are translated into HTTPS requests to
    the Stormpath REST+JSON API. The Stormpath Python SDK therefore provides a clean
    object-oriented paradigm natural to Python developers and alleviates the need to
    know how to make REST+JSON requests.

    LICENSE The Stormpath Python SDK is distributed under the Apache Software License.
    """ )