# Stormpath Python SDK

Stormpath is the first easy, secure user management and authentication service for developers.
This is the Python SDK to ease integration of its features with any Python language based
application.

## Install

```sh
$ pip install stormpath-sdk
```

## Quickstart Guide

1.  If you have not already done so, register as a developer on
    [Stormpath][stormpath] and set up your API credentials and resources:

    1.  Create a [Stormpath][stormpath] developer account and [create your API Keys][create-api-keys]
        downloading the <code>apiKey.properties</code> file into a <code>.stormpath</code>
        folder under your local home directory.

    1.  Create an application and a directory to store your users'
        accounts. Make sure the directory is assigned as a login source
        to the application.

    1.  Take note of the _REST URL_ of the application and of directory
        you just created.

1.  **Create a client** using the API key properties file

    ```python
    from stormpath import Client

    client = Client(api_key_file_location="/some/path/to/apiKey.properties")
    ```

1.  **List all your applications and directories**

    ```python
    for application in client.applications:
        print("Application: ", application.name)

    for directory in client.directories:
        print("Directory:", directory.name)
    ```

1.  **Get access to the specific application and directory** using the
    URLs you acquired above.

    ```python
    application = client.applications.get(application_url)

    directory = client.directories.get(directory_url)
    ```

1.  **Create an account for a user** on the directory.

    ```python
    account = directory.accounts.create(
            given_name='John',
            surname='Smith',
            email='john.smith@example.com',
            username='johnsmith',
            password='4P@$$w0rd!'
            )
    ```

1.  **Update an account**

    ```python
    account.given_name = 'Johnathan'
    account.middle_name = 'A.'
    account.save()
    ```

1.  **Authenticate the Account** for use with an application:

    ```python
    try:
        account = application.authenticate_account('johnsmith', '4P@$$w0rd!')
    except stormpath.Error as e:
        print("Credentials are invalid or account doesn't exist")
    ```

1.  **Send a password reset request**

    ```python
    application.send_password_reset_email('john.smith@example.com')
    ```

1.  **Create a group** in a directory

    ```python
    directory.groups.create(name='Admins')
    ```

1.  **Add the account to the group**

    ```python
    group.add_account(account)
    ```

1. **Check for account inclusion in group** by reloading the account

    ```python
    account = clients.accounts.get(account.href)
    is_admin = any('Admin' == group.name for group in account.groups)
    ```

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
  key id and secret. For example, suppose your properties was:

  ```
  foo=APIKEYID
  bar=APIKEYSECRET
  ```

  You could load it with the following:

  ```python
  client = stormpath.Client(
      api_key_file_location='/some/path/to/apiKey.properties',
      api_key_id_property_name='foo',
      api_key_secret_property_name='bar')
  ```

* Passing in a stormpath.APIKey instance:

  ```python
  client = stormpath.Client(id=api_id, secret=api_secret)
  ```

* By explicitly setting the API key id and secret:

  ```python
  client = stormpath.Client(api_key={
      'id': api_id,
      'secret': api_secret
  })
  ```

* By passing the REST URL of a Stormpath application on your account
  with the API id and secret embedded. For example, the URL would look
  like:

  ```
  http://#{api_key_id}:#{api_key_secret}@api.stormpath.com/v1/applications/#{application_id}
  ```

  The client could then be created with the above URL:

  ```python
  client = stormpath.Client(application_url=application_url)
  ```

  This method will also provide a <code>application</code> property on
  on the client to directly access that resource.

### Accessing Resources

Most of the work you do with Stormpath is done through the applications
and directories you have registered. You use the client to access them
with their REST URL:

```python
application = client.applications.get(application_url)

directory = client.directories.get(directory_url)
```

The <code>applications</code> and <code>directories</code> property on a
client instance also you to iterate
and scan for resources via that interface.

Additional resources are <code>accounts</code>, <code>groups</code>,
<code>group_membership</code>, and the single reference to your
<code>tenant</code>.

### Registering Accounts

Accounts are created on a directory instance. They can be created in two
ways:

* With the <code>create_account</code> method:

  ```python
  account = directory.create_account({
    given_name: 'John',
    surname: 'Smith',
    email: 'john.smith@example.com',
    username: 'johnsmith',
    password: '4P@$$w0rd!'
  })
  ```

  This metod can take an additional flag to indicate if the account
  can skip any registration workflow configured on the directory.

  ```python
  ## Will skip workflow, if any
  account = directory.create_account(account_props, False)
  ```

* Creating it directly on the <code>accounts</code> collection property
  on the directory:

  ```python
  account = directory.accounts.create({
    given_name: 'John',
    surname: 'Smith',
    email: 'john.smith@example.com',
    username: 'johnsmith',
    password: '4P@$$w0rd!'
  })
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
group:

```python
    any('administrators' == group.name for group in account.groups)
```

You can create groups and assign them to accounts using the Stormpath
web console, or programmatically. Groups are created on directories:

```python
group = directory.groups.create(name='administrators')
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
  group.add_group(account)
  ```

You will need to reload the account or group resource after these
operations to ensure they've picked up the changes.

## Testing

### Setup

The functional tests of the SDK run against a Stormpath tenant. In that
account, create:

* An application reserved for testing.
* A directory reserved for test accounts. _Be sure to associate this
  directory to the test application as a login source_.
* Another directory reserved for test accounts with the account
  verification workflow turned on. _Be sure to associate this directory
  to the test application as a login source_.

The following environment variables need will then need to be set:

* <code>STORMPATH_SDK_TEST_API_KEY_ID</code> - The <code>id</code> from
  your Stormpath API key.
* <code>STORMPATH_SDK_TEST_API_KEY_SECRET</code> - The
  <code>secret</code> from your Stormpath API key.
* <code>STORMPATH_SDK_TEST_APPLICATION_URL</code> - The URL to the
  application created above.
* <code>STORMPATH_SDK_TEST_DIRECTORY_URL</code> - The URL to the first
  directory created above.
* <code>STORMPATH_SDK_TEST_DIRECTORY_WITH_VERIFICATION_URL</code> - The
  URL to the second directory created above.

### Running

Once properly configured, you can run tests:

```sh
$ python setup.py test
```

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

## Quick Class Diagram

```
+-------------+
| Application |
|             |
+-------------+
       + 1
       |
       |           +-------------+
       |           | LoginSource |
       o- - - - - -|             |
       |           +-------------+
       |
       v 0..*
+--------------+            +--------------+
|  Directory   | 1        1 |   Account    |1
|              |<----------+|              |+----------+
|              |            |              |           |
|              | 1     0..* |              |0..*       |
|              |+---------->|              |+-----+    |
|              |            +--------------+      |    |         +-----------------+
|              |                                  |    |         | GroupMembership |
|              |                                  o- - o - - - - |                 |
|              |            +--------------+      |    |         +-----------------+
|              | 1     0..* |    Group     |1     |    |
|              |+---------->|              |<-----+    |
|              |            |              |           |
|              | 1        1 |              |0..*       |
|              |<----------+|              |<----------+
+--------------+            +--------------+
```

## Copyright & Licensing

Copyright &copy; 2012 Stormpath, Inc. and contributors.

This project is licensed under the [Apache 2.0 Open Source License](http://www.apache.org/licenses/LICENSE-2.0).

For additional information, please see the full [Project Documentation](https://www.stormpath.com/docs/python/product-guide).

  [stormpath]: http://stormpath.com/
  [create-api-keys]: http://www.stormpath.com/docs/python/product-guide#AssignAPIkeys
