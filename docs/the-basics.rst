The Basics
==========

The basic things most people want to do with Stormpath, is:

- Create user accounts.
- Check user credentials.
- Create user groups.
- Put users into groups.
- Store custom data for a user account.

Below, we'll cover all this -- as you'll soon see, it's incredibly easy.


Create a User
-------------

Alright, let's create a user!  No time to waste!  Feast your eyes upon this::

    vader = app.accounts.create({
        'email': 'vader@evilgenius.es',
        'password': 'j01nTHEd4rkSIDELUKE',
        'given_name': 'Darth',
        'surname': 'Vader',
    })

The above code snippet will create a new Stormpath Account, inside of our
Application (which we created in the previous section).

.. note::
    When creating users with Stormpath, there are 4 required fields:

    - email
    - password
    - given_name (first name)
    - surname (last name)

You can also allow your users to specify a username (if that's your thing)::

    the_professor = app.accounts.create({
        'username': 'theprofessor',
        'email': 'professor@chaos.co',
        'password': 'MUAHAUahahah2342352!!!@%',
        'given_name': 'Butters',
        'surname': 'Stotch',
    })

.. note::
    If you don't specify a username when creating a user, Stormpath will
    auto-populate the username field with your user's email address.


Check User Credentials
----------------------

Let's say you want to see whether or not a user exists by checking credentials.
Stormpath makes this incredibly simple::

    professor = app.accounts.authenticate_account(
        'theprofessor',
        'MUAHAUahahah2342352!!!@%',
    ).account

The ``authenticate_account`` method returns a valid user object (if the
credentials supplied are valid) -- otherwise it raises an exception.

Try the following, and see for yourself::

    from stormpath.error import Error as StormpathError


    try:
        professor = app.accounts.authenticate_account(
            'theprofessor',
            'MUAHAUahahah2342352!!!@%',
        ).account
    except StormpathError, err:
        print 'Human friendly error message:', err.message
        print 'Developer friendly error message:', err.developer_message


Create User Groups
------------------

So, we've got a couple of users created.  Let's create groups to organize them::

    # NOTE: The description field is optional.
    admins = app.groups.create({
        'name': 'admins',
        'description': 'The highest level super villains.',
    })

    minions = app.groups.create({
        'name': 'minions',
        'description': 'Otherwise known as the expendables.',
    })

Wow, that was easy!  We've now got two groups.


Put Users Into Groups
---------------------

Ok, so let's move our ``vader`` user into the ``admins`` group, and our
``professor`` user into the ``minions`` group (sorry Butters!)::

    admins.add_account(vader)
    minions.add_account(professor)

Now we've got our two users assigned to their own groups.  We can verify this by
iterating over each user's groups::

    >>> for group in vader.groups:
    ...     print group.name, group.description
    ...
    admins The highest level super villains.
    >>> for group in professor.groups:
    ...     print group.name, group.description
    ...
    minions Otherwise known as the expendables.


Store Custom Data for User Accounts
-----------------------------------

Ok, so you get the idea by now: making users is really easy with Stormpath.  *But
what about the HARD stuff?  How can I store data with my users?*

I'm glad you asked!

Let's take a closer look::

    professor.custom_data['birthday'] = '06/28/1988'
    professor.custom_data['favorite_places'] = [
        {
            'city': 'Southpark',
            'state': 'Colorado',
        },
        {
            'city': 'Los Angeles',
            'state': 'California',
        },
    ]
    professor.save()

    >>> from json import dumps
    >>> print dumps(dict(professor.custom_data), indent=2, sort_keys=True)
    {
      "birthday": "06/28/1988",
      "favorite_places": [
        {
          "city": "Southpark",
          "state": "Colorado"
        },
        {
          "city": "Los Angeles",
          "state": "California"
        }
      ]
    }

Not bad, right?

By accessing a user's ``custom_data`` attribute, you can store any sort of
key-value data you want (up to 10MB per user account).  Regardless of the type
of data (nested JSON, arrays, etc.), Stormpath will efficiently store, protect,
and hold onto this data.

Stormpath's custom data is a great way to securely (and quickly) store important
user information (including billing tokens, etc.) -- allowing you to scale your
application to support millions of users, without the need to grow your users
database or change a single line of code!
