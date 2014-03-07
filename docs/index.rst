Stormpath Python SDK
====================

*The official Stormpath SDK for Pythonistas!*

.. image:: assets/images/stormpath-logo.png
    :alt: Stormpath Logo

The Stormpath Python SDK allows any Python based application to easily use the
Stormpath user management service for all authentication and access control needs.

This documentation will walk you through everything you need to know to start
using Stormpath in your Python application!

If you'd like to view our more comprehensive Python guide (which walks through
every possible use case), you should probably check out the official
`Python SDK Product Guide <http://docs.stormpath.com/python/product-guide/>`_.

For reference, the official Stormpath website can be found here:
https://stormpath.com


What is Stormpath?
------------------

TODO: Rewrite this.

If you have no idea what Stormpath is -- don't worry!  Read the story below.

A long time ago, in a galaxy far, far away, there lived a programmer named John.
John was a happy developer, and built many websites for his clients.

One day, John got a request from a client to build user account support into
their application.  This client wanted to allow users on the website to create
accounts, verify these accounts via email, and securely manage these users
(login, logout, etc.).

After thinking about the issue for a while, John decided the best way to support
user accounts on the website was to create a new database table for the users
and their data.

John developed a new `users` table, then used his framework's built in
authentication library to log users in and out of the website.  *"This is not so
bad."*, John thought.

Then John started working on the email verification problem.  After a while,
John decided the best way to handle email verification was to modify his `users`
table and add two new columns: `verified` and `verification_token`.  John then
implemented a custom solution, and within a few days was able to ship the new
user system into production -- and the client was happy.  *"This was a bit more
work, but not so bad."*, John thought.

Several days later, the client told John that users were complaining about website
slowness.

When John looked into the issue, he realized that each user request was hitting the
`users` table to check the user's credentials, so John implemented a new `sessions`
table, and used his framework's libraries to support user sessions to lessen the load
on the database, and speed up user requests -- and the client was happy.  *"This
is becoming a bit of a pain."*, John thought.

As time passed, and the client continued to have more and more users sign up for
the website.  Before too long, the client asked John for help: users needed to
store various bits of application information.

John took a look at the system, and added a new table to his database, named
`user_data`.  John then added the data fields the client wanted, and deployed
his changes -- and the client was happy.  *"This is becoming a bit tricky to
maintain."*, John thought.

Over time, John received more and more requests from the client:

- Users needed to store more data fields.
- Requests for user data were becoming slow due to increased usage.

After spending many days customizing his user management software, John couldn't
help but think "Wow, this user management stuff is quite tricky."

After spending a lot of time customizing the client's user management software,
John found `Stormpath <https://stormpath.com>`_, and was happy.

John used Stormpath's simple Python SDK to easily (*and securely!*) create and
manage users and user data.  Stormpath allowed John to:

- Automatically verify new users via email.
- Keep user account data safely secured away from prying eyes.
- Keep users backed up and synced to prevent the possibility of data loss.
- Easily store *any* user data in Stormpath, without the need for separate
  databases and storage systems.
- Easily handle his client's growth without any hiccups: as the client's user
  base continued to grow, Stormpath gracefully handled all scaling issues.

John was happy that he no longer had to worry about his authentication problems,
and the client was happy that their website was now faster, more secure, and
*more affordable* (since they required less of John's time to maintain their
site).


.. toctree::
   :maxdepth: 3

   stormpath


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
