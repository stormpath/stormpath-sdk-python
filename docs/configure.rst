Configure
=========

Now that you've got ``stormpath`` installed, let's get you set up!


Create a Stormpath Account
--------------------------

Before continuing, you need a `Stormpath <https://stormpath.com/>`_ account.  If
you don't already have one, you can create one here: https://api.stormpath.com/register


Create an API Key Pair
----------------------

Next, you need to generate an API key pair, so that you can talk to the
Stormpath API endpoints.

First, log into your Stormpath dashboard here: https://api.stormpath.com/login

Next, click the big ``Create API Key`` button -- this will generate a new API
key pair for you, and download this newly created key pair.  The file that will
be downloaded is named ``apiKey.properties``.

This file contains two variables, an ``id`` and ``secret``.  These are the two
keys that allow you to communicate with Stormpath.

.. note::
    These credentials give you unlimited access to Stormpath -- please keep them
    safe!  You should never make these credentials public -- they should never
    be checked into version control, etc.

    Generally, you'll want to do one of two things:

    - Store this ``apiKey.properties`` file somewhere safe in your home
      directory (``~/.stormpath/apiKey.properties``).
    - Store these credentials as environment variables named
      ``STORMPATH_API_KEY_ID`` and ``STORMPATH_API_KEY_SECRET``.

Stormpath allows you to have as many API key pairs as you'd like -- you can add
and remove them at any time.  This allows you to maintain high levels of access
security by periodically rotating API key pairs.
