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


Create a Client
---------------

The first step in actually connecting to Stormpath and getting stuff done is to
create a ``client`` object.  This object is responsible for handling all
connections to Stormpath -- and it does this very well!

Create a ``client`` like so::

    from os import environ
    from os.path import expanduser

    from stormpath.client import Client


    # Method 1: Create the client with your apiKey.properties file.
    client = Client(api_key_file_location=expanduser('~/.stormpath/apiKey.properties'))

    # Method 2: Create the client using environment variables.
    client = Client(
        id = environ.get('STORMPATH_API_KEY_ID'),
        secret = environ.get('STORMPATH_API_KEY_SECRET'),
    )


Creating an Application (and Directory)
---------------------------------------

The next thing you'll want to do is create a Stormpath Application.  You can
think of a Stormpath Application as a project -- if you're planning on building
a website called ``evilgenius.es``, for instance, you might want to create a
Stormpath Application named ``evilgeniuses``.

Stormpath Applications are unique containers that will hold all of your users.
Now, Stormpath also has something called a 'Directory'.  Think of a Directory as
a group of unique users within an Application.

Let's say your ``evilgenius.es`` website has URLs for each evil genius to log
into.  You might have URLs that look like this:

- https://vader.evilgenius.es
- https://professor-chaos.evilgenius.es
- etc.

In this case, assuming each sub-domain allows users to sign up and coordinate
evil plots together, you might want to have:

- One Stormpath Application named ``evilgeniuses``.
- One Stormpath Directory named ``vader``.
- One Stormpath Directory named ``professor-chaos``.

This way, if a minion, ``aquaman``, is working for two evil geniuses at the same
time, he'll be able to create an account for each of those domains using the
same login details.

Make sense?  OK!

Now, about creating that application -- let's do it (we won't need more than one
directory here, so let's just create one with the same name as our Application
to make things simple)::

    # NOTE: The 'description' field is optional!
    app = client.applications.create({
        'name': 'evilgeniuses',
        'description': 'A gathering place for only the evilest of villains.',
    }, create_directory=True)

The ``create_directory`` argument will automatically create a directory for you!

Now that you've created a ``client`` and ``application``, you're ready to do
some cool stuff!
