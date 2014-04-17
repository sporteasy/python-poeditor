"""
    API Client Interface for POEditor API (https://poeditor.com).

    Usage:

    >>> from poeditor import POEditorAPI
    >>> client = POEditorAPI(api_token='my_token')
    >>> projects = client.list_projects()
"""

__version__ = "1.0.3"

try:
    from client import POEditorAPI, POEditorException, POEditorArgsException
except ImportError:
    pass
