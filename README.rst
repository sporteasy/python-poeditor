Python POEditor
===============

Overview
--------

API Client Interface for `POEditor API <https://poeditor.com/docs/api/>`_.

`POEditor <https://poeditor.com/>`_ is a quick and sleek web-based software
localization platform, designed for happy translators and project managers.

Support Python 2 and Python 3.

Installation
------------

To install the current version, run::

  $ pip install poeditor

You can also install the development version with::

  $ pip install -e git://github.com/sporteasy/python-poeditor.git#egg=poeditor-dev


Usage
-----

  >>> from poeditor import POEditorAPI
  >>> client = POEditorAPI(api_token='my_token')
  >>> projects = client.list_projects()
  >>> # create a new project
  >>> client.create_project("name", "description")
  >>> # get project details
  >>> project = client.view_project_details("project id")
  >>> # list project languages
  >>> languages = client.list_project_languages("project id")

Testing
-------

To run tests, you need a POEditor account. You can create a free trial account.

All requests to the API must contain the parameter api_token. You can get this
key from your POEditor account. You'll find it in `My Account > API Access <https://poeditor.com/account/api>`_::

  $ export POEDITOR_TOKEN=my_token
  $ nosetests

License
-------

MIT License (MIT)
