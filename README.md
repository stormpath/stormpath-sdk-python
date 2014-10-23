# Stormpath Python SDK

[![Latest Version](https://pypip.in/version/stormpath/badge.png)](https://pypi.python.org/pypi/stormpath/)
[![Downloads](https://pypip.in/download/stormpath/badge.png)](https://pypi.python.org/pypi/stormpath/)
[![Build Status](https://travis-ci.org/stormpath/stormpath-sdk-python.png?branch=master)](https://travis-ci.org/stormpath/stormpath-sdk-python)


Stormpath is the first simple and secure user management and authentication
service for developers *like you*.  This Python SDK makes using Stormpath with
your application a painless, and even enjoyable process.


## Install

To get started, install the `stormpath` library using
[Pip](http://www.pip-installer.org/en/latest/).

```bash
$ pip install stormpath
```

If this doesn't work, you might need to install `pip` on your computer.  See the
[Pip installation guide](http://www.pip-installer.org/en/latest/installing.html)
for more information.


## Quickstart Guide

If you have not already done so, register as a developer on
[Stormpath](https://stormpath.com/), and create (and download) an API Key pair
(this consists of an `APIKeyID` and an `APIKeySecret`).

When you first create your API Key pair using the Stormpath interface, you'll be
prompted to download a file named `apiKey.properties`.  This file contains your
API Key pair information, which you'll need below.


### Create a Client

Next, you'll want to create a Stormpath API client.  You can do this in one of
two ways:

```python
from stormpath.client import Client

# 1) By using the apiKey.properties file you previously downloaded.
client = Client(api_key_file_location='/path/to/apiKey.properties')

# 2) By specifying your API Key pair credentials manually.
client = Client(
    id = STORMPATH_API_KEY_ID,
    secret = STORMPATH_API_KEY_SECRET,
)
```

**NOTE**: Once you've created a client, you can use it for the life of your
application.  There's no need to recreate a new client for each new request --
the client is smart, and will smartly handle SDK requests.


### List Your Applications and Directories

To view a list of all your Stormpath
[Applications](http://docs.stormpath.com/rest/product-guide/#applications) and
[Directories](http://docs.stormpath.com/rest/product-guide/#directories), you
can easily iterate through the `client.applications` and `client.directories`
generators show below:

```python
for application in client.applications:
    print 'Application (name):', application.name
    print 'Application (href):', application.href

for directory in client.directories:
    print 'Directory (name):', directory.name
    print 'Directory (href):', directory.href
```


### Retrieve a Given Application and Directory

If you know the full
[Application](http://docs.stormpath.com/rest/product-guide/#applications) and
[Directory](http://docs.stormpath.com/rest/product-guide/#directories) `href`
(like the ones show in the previous example), you can easily retrieve the
`application` and `directory` objects directly, like so:

```python
application = client.applications.get('https://api.stormpath.com/v1/application/<uid>')
directory = client.directories.get('https://api.stormpath.com/v1/directories/<uid>')
```

Easy, right?


### Create an Application

As you can probably guess, creating an
[Application](http://docs.stormpath.com/rest/product-guide/#applications) is
also simple business.

The example below shows you how to create an
[Application](http://docs.stormpath.com/rest/product-guide/#applications) by
itself, **or**, if you want, an
[Application](http://docs.stormpath.com/rest/product-guide/#applications) and a
[Directory](http://docs.stormpath.com/rest/product-guide/#directories) together!

The benefits to creating them at the same time is that all the association stuff
is handled automatically!

```python
# Create an Application by itself.
application = client.applications.create({
    'name': 'Instagram',
    'description': 'A place to post photos of your food.',
})

# Create an Application AND Directory.
application = client.applications.create({
    'name': 'Instagram',
    'description': 'A place to post photos of your food.',
}, create_directory=True)
```


### Create an Account in an Application

Now that you've (hopefully!) already created an
[Application](http://docs.stormpath.com/rest/product-guide/#applications) and
associated
[Directory](http://docs.stormpath.com/rest/product-guide/#directories), we can
now move on to creating a user
[Account](http://docs.stormpath.com/rest/product-guide/#accounts).

You can create a new
[Account](http://docs.stormpath.com/rest/product-guide/#accounts) on either an
[Application](http://docs.stormpath.com/rest/product-guide/#applications) or
[Directory](http://docs.stormpath.com/rest/product-guide/#directories) instance:

```python
# Create a new Account on an Application instance.
emusk = application.accounts.create({
    'given_name': 'Elon',
    'surname': 'Musk',
    'email': 'emusk@spacex.com',
    'password': 'KINGofSPACE!W00',
})

# Create a new Account on a Directory instance.
pgraham = directory.accounts.create({
    'given_name': 'Paul',
    'surname': 'Graham',
    'email': 'paul@ycombinator.com',
    'username': 'pg',
    'password': 'STARTUPSar3th3b3sT!',
})
```


### Update an Account

Once you have a few
[Accounts](http://docs.stormpath.com/rest/product-guide/#accounts) created,
updating them is equally simple:

```python
pgraham.middle_name = 'Iceman'
pgraham.save()
```


### Authenticate an Account

Now that you have some user
[Accounts](http://docs.stormpath.com/rest/product-guide/#accounts), we'll cover
how you can securely check a user's credentials:

```python
from stormpath.error import Error as StormpathError

try:
    auth_attempt = application.authenticate_account('pg', 'STARTUPSar3th3b3sT!')
except StormpathError, err:
    print 'Human friendly error message:', err.message
    print 'Developer friendly error message:', err.developer_message
```


### Send a Password Reset Email

It's often very useful to be able to reset a user's account password.  Doing
this is simple using the `send_password_reset_email` method:

```python
application.send_password_reset_email('emusk@spacex.com')
```


### Create a Group

In Stormpath, the best way to think about roles and permissions is with
[Groups](http://docs.stormpath.com/rest/product-guide/#groups).
[Groups](http://docs.stormpath.com/rest/product-guide/#groups) allow you to
categorize [Accounts](http://docs.stormpath.com/rest/product-guide/#accounts),
and build complex permissions systems.

Creating a new [Group](http://docs.stormpath.com/rest/product-guide/#groups) is
easy:

```python
directory.groups.create({
    'name': 'Administrators',
    'description': 'This group holds all Administrator accounts with *full* system access.',
})
```


### Add an Account to a Group

To add an [Account](http://docs.stormpath.com/rest/product-guide/#accounts) to a
[Group](http://docs.stormpath.com/rest/product-guide/#groups), just do the
following:

```python
group.add_account(pgraham)
```

**NOTE**: An [Account](http://docs.stormpath.com/rest/product-guide/#accounts)
may belong to an infinite number of
[Groups](http://docs.stormpath.com/rest/product-guide/#groups).


### Store Custom Account Data

One of the newest (and most popular) of Stormpath's features is the ability to
store variable data with each
[Account](http://docs.stormpath.com/rest/product-guide/#accounts) instance.

The example below stores some custom data:

```python
pgraham.custom_data['favorite_company'] = 'Stormpath'
pgraham.custom_data['millions_invested'] = 99.999999
pgraham.custom_data['billions_acquired'] = 5
pgraham.custom_data['favorite_movie'] = 'The Lion King'
pgraham.custom_data.save()

print 'All custom data:', dict(pgraham.custom_data)
```

**NOTE**: None of the custom data entered above is actually saved to Stormpath
until the `.save()` method is called.


## Common Uses

Below you'll find information on using our Python SDK to accomplish commonly
requested tasks.


### Accessing Resources

Most of the work you do with Stormpath is done through the
[Applications](http://docs.stormpath.com/rest/product-guide/#applications) and
[Directories](http://docs.stormpath.com/rest/product-guide/#directories) you
have created.

If you know what your
[Application](http://docs.stormpath.com/rest/product-guide/#applications) or
[Directory](http://docs.stormpath.com/rest/product-guide/#directories) `href`
is, you can fetch the instance directly:

```python
application = client.applications.get(application_url)
directory = client.directories.get(directory_url)
```

The `applications` and `directories` properties on the `client` instance allow
you to iterate through *all* existing
[Applications](http://docs.stormpath.com/rest/product-guide/#applications) and
[Directories](http://docs.stormpath.com/rest/product-guide/#directories),
respectively.

```python
for application in client.applications:
    print '%s (%s)' % (application.name, application.href)
```

**NOTE**: If you have a lot of
[Applications](http://docs.stormpath.com/rest/product-guide/#applications), the
above code snippet will take a while to run, as it will iterate through *all*
applications.

There are, of course, other resources available to iterate through, as well!

If you're on a [Client](http://docs.stormpath.com/rest/product-guide/#clients)
instance, you can iterate through the following objects:

- `applications` - Iterate through all
  [Applications](http://docs.stormpath.com/rest/product-guide/#applications).

- `directories` - Iterate through all
  [Directories](http://docs.stormpath.com/rest/product-guide/#directories).

- `tenant` - A **single** link to your current
  [Tenant](http://docs.stormpath.com/rest/product-guide/#tenants).

If you're on an
[Application](http://docs.stormpath.com/rest/product-guide/#applications)
instance, you can iterate through the following objects:

- `accounts` - Iterate through all
  [Accounts](http://docs.stormpath.com/rest/product-guide/#accounts).

- `groups` - Iterate through all
  [Groups](http://docs.stormpath.com/rest/product-guide/#groups).

- `tenant` - A **single** link to your current
  [Tenant](http://docs.stormpath.com/rest/product-guide/#tenants).

If you're on a
[Directory](http://docs.stormpath.com/rest/product-guide/#directories) instance,
you can iterate through the following objects:

- `accounts` - Iterate through all
  [Accounts](http://docs.stormpath.com/rest/product-guide/#accounts).

- `groups` - Iterate through all
  [Groups](http://docs.stormpath.com/rest/product-guide/#groups).

- `tenant` - A **single** link to your current
  [Tenant](http://docs.stormpath.com/rest/product-guide/#tenants).

If you're on a [Group](http://docs.stormpath.com/rest/product-guide/#groups)
instance, you can iterate through the following objects:

- `accounts` - Iterate through all
  [Accounts](http://docs.stormpath.com/rest/product-guide/#accounts).

- `tenant` - A **single** link to your current
  [Tenant](http://docs.stormpath.com/rest/product-guide/#tenants).


### Registering New Accounts

When creating new
[Accounts](http://docs.stormpath.com/rest/product-guide/#accounts) in Stormpath,
you have several options.

There are only 4 required fields for each new
[Account](http://docs.stormpath.com/rest/product-guide/#accounts) you create:

- `given_name` - The user's first name.
- `surname` - The user's last name.
- `email` - The user's email address.
- `password` - The user's plain text password -- this will be hashed and
  securely stored when sent to Stormpath.

There are several other optional fields which can be used:

- `middle_name` - The user's middle name.
- `status` - The user's status (can be one of: 'enabled', 'disabled',
  'unverified').
- `custom_data` - A dictionary of custom user data (up to 10MB, per user).
- `username` - A username.

If you have custom Stormpath workflows configured (rules that say what passwords
are allowed, if email verification is required, etc.), you can optionally choose
to create a new user account and **skip applying these workflow rules** by using
the `registration_workflow_enabled` flag:

```python
# This example will skip over the normal workflow you've got configured, and
# just create the user.
account = directory.accounts.create({
    'given_name': 'Michael',
    'surname': 'Bay',
    'middle_name': 'BOOM!',
    'email': 'michael@bay.com',
    'password': 'ILOVE3xpl0si0ns!!!!!',
}, registration_workflow_enabled=False)
```

If the [Directory](http://docs.stormpath.com/rest/product-guide/#directories)
has been configured with an email verification workflow and a non-Stormpath
URL, you have to pass the verification token sent to the URL in a `sptoken`
query parameter back to Stormpath to complete the workflow.  This is done
through the `verify_email_token` on the `accounts` collection.


### Authentication

When you authenticate users, you can provide either the `username` OR `email`,
and `password` fields.  This way you can accept registration using *only* email
and password, username and password, or email, username, and password.

When users are successfully authenticated, an `AuthenticationResult` object will
be return, with the
[Account](http://docs.stormpath.com/rest/product-guide/#accounts) attached.

To check for successful authentication, you should do something like the
following:

```python
from stormpath.error import Error as StormpathError

try:
    account = application.authenticate_account('username_or_email',
    'password').account
except StormpathError, err:
    print 'Human friendly error message:', err.message
    print 'Developer friendly error message:', err.developer_message
except Exception, err:
    print 'Something unexpected happened:', err
```


### Password Reset

A password reset workflow, if configured on the
[Directory](http://docs.stormpath.com/rest/product-guide/#directories) the
[Account](http://docs.stormpath.com/rest/product-guide/#accounts) is registered
on, can be kicked off with the `send_password_reset_email` method on an
[Application](http://docs.stormpath.com/rest/product-guide/#applications):

```python
application.send_password_reset_email('john.smith@example.com')
```

If the workflow has been configured to verify through a non-Stormpath URL, you
can verify the token sent in the query parameter `sptoken` with the
`verify_password_reset_token` method on the
[Application](http://docs.stormpath.com/rest/product-guide/#applications).

With the [Account](http://docs.stormpath.com/rest/product-guide/#accounts)
acquired you can then update the password:

```python
account.password = new_password
account.save()
```

**NOTE**: Confirming a new password is left up to the web application code
calling the Stormpath SDK.  The SDK does not require confirmation.


### ACL Through Groups

Memberships of [Accounts](http://docs.stormpath.com/rest/product-guide/#accounts)
in certain [Groups](http://docs.stormpath.com/rest/product-guide/#groups) can be
used as an authorization mechanism.  As the `groups` collection property on an
[Account](http://docs.stormpath.com/rest/product-guide/#accounts) instance is
iterable, you can use any of that module's methods to determine if an
[Account](http://docs.stormpath.com/rest/product-guide/#accounts) belongs to a
specific [Group](http://docs.stormpath.com/rest/product-guide/#groups).

You can create [Groups](http://docs.stormpath.com/rest/product-guide/#groups)
and assign them to
[Accounts](http://docs.stormpath.com/rest/product-guide/#accounts) using the
Stormpath web console, or programmatically 

Creating a [Group](http://docs.stormpath.com/rest/product-guide/#groups) is
easy, just call the `create` method from your
[Directory](http://docs.stormpath.com/rest/product-guide/#directories) instance:

```python
group = directory.groups.create({'name': 'Administrators'})
```

Group membership can be created by:

* Explicitly creating a
  [GroupMembership](http://docs.stormpath.com/rest/product-guide/#group-memberships)
  resource with your client:

  ```python
  group_memebership = client.group_memberships.create(group, account)
  ```

* Using the `add_group` method on the
  [Account](http://docs.stormpath.com/rest/product-guide/#accounts) instance:

  ```python
  account.add_group(group)
  ```

* Using the `add_account` method on the
  [Group](http://docs.stormpath.com/rest/product-guide/#groups) instance:

  ```python
  group.add_account(account)
  ```


### Managing Custom Data

[Groups](http://docs.stormpath.com/rest/product-guide/#groups) and
[Accounts](http://docs.stormpath.com/rest/product-guide/#accounts) have
[CustomData](http://docs.stormpath.com/rest/product-guide/#custom-data) fields
that act as a dictionary:

* Accessing custom data field:

  ```python
  print account.custom_data['favorite_color']
  print group.custom_data['favorite_api_company']
  ```

* Creating or updating a
  [CustomData](http://docs.stormpath.com/rest/product-guide/#custom-data) field:

  ```python
  account.custom_data['rank'] = 'Captain'
  account.custom_data.save()

  group.custom_data['affiliation'] = 'NCC-1701'
  group.custom_data.save()
  ```

* Deleting a
  [CustomData](http://docs.stormpath.com/rest/product-guide/#custom-data) field:

  ```python
  del account.custom_data['rank']
  del group.custom_data['affiliation']
  ```

* Saving [CustomData](http://docs.stormpath.com/rest/product-guide/#custom-data)
  changes (creates, updates and deletes) to Stormpath only take place when `save()`
  is explicitly called.

  ```python
  account.custom_data.save()
  group.custom_data.save()
  ```

  OR

  ```python
  account.save()
  group.save()
  ```


## Testing

The Stormpath Python SDK is well tested.  Don't take our word on it though, run
our test suite and see for yourself!

We currently test against Python 2.7, 3.2 and 3.3.


### Testing with tox

The simplest way is to run the test suite is to install
[tox](http://tox.readthedocs.org/en/latest/).  Tox automatically tests the code
on multiple versions of Python by creating virtualenvs.

To get started, installed `tox`:

```bash
$ pip install tox
```

There is a `tox.ini` file in the root folder of Stormpath SDK.  You can modify
it to suit your needs, then run:

```bash
$ tox
```

To run the test suite.

Running a single environment (Python 2.7)

```bash
$ tox  -e py27
```

Running a single test in that environment:

```bash
$ tox  -e py27 -- -k test_name_of_the_test
```


### Testing without tox

What is common in all tests is that our `setup.py` uses
[pytest](http://pytest.org/latest/) to run tests and the tests themselves use
`HTTPretty` with `unittest`.  Python `mock` is also (sometimes) used, but in
Python 3.3, `mock` became part of the `unittest` module so you don't have to
install it if you're using Python 3.3.  The tests make sure the correct module
is used.

To install those dependencies manually, there is a `testdep` command that
checks the Python version and installs required packages accordingly:

```bash
$ python setup.py testdep
```

To run tests:
```bash
$ python setup.py test
```


### Live Testing

All of the above methods use `mock` and `HTTPretty` and don't query Stormpath.
That makes them fast and self-reliant.  If you want to run tests that don't
patch any of the methods, you have to set the following environment variables
to working Stormpath credentials:

```bash
$ export STORMPATH_API_KEY_ID=YOUR_APIKEY_ID
$ export STORMPATH_API_KEY_SECRET=YOUR_APIKEY_SECRET
```

To run the live tests against the Stormpath service, you can then run:

```bash
$ python setup.py livetest
```

**WARNING**: Since the tests make live changes to Stormpath data, **DO NOT** run
these tests in a production environment!


## Contributing

You can make your own contributions by forking the `development` branch of this
repository, making your changes, and issuing pull requests on the `development`
branch.

We regularly maintain our GitHub repostiory, and are quick about reviewing pull
requests and accepting changes!


### Building and Installing the Development Package

To build and install the development branch yourself, you can do the following:

```bash
$ git clone git@github.com:stormpath/stormpath-sdk-python.git
$ cd stormpath-sdk-python
$ python setup.py develop # If you want to install the package for development.
```


## Documentation

To generate our [Sphinx](http://sphinx-doc.org/) documentation, you'll need to
first install `sphinx`:

```bash
$ pip install sphinx
```

Next, you'll want to run:

```bash
$ python setup.py docs
```

To build the HTML documentation.  You can then open your browser and navigate to
`docs/_build/html/index.html`, which should open the fully built HTML
documentation!


## Quick Class Diagram

```
+-------------+
| Application |
|             |
+-------------+
       + 1
       |
       |        +------------------------+
       |        |     AccountStore       |
       o- - - - |                        |
       |        +------------------------+
       |                     ^ 1..*
       |                     |
       |                     |
       |          +---------OR---------+
       |          |                    |
       |          |                    |
       v 0..*   1 +                    + 1
+---------------------+            +--------------+
|      Directory      | 1        1 |    Group     |1
|                     |<----------+|              |+----------+
|                     |            |              |           |
|                     | 1     0..* |              |0..*       |
|                     |+---------->|              |<-----+    |
|                     |            +--------------+      |    |         +-----------------+
|                     |                                  |    |         | GroupMembership |
|                     |                                  o- - o - - - - |                 |
|                     |            +--------------+      |    |         +-----------------+
|                     | 1     0..* |   Account    |1     |    |
|                     |+---------->|              |+-----+    |
|                     |            |              |           |
|                     | 1        1 |              |0..*       |
|                     |<----------+|              |<----------+
+---------------------+            +--------------+
```


## Copyright & Licensing

Copyright &copy; 2012, 2013, 2014 Stormpath, Inc. and contributors.

This project is licensed under the
[Apache 2.0 Open Source License](http://www.apache.org/licenses/LICENSE-2.0).

For additional information, please see the full
[Project Documentation](https://www.stormpath.com/docs/python/product-guide).
