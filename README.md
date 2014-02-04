# Stormpath Python SDK

[![Build Status](https://travis-ci.org/stormpath/stormpath-sdk-python.png?branch=master)](https://travis-ci.org/stormpath/stormpath-sdk-python)

Stormpath is the first easy, secure user management and authentication service for developers.
This is the Python SDK to ease integration of its features with any Python language based
application.

## Install

```sh
$ pip install stormpath-sdk --pre
```

## Quickstart Guide

1.  If you have not already done so, register as a developer on
    [Stormpath][stormpath] and set up your API credentials and resources:

    1.  Create a [Stormpath][stormpath] developer account and [create your API Keys][create-api-keys]
        downloading the <code>apiKey.properties</code> file into a <code>.stormpath</code>
        folder under your local home directory.

2.  **Create a client** using the API key properties file

    ```python
    from stormpath import Client

    client = Client(api_key_file_location="/some/path/to/apiKey.properties")
    ```

3.  **List all your applications and directories**

    ```python
    for application in client.applications:
        print("Application: ", application.name)

    for directory in client.directories:
        print("Directory:", directory.name)
    ```

4.  **Get access to the specific application and directory** using the
    URLs you acquired above.

    ```python
    application = client.applications.get("https://api.stormpath.com/v1/applications/APP_UID")

    directory = client.directories.get("https://api.stormpath.com/v1/directories/DIR_UID")
    ```

5.  **Create an application** and autocreate a directory as the login source.

    ```python
    account = client.applications.create({
            'name':'Holodeck',
            'description': "Recreational facility",
            }, create_directory=True)
    ```

6.  **Create an account for a user** on the directory.

    ```python
    account = application.accounts.create({
            'given_name':'John',
            'surname':'Smith',
            'email':'john.smith@example.com',
            'username':'johnsmith',
            'password':'4P@$$w0rd!'
            })
    ```

7.  **Update an account**

    ```python
    account.given_name = 'Johnathan'
    account.middle_name = 'A.'
    account.save()
    ```

8.  **Authenticate the Account** for use with an application:

    ```python
    try:
        account = application.authenticate_account('johnsmith', '4P@$$w0rd!')
    except stormpath.Error as e:
        print(e)
    ```

9.  **Send a password reset request**

    ```python
    application.send_password_reset_email('john.smith@example.com')
    ```

10.  **Create a group** in a directory

    ```python
    directory.groups.create({'name':'Admins'})
    ```

11.  **Add the account to the group**

    ```python
    group.add_account(account)
    ```

12. **Modify your custom data**

    ```python
    print(account.custom_data['birthDate'])
    account.custom_data['rank'] = 'Captain'
    account.custom_data.save()

## Common Uses

### Creating a client

All Stormpath features are accessed through a
<code>stormpath.Client</code> instance, or a resource
created from one. A client needs an API key (made up of an _id_ and a
_secret_) from your Stormpath developer account to manage resources
on that account. That API key can be specified any number of ways
in the hash of values passed on Client initialization:

* The location of API key properties file:

  ```python
  client = stormpath.Client(api_key_file_location='/some/path/to/apiKey.properties')
  ```

  You can even identify the names of the properties to use as the API
  key id and secret. For example, suppose your properties were:

  ```
  foo=APIKEYID
  bar=APIKEYSECRET
  ```

  You could load it with the following parameters:

  ```python
  client = stormpath.Client(
      api_key_file_location='/some/path/to/apiKey.properties',
      api_key_id_property_name='foo',
      api_key_secret_property_name='bar')
  ```

* By explicitly setting the API key id and secret:

  ```python
  client = stormpath.Client(id=api_id, secret=api_secret)
  ```

* Passing in an APIKey dictionary:

  ```python
  client = stormpath.Client(api_key={
      'id': api_id,
      'secret': api_secret
  })
  ```

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
registered on Stormpath. This will either return an <code>Account</code>
instance if the credentials are valid, or raise a <code>stormpath.Error</code>
otherwise. In the former case, you can get the <code>account</code>
associated with the credentials.

```python
try:
    account = application.authenticate_account('johnsmith', '4P@$$w0rd!')
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

* Saving custom data changes (creates, updates and ) to Stormpath:
When deleting custom fields, the information is not synced with Stormpath until the custom_data object is saved. Also, saving groups and accounts automatically saves their custom data.

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

Copyright &copy; 2012, 2013 Stormpath, Inc. and contributors.

This project is licensed under the [Apache 2.0 Open Source License](http://www.apache.org/licenses/LICENSE-2.0).

For additional information, please see the full [Project Documentation](https://www.stormpath.com/docs/python/product-guide).

  [stormpath]: http://stormpath.com/
  [create-api-keys]: http://www.stormpath.com/docs/python/product-guide#AssignAPIkeys
