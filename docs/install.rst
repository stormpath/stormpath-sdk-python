Install
=======

The Stormpath Python SDK is best installed through `PyPI
<https://pypi.python.org/pypi/stormpath>`_.

PyPI is the official package repository for the Python programming language.

To install ``stormpath``, you can use the `pip
<http://pip.readthedocs.org/en/latest/>`_ tool like so::

    $ pip install stormpath

This will install the ``stormpath`` library locally.

Once you've installed the library, you'll want to check to make sure it was
installed properly by running::

    $ python
    >>> import stormpath

If this works (and doesn't give you an error), the ``stormpath`` library was
successfully installed!  If you're having problems getting the library
installed, you might want to read about:

- `virtualenv <http://www.virtualenv.org/en/latest/>`_
- `virtualenvwrapper <http://virtualenvwrapper.readthedocs.org/en/latest/>`_

These two tools making installing Python packages much simpler in complex
environments.


Upgrade
-------

If you'd like to upgrade to the latest version of the ``stormpath`` library, you
can also use ``pip``, with the ``-U`` flag, like so::

    $ pip install -U stormpath

This will automatically fetch and install the latest release.

.. note::
    Before upgrading the library, please refer to the `changelog
    <https://github.com/stormpath/stormpath-sdk-python/blob/master/CHANGES.md>`_
    to ensure the new release won't break anything.
