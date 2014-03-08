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
        'MUAHAUahahah2342352!!!@%'.account,
    )

The ``authenticate_account`` method returns a valid user object (if the
credentials supplied are valid) -- otherwise it raises an exception.

Try the following, and see for yourself::

    from stormpath.error import Error as StormpathError


    try:
        professor = app.accounts.authenticate_account(
            'theprofessor',
            'MUAHAUahahah2342352!!!@%'.account,
        )
    except StormpathError, err:
        print 'Human friendly error message:', err.message
        print 'Developer friendly error message:', err.developer_message
