# Stormpath Python SDK

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
[Stormpath][https://stormpath.com/], and create (and download) an API Key pair
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
    auth_attempt = applicatoin.authenticate_account('pg', 'STARTUPSar3th3b3sT!')
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

### Accessing Resources

Most of the work you do with Stormpath is done through the applications
and directories you have registered. You use the client to access them
with their REST URL:

```python
application = client.applications.get(application_url)

directory = client.directories.get(directory_url)
```

The <code>applications</code> and <code>directories</code> property on a
client instance allows you to iterate
and scan for resources via that interface.

Additional resources are <code>accounts</code>, <code>groups</code>,
<code>group_memberships</code>, <code>account_store_mappings</code>, and the single reference to your
<code>tenant</code>.

### Registering Accounts

Accounts are created on a directory instance:

  ```python
  account = directory.accounts.create({
    given_name: 'John',
    surname: 'Smith',
    email: 'john.smith@example.com',
    username: 'johnsmith',
    password: '4P@$$w0rd!'
  })
  ```

  Directory account creation can take an additional flag to indicate if the account
  can skip any registration workflow configured on the directory.

  ```python
  ## Will skip workflow, if any
   account = directory.accounts.create({
        'given_name': 'John',
        'surname': 'Smith',
        'email': 'frank@stormpath.com',
        'username': 'johnsmith',
        'password': 'Temp1234'
  }, registration_workflow_enabled=False)
  ```

If the directory has been configured with an email verification workflow
and a non-Stormpath URL, you have to pass the verification token sent to
the URL in a <code>sptoken</code> query parameter back to Stormpath to
complete the workflow. This is done through the
<code>verify_email_token</code> on the <code>accounts</code> collection.

### Authentication

Authentication is accomplished by passing a username or an email and a
password to <code>authenticate_account</code> of an application we've
registered on Stormpath. This will either return an <code>AuthenticationResult</code>
instance if the credentials are valid, or raise a <code>stormpath.Error</code>
otherwise. In the former case, you can get the <code>account</code>
associated with the credentials.

```python
try:
    account = application.authenticate_account('johnsmith', '4P@$$w0rd!').account
except stormpath.Error as e:
  #If credentials are invalid or account doesn't exist
  print(e)
```

### Password Reset

A password reset workflow, if configured on the directory the account is
registered on, can be kicked off with the
<code>send_password_reset_email</code> method on an application:

```python
application.send_password_reset_email('john.smith@example.com')
```

If the workflow has been configured to verify through a non-Stormpath
URL, you can verify the token sent in the query parameter
<code>sptoken</code> with the <code>verify_password_reset_token</code>
method on the application.

With the account acquired you can then update the password:

```python
  account.password = new_password
  account.save()
```

_NOTE :_ Confirming a new password is left up to the web application
code calling the Stormpath SDK. The SDK does not require confirmation.

### ACL through Groups

Memberships of accounts in certain groups can be used as an
authorization mechanism. As the <code>groups</code> collection property
on an account instance is <code>iterable</code>, you can use any of
that module's methods to determine if an account belongs to a specific
group.

You can create groups and assign them to accounts using the Stormpath
web console, or programmatically. Groups are created on directories:

```python
group = directory.groups.create({'name':'administrators'})
```

Group membership can be created by:

* Explicitly creating a group membership resource with your client:

  ```python
  group_memebership = client.group_memberships.create(group, account)
  ```

* Using the <code>add_group</code> method on the account instance:

  ```python
  account.add_group(group)
  ```

* Using the <code>add_account</code> method on the group instance:

  ```python
  group.add_account(account)
  ```
### Managing custom data

Groups and account have custom data fields that act as a dictionary:

* Accessing custom data field:
  ```python
  print(account.custom_data['birthDate'])
  print(group.custom_data['foundationDate'])
  ```

* Creating or updating a custom data field:
  ```python
  account.custom_data['rank'] = 'Captain'
  account.custom_data.save()
  group.custom_data['affiliation'] = 'NCC-1701'
  group.custom_data.save()
  ```

* Deleting a custom data field:
  ```python
  del account.custom_data['rank']
  del group.custom_data['affiliation']
  ```

* Saving custom data changes (creates, updates and deletes) to Stormpath:
When deleting custom fields, the information is not synced with Stormpath until the custom_data object is saved by calling the `save` method. Also, saving groups and accounts automatically saves their custom data.

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

### Setup

The tested versions are Python 2.7, 3.2 and 3.3.

#### Testing with tox
The simplest way is to install tox. Tox automatically tests the code on multiple versions of Python by creating virtualenvs:

```sh
$ pip install tox
```

There is a tox.ini file in the root folder of Stormpath SDK. You can modify it to suit your needs and run:

```sh
$ tox
```

#### Testing without tox

What is common in all tests is that our setup.py uses `pytest` to run tests and the tests themselves use `HTTPretty` with `unittest`. Python `mock` is also (sometimes) used but in Python 3.3 `mock` became part of the `unittest` module so you don't have to install it if you're using Python 3.3. The tests make sure the correct module is used.

To install those dependencies manually, there is a `testdep` command that checks the Python version and installs required packages accordingly:

```sh
$ python setup.py testdep
```

To run tests:
```sh
$ python setup.py test
```

#### Live testing

All of the above methods use `mock` and `HTTPretty` and don't query Stormpath. That makes them fast and self-reliant. If you want to run tests that don't patch any of the methods, you have to set the following environment variables to working Stormpath credentials:

```sh
$ export STORMPATH_SDK_TEST_API_KEY_ID=YOUR_APIKEY_ID
$ export STORMPATH_SDK_TEST_API_KEY_SECRET=YOUR_APIKEY_SECRET
```

To run tests
```sh
$ python setup.py livetest
```

WARNING: Since the tests make live changes to Stormpath data, DO NOT run these tests in a production environment!


## Contributing

You can make your own contributions by forking the <code>development</code>
branch, making your changes, and issuing pull-requests on the
<code>development</code> branch.

### Building and installing package

To build and install the development branch yourself from the latest source:

```
$ git clone git@github.com:stormpath/stormpath-sdk-python.git
$ cd stormpath-sdk-python
$ python setup.py install # if you want to install
$ python setup.py sdist # if you want to build a package
```

## Documentation
To generate docs from docstrings you need to install `sphinx`:

```sh
$ pip install sphinx
```

And then run:
```sh
$ python setup.py docs
```

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

This project is licensed under the [Apache 2.0 Open Source License](http://www.apache.org/licenses/LICENSE-2.0).

For additional information, please see the full [Project Documentation](https://www.stormpath.com/docs/python/product-guide).

  [stormpath]: http://stormpath.com/
  [create-api-keys]: http://www.stormpath.com/docs/python/product-guide#AssignAPIkeys
