Version 2.5.0
-------------

**Not yet released.**

- Fixing broken tests.
- Adding support for `Account.password_modified_at` property.
- Adding support for `Error.request_id` property.
- Simplifying Travis build scripts for speed.
- Re-arranging private SSH key files for builds.
- Cleaning up Facebook Graph API test accounts after each test run to prevent
  errors.
- Adding support for `PasswordStrength.prevent_reuse` setting which allows
  developers to control password reuse settings for their Directories.
- Adding support for `AccountSchema` and `Field` resources.
- Adding tests for new `AccountSchema` and `Field` resources.
- Supporting MFA, and all new MFA resources.
- Adding tests for all new MFA functionality.
- Supporting `use_subdomain` option for IDSite redirect logic.
- Supporting `ApiKey.name` and `ApiKey.description` resources fields.
- Fixing broken MFA tests after accidentally messing them up.
- Updating tox testing tool stuff. It now works in more environments, and more
  better-er =)
- Fixing security issue / performance issue regarding local JWT validation. We
  now do this properly in a faster, more efficient manner.
- Supporting manual account linking. This now includes the new resources and
  tests.


Version 2.4.5
-------------

**Released September 21, 2016.**

- Using our new Sphinx docs.


Version 2.4.4
-------------

**Released August 4, 2016.**

- Attempting to fix Travis Deployments with Sphinx install changes.


Version 2.4.3
-------------

**Released August 4, 2016.**

- Attempting to automate API doc deployment through Travis CI.


Version 2.4.2
-------------

**Released July 18, 2016.**

- Removing legacy logging logic from ``stormpath.http`` package.  This was
  causing errors in certain circumstances where UTF-8 was not being supplied
  over the network.


Version 2.4.1
-------------

**Relased June 28, 2016.**

- Fixing bug in API authentication that would result in multiple invalid HTTP
  calls being generated when attempting to do token based authentication.
- Cleaning up token management code.
- Adding tests for asserting that account stores are properly set for token
  multi-tenancy.


Version 2.4.0
-------------

**Released June 14, 2016.**

- Fixing `Client.api_keys` generator, it now works properly.
- Adding support for `Client.id_sites`.
- Fixing broken `Client.agents` functionality.
- Allowing users to create `GroupMemberships` from the `Client`.
- Replacing old string manipulation on URLs with proper URL parsing library
  calls.
- Adding `to_json()` method for all Stormpath resources.
- Adding cache support for Organization resources.
- Adding more integration tests.
- Fixing broken Python 3 tests. Fully 3k compatible =)
- Properly handling retry requests.
- Fixing tests so they no longer leave Stormpath resources around after a run.
- Pinning oauthlib version to avoid issues with `__repr__`.


Version 2.3.1
-------------

**Released April 11, 2016.**

