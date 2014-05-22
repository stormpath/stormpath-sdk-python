Version 1.2.4
-------------

Relased on May 22, 2014.

- Adding support for custom user agents: `Client` now has `user_agent` param.


Version 1.2.3
-------------

Released on May 14, 2014.

- Fixing another bug with nested customData fields being automatically
  camelCased.


Version 1.2.2
-------------

Released on May 14, 2014.

- Fixing bug with customData fields being automatically camelCased.


Version 1.2.1
-------------

Released on May 13, 2014.

- Fixing minor bug with `sp_http_status` code being written to customData.


Version 1.2.0
-------------

Released on May 2, 2014.

- Adding debugging abilities to HttpExecutor (to make finding issues simpler).
- Adding support for social identity providers (Facebook, Google).
- Fixing custom data deletion issue.  Previously custom data wasn't deleted on
  the server-side when a `del user.custom_data['field']` command was excecuted
  and saved.


Version 1.1.0
-------------

Released on March 27, 2014.

- Adding docs.
- Adding customizable authentication methods to the Client.
- Deprecating the `signer` property in favor of `scheme`.
- Adding `Account.in_group()` helper method, to make asserting group membership
  simpler.
- Adding `Account.in_groups()` helper method, to make asserting multiple group
  memberships simpler.
- Adding the ability for `Account.add_group()` to support Group objects, hrefs,
  or names.
- Adding the ability for `Account.has_group()` to support Group objects, hrefs,
  or names.
- Adding the ability for `Account.has_groups()` to support Group objects, hrefs,
  or names.
- Adding the ability for `Group.add_account()` to support Account objects, hrefs,
  usernames or emails.
- Adding new method, `Account.remove_group(group_object_or_href_or_name)`. This
  lets users easily remove Groups from an Account.
- Adding new method,
  `Group.remove_account(account_object_or_href_or_username_or_email)`. This lets
  users easily remove Accounts from a Group.
- Adding new method,
  `Group.has_account(account_object_or_href_or_username_or_email)`. This lets
  users easily check to see whether an Account is in a Group.
- Adding new method,
  `Group.has_accounts(account_objects_or_hrefs_or_usernames_or_emails)`. This lets
  users easily check to see whether a list of Accounts are part of a Group or
  not.


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
