How to run the test suite
=========================

To run the test suite, you need to install some additional dependencies and
set up a database.

The dependencies can be installed by running the following command:

    pip install -r tests/requirements.txt

Although djeneralize is RDBMS-agnostic, the test suite depends on PostgreSQL
because Django 1.6 introduced transaction-related changes that won't
work with the fixture library and SQLite.

Running the test suite is no different to running the test suite for a Django
project: The database and the tables must exist by the time the test suite is
run.

You have to create a database named "djeneralize-tests" and make sure it can
be accessed without credentials (e.g., using the "ident" authentication method).
Then, the tables can be created with::

    cd tests/test_djeneralize/
    python manage.py syncdb --noinput

From there on, you can run the tests the usual way; e.g.:

    nosetests