- Supporting new attributes for `Application.build_id_site_redirect_url()`.
  Thanks to [@lwcolton](https://github.com/lwcolton) for the pull request!


Version 2.3.0
-------------

**Released April 11, 2016.**

- Removing some unused code.
- Supporting IDSite in it's entirety: modifying IDSites, etc.
- Updating test runners to be a bit more pythonic.
- Adding tests for custom data attributes, and more advanced live testing.
- Adding better docs for PyPI.
- Adding code coverage logging / support.


Version 2.2.0
-------------

**Released March 16, 2016.**

- Adding more SAML features: ``DefaultRelayState``, and adding ``account_store``
  and ``organization`` support to SAML IDP redirect URL helper.
- Fixing issue iterating through API Keys.
- Adding test to assert API Key iteration.
- Pruning some unnecessary files.


Version 2.1.9
-------------

**Released February 22, 2016.**

- Fixing typos in this very changelog.
- Making new release without conflicted copies of local files (thanks
  @dropbox...).


Version 2.1.8
-------------

**Released February 18, 2016.**

- Adding support for SAML. Yey!
- Supporting a new `NullCache` which completely disables all caching for the
  SDK.
- Fixing cache region bug that would break cache when the configuration was
  used.


Version 2.1.7
-------------

**Released February 12, 2016.**

- Fixing bugs in Error handling class.  We now have standardized Error objects
  that properly reflect our error messages.
- Fixing caching for API keys.
- Updating code samples in the README to support Python 3 syntax.
- Adding support for Python 3.5.
- Fixing broken readme badges.


Version 2.1.6
-------------

**Released on November 17, 2015.**

- Adding leeway for ID site tokens.  This makes it possible for us to correctly
  account for clock skew when validating tokens.


Version 2.1.5
-------------

**Released on November 12, 2015.**

- Making it easier to use Organization Mappings.
- Fixing support for Error Callbacks with ID Site.


Version 2.1.4
-------------

**Released on November 6, 2015.**

- Adding support for suppressing registration emails on account creation.
  Example:

```python
# Suppress registration emails even if workflow settings are enabled.
application.accounts.create(data, registration_workflow_enabled=False)
```


Version 2.1.3
-------------

**Released on November 2, 2015.**

- Fixing bug with password grant authentication not working.
- Supporting the iteration of Groups from the Client object.
- Updating Sphinx API docs to be more intuitive for developers.


Version 2.1.2
-------------

**Released on October 28, 2015.**

- Adding tests to improve coverage.
- Adding Password Grant Type support.
- Adding in better error handling for Password Strength rules.
- Adding support for new Organization resources.
- Adding support for Organization name keys when performing a LoginAttempt.
- Adding in better documentation for API auth.
- Adding an IDSiteTokenAuthenticator.


Version 2.1.1
-------------

**Released on August 31, 2015.**

- Version bump for vanity.


Version 2.1.0
-------------

**Relased on August 31, 2015.**

- Adding new `OauthPolicy` class.  This allows users to modify their
  Application's OAuth Policies, setting new Access Token and Refresh Token TTLs.


Version 2.0.9
-------------

**Released on August 19, 2015.**

- Adding new API authentication classes / logic!  These make API authentication
  WAYYYYY easier: both for Basic Auth and OAuth2 requests!
- Supporting fetching of resources by partial HREF. So you can say like
  `client.get_application('/v1/applications/xxx')` as opposed to including the
  ENTIRE href.  This makes moving to the Stormpath enterprise cloud a bit
  simpler.
- Making it possible to create new accounts with EXISTING password hashes!
  Finally!  If you're migrating users into Stormpath, we can now utilize your
  existing password hashes to make migrations 100% painless.
- Various packaging fixes, thanks a ton [Alex](https://github.com/alunduil)!
  Much love!
- Allowing custom data to be used as a dictionary.  This makes storing /
  retrieving custom data a bit easier.


Version 2.0.8
-------------

**Released on July 6, 2015.**

This is our (belated) Independence Day release!  Thanks to Will Smith for saving
the earth and therefore making this release possible!

- Adding account creation policy support.
- Renaming ResetEmailTemplate -> DefaultModelEmailTemplate
- Making our API Key resource dict() compatible.


Version 2.0.7
-------------

**Released on June 18, 2015.**

- Removing Python 3.2 support.
- Adding in support for signals / binding.  This allows us to do really cool
  event-driven development.
- Adding in better social login integration tests.
- Adding new Travis CI environment variables.
- Fixing some broken tests.
- Adding sleep statements after tests to ensure eventually consistent tests
  pass.
- Adding in better tests for ID site functionality.


Version 2.0.6
-------------

**Released on May 12, 2015.**

- Fixing issue with `limit` being modified during pagination.
- Adding support for resource signals!  This means you can now 'listen' for
  resource creation, updates, and deletes.
- Adding checks to ensure that when an ID site login happens, the account is
  part of a Stormpath Application.


Version 2.0.5
-------------

**Released on April 16, 2015.**

- Updating the pyjwt dependency to fix JWT security issues.
- Adding support for Mirror Directories and Agents (*this lets users manage
  Active Directory and LDAP systems*).


Version 2.0.4
-------------

**Released on April 12, 2015.**

- Adding in hotfix for the Stormpath Error class.  It now supports string only
  arguments, which makes the library more flexible for handling weird edge
  cases.


Version 2.0.3
-------------

**Released on April 1, 2015.**

- Improving API authentication API.  It now allows for API authentication
  WITHOUT OAuth2 scopes, as well as an empty body.  This makes the parameters
  much simpler for users, and makes more sense.


Version 2.0.2
-------------

**Released on March 12, 2015.**

- Simplifying the API authentication method signatures. It's now MUCH simpler to
  perform API authentication as almost all parameters are optional =)
- Adding in support for generating JWTs after an account has been authenticated.
  This opens the door for smarter sessions, as well as sophisticated API
  authentication and OAuth2 flows.
- Adding `created_at` and `modified_at` properties to all resources.  This
  allows developers to get more information for their usage purposes.


Version 2.0.1
-------------

**Released on March 9, 2015.**

- Fixing Google App Engine specific bug: GAE won't let users import `win32_ver`
  as their sandbox mode breaks it :(  This is a dirty hack to make things work
  for our super awesome, wonderful, and incredibly brilliant GAE users.  <333
  ya'll!


Version 2.0.0
-------------

**Released on March 2, 2015.**

- Major release!
- Changing the way timestamp fields are represented -- they're now represented
  as `datetime` objects exclusively (no more strings). This makes developing
  applications much simpler, and less error prone!


Version 1.3.6
-------------

**Released on February 27, 2015.**

- Adding in support for Stormpath's new "Password Policies" for Directories. The
  way it works is pretty simple: there's a new `password_policy` attribute on
  Directory objects which let's you configure your password strength
  requirements on a directory, as well as enabling / disabling / customizing
  email templates.
- Adding in various Python 3 fixes.


Version 1.3.5
-------------

**Released on February 11, 2015.**

- Fixing bug with Memcached cache serialization for tuples.
  `json_deserializer()` was accidentally returning a tuple instead of a JSON
  value.
- Improving test coverage.
- Fixing odd case where custom data keys were not deleted properly.  This is now
  resolved, so custom data deletion always behaves as expected.


Version 1.3.4
-------------

**Released on February 5, 2015.**

- Fixing bug with collection resources.  We had improper size issues before,
  which is now fixed.
- Using our new Sphinx theme for docs.


Version 1.3.3
-------------

**Released on February 2, 2015.**

- Adding size property to all collection resources -- this makes pagination
  simpler / faster, and improves the iteration speed over large collections of
  items.


Version 1.3.2
-------------

**Released on January 28, 2015.**

- Adding custom data caching / tests.  This substantially speeds up webapps that
  heavily rely on custom data, yey!


Version 1.3.1
-------------

**Released on January 26, 2015.**

- Adding an exponential backoff strategy.  This greatly improves library
  stability by automatically handling API service errors if they occur (network
  errors, actual Stormpath errors, etc.).
- Fixing JWT library upgrade errors.
- Fixing our Sauthc1 custom digest authentication implementation -- we now
  properly order our query strings, solving several issues.
- Fixing recursion errors due to weird redirect logic.
- Adding `Account.applications` helper to directly iterate over the Applications
  an Account is a member of.
- Error'ing out loudly on JSON decoding errors (*as we should*).


Version 1.3.0
-------------

**Released on December 29, 2014.**

- Deprecating `Client(id, secret)` in favor of `Client(api_key_id,
  api_key_secret)`.
- Deprecating `Client(api_key_file_location)` in favor of
  `Client(api_key_file)`.
- Exposing `Client._api_key_id` and `Client._api_key_secret`.
- Making the client automatically load API key file information from
  `STORMPATH_API_KEY_FILE` environment variable if present.
- Making the client automatically load API key information from
  `STORMPATH_API_KEY_ID` and `STORMPATH_API_KEY_SECRET` environment variables if
  present.
- Making the client automatically load ~/.stormpath/apiKey.properties if no
  other settings are present.
- Updating README to take advantage of the new setup stuff.


Version 1.2.9
-------------

**Released on December 26, 2014.**

- Adding better error handling for server-side requests.
- Improving provider naming (*github social login*).
- Updating docstrings for clarity.


Version 1.2.8
-------------

**Released on December 24, 2014.**

- Adding in the ability to specify an account store when doing a password reset
  -- this allows you to specify what user (in what directory / group / etc) to
  reset.
- Adding in the ability to specify search queries when specifying accounts /
  groups.
- Adding in convenience methods for accounts / groups (every one imaginable) =)


Version 1.2.7
-------------

**Released on December 8, 2014.**

- Added the ability to resend verification email tokens.
- Added support for memcached as a cache backend.
- Adding minor cleanup to Redis backend docs.


Version 1.2.6
-------------

Released on October 29, 2014.

- Upgrading requests dependency to latest release.
- Adding support for social login via Github and LinkedIn.
- Adding support for API authentication with Basic Auth / Oauth2.
- Refactoring test suite.
- Adding Python 3.4 compatibility.
- Adding badges for PyPI =)
- Adding ID site support.
- Adding support for passing additional options to the Redis cache backend.
- Fixing searching encoding issues.
- Fixing pagination issues.
- Tweaking user agent for Stormpath compliance.
- Implementing a limit on the maximum allowed amount of cached objects.
- Fixing a small bug with data expansion.


Version 1.2.5
-------------

Released on May 28, 2014.

- Fixing bugs with the Redis cache implementation.  Key expiration now works as
  expected, along with optional arguments to the Redis backend.
- Adding python 3.4 support.
- Adding the ability to treat all resources as dictionaries -- you can set
  fields and update fields in a dict-like manner.
- Adding the ability to perform updates which instantly propagate changes to the
  server.


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
