python-poeditor
===============


Overview
--------

API Client Interface for [POEditor API](https://poeditor.com/api_reference/).



Testing
-------

To run tests, you need a POEditor account. You can create a free trial account.

All requests to the API must contain the parameter api_token. You can get this
key from your POEditor account. You'll find it in
[My Account > API Access.](https://poeditor.com/account/api)

    $ export POEDITOR_TOKEN=my_token
    $ nosetests

**Note**: there is no API method to delete a project. So, you must delete test
project by hand.
