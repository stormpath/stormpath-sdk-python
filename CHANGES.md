Version 1.1.0
-------------

Released on March 10, 2014.

- Adding docs.
- Adding customizable authentication methods to the Client.
- Deprecating the `signer` property in favor of `scheme`.
- Adding `Account.in_group()` helper method, to make asserting group membership
  simpler.
- Adding `Account.in_groups()` helper method, to make asserting multiple group
  memberships simpler.
- Adding the ability for `Account.add_group()` to support Group objects, hrefs,
  or names.
- Adding the ability for `Account.in_group()` to support Group objects, hrefs,
  or names.
- Adding the ability for `Account.in_groups()` to support Group objects, hrefs,
  or names.
- Adding the ability for `Group.add_account()` to support Account objects, hrefs,
  usernames or emails.
- Adding new method, `Account.remove_group(group_object_or_href_or_name)`. This
  lets users easily remove Groups from an Account.
- Adding new method,
  `Group.remove_account(account_object_or_href_or_username_or_email)`. This lets
  users easily remove Accounts from a Group.


Version 1.0.1
-------------

Released on February 12, 2014.

- Upgrading all documentation in the README.md.
- Rewriting large portion of docs for clarity.


Version 1.0.0
-------------

Released on February 11th, 2014.

- Library no longer in BETA!
- PEP-8 fixes.
- Error object now has a `user_message` attribute, which contains the
  user-friendly error message from the API service.
- Error object's `message` attribute now contains the developer friendly
  message.
- Adding HTTP proxy support to Clients.
- Renaming PyPI package from stormpath-sdk -> stormpath.
- Updating copyright notices.
- Updating PyPI contact information.
- `authenticate_account` no longer returns an account object directly.
- Added support for accountStore specification when authenticating an account.
- Added custom data fields for groups and accounts.
- Added support for login attempt expansion.


Version 1.0.0.beta
------------------

Released on September 26, 2013

- Complete rewrite of codebase
- Support for Python 2.7
- Added self-contained tests
- Account store resources added
- Implemented caching
- Added ability to autocreate directory
- Added entity expansion to create method and tenant resource


Version 0.2.1
-------------

Released on June 27, 2013

- Fixed current tenant redirection handling by adding general redirection support of the Stormpath REST API.


Version 0.2.0
-------------

Released on March 22, 2013

- Implementing Stormpath Digest Authentication (SAuthc1).
- Fixing implementation when no 'base_url' is specified when creating a DataStore.


Version 0.1.1
-------------

Released on March 14, 2013

- Making the 'base_url' an optional argument in the Client class constructor.


Version 0.1.0
-------------

Released on March 14, 2013

- First release of the Stormpath Python SDK where all of the features available on the REST API, before the ones released on February 19th 2013, were implemented.
