"""
    Client Interface for POEditor API (https://poeditor.com).

    Usage:

    >>> from poeditor import POEditorAPI
    >>> client = POEditorAPI(api_token='my_token')
    >>> projects = client.list_projects()
"""

import json
from datetime import datetime
import tempfile

import requests

__all__ = ['POEditorException', 'POEditorArgsException', 'POEditorAPI']


class POEditorException(Exception):
    """
    POEditor API exception
    """
    def __init__(self, error_code, status, message):
        self.exp = u'POEditorException'
        self.error_code = error_code
        self.message = u"Status '{}', code {}: {}".format(
            status, error_code, message)
        super(POEditorException, self).__init__()

    def __str__(self):
        return self.message


class POEditorArgsException(Exception):
    """
    POEditor args method exception
    """
    def __init__(self, message):
        self.exp = u'POEditorArgsException'
        self.message = message
        super(POEditorArgsException, self).__init__()


class POEditorAPI(object):
    """
    Connect your software to POEditor with its simple API
    Please refers to https://poeditor.com/api_reference/ if you have questions
    """

    HOST = "https://poeditor.com/api/"

    SUCCESS_CODE = "success"
    FILE_TYPES = ['po', 'pot', 'mo', 'xls', 'apple_strings', 'android_strings',
                  'resx', 'resw', 'properties', 'json', 'key_value_json']
    FILTER_BY = ['translated', 'untranslated', 'fuzzy', 'not_fuzzy',
                 'automatic', 'not_automatic']

    UPDATING_TERMS = 'terms'
    UPDATING_TERMS_DEFINITIONS = 'terms_definitions'
    UPDATING_DEFINITIONS = 'definitions'

    # in seconds. Upload: No more than one request every 30 seconds
    MIN_UPLOAD_INTERVAL = 30

    def __init__(self, api_token):
        """
        All requests to the API must contain the parameter api_token.
        You'll find it in My Account > API Access in your POEditor account.
        """
        self.api_token = api_token

    def _run(self, action, headers=None, **kwargs):
        """
        Requests API
        """
        payload = kwargs
        payload.update({'action': action, 'api_token': self.api_token})
        if payload.get('file'):
            file = {'file': payload.pop('file')}
            response = requests.post(url=self.HOST, data=payload, headers=headers, files=file)
        else:
            response = requests.post(url=self.HOST, data=payload, headers=headers)

        if response.status_code != 200:
            raise POEditorException(
                status='fail',
                error_code=response.status_code,
                message=response.reason
            )

        data = json.loads(response.text)

        if 'response' not in data:
            raise POEditorException(
                status='fail',
                error_code=-1,
                message=u'"response" key is not present'
            )

        if 'status' in data['response'] and \
                data['response']['status'] != self.SUCCESS_CODE:
            raise POEditorException(
                error_code=data['response'].get('code'),
                status=data['response']['status'],
                message=data['response'].get('message')
            )

        return data

    def _project_formatter(self, data):
        """
        Project object
        """
        open_ = False if not data['open'] or data['open'] == '0' else True
        public = False if not data['public'] or data['public'] == '0' else True
        return {
            'created': datetime.strptime(data['created'], '%Y-%m-%d %H:%M:%S'),
            'id': int(data['id']),
            'name': data['name'],
            'open': open_,
            'public': public,
        }

    def list_projects(self):
        """
        Returns the list of projects owned by user.
        """
        data = self._run(
            action="list_projects"
        )
        projects = data.get('list', [])
        return [self._project_formatter(item) for item in projects]

    def create_project(self, name, description=None):
        """
        creates a new project. Returns the id of the project (if successful)
        """
        description = description or ''
        data = self._run(
            action="create_project",
            name=name,
            description=description
        )
        return data['response']['item']

    def view_project_details(self, project_id):
        """
        Returns project's details.
        """
        data = self._run(
            action="view_project",
            id=project_id
        )
        return self._project_formatter(data['item'])

    def list_project_languages(self, project_id):
        """
        Returns project languages and percentage of translation done for each.
        """
        data = self._run(
            action="list_languages",
            id=project_id
        )
        return data.get('list', [])

    def add_language_to_project(self, project_id, language_code):
        """
        Adds a new language to project
        """
        self._run(
            action="add_language",
            id=project_id,
            language=language_code
        )
        return True

    def delete_language_from_project(self, project_id, language_code):
        """
        Deletes existing language from project
        """
        self._run(
            action="delete_language",
            id=project_id,
            language=language_code
        )
        return True

    def set_reference_language(self, project_id, language_code):
        """
        Sets a reference language to project
        """
        self._run(
            action="set_reference_language",
            id=project_id,
            language=language_code
        )
        return True

    def clear_reference_language(self, project_id):
        """
        Clears reference language from project
        """
        self._run(
            action="clear_reference_language",
            id=project_id
        )
        return True

    def view_project_terms(self, project_id, language_code=None):
        """
        Clears reference language from project
        """
        data = self._run(
            action="view_terms",
            id=project_id,
            language=language_code
        )
        return data.get('list', [])

    def add_terms(self, project_id, data):
        """
        Adds terms to project.
        >>> data = [
            {
                "term":"Add new list",
                "context":"",
                "reference":"/projects",
                "plural":""
            },
            {
                "term":"one project found",
                "context":"",
                "reference":"/projects",
                "plural":"%d projects found",
                "tags":[
                    "first_tag",
                    "second_tag"
                ]
            },
            {
                "term":"Show all projects",
                "context":"",
                "reference":"/projects",
                "plural":"",
                "tags":"just_a_tag"
            }
        ]
        """
        data = self._run(
            action="add_terms",
            id=project_id,
            data=json.dumps(data)
        )
        return data['details']

    def delete_terms(self, project_id, data):
        """
        Deletes terms from project.
        >>> data = [
            {
                "term":"one project found",
                "context":""
            },
            {
                "term":"Show all projects",
                "context":"form"
            }
        ]
        """
        data = self._run(
            action="delete_terms",
            id=project_id,
            data=json.dumps(data)
        )
        return data['details']

    def sync_terms(self, project_id, data):
        """
        Syncs your project with the array you send (terms that are not found
        in the dict object will be deleted from project and the new ones
        added).
        >>> data = [
            {
                "term":"Add new list",
                "context":"",
                "reference":"/projects",
                "plural":""
            },
            {
                "term":"one project found",
                "context":"",
                "reference":"/projects",
                "plural":"%d projects found",
                "tags":[
                    "first_tag",
                    "second_tag"
                ]
            },
            {
                "term":"Show all projects",
                "context":"",
                "reference":"/projects",
                "plural":"",
                "tags":"just_a_tag"
            }
        ]
        """
        data = self._run(
            action="sync_terms",
            id=project_id,
            data=json.dumps(data)
        )
        return data['details']

    def update_project_language(self, project_id, language_code, data):
        """
        Inserts / overwrites translations.
        >>> data = [
            {
                "term":{
                "term":"%d Projects available",
                "context":"project list"
            },
                "definition":{
                    "forms":[
                        "first form",
                        "second form",
                        "and so on"
                    ],
                    "fuzzy":"1/0"
                }
            }
        ]
        """
        data = self._run(
            action="update_language",
            id=project_id,
            language=language_code,
            data=json.dumps(data)
        )
        return data['details']

    def export(self, project_id, language_code, file_type='po', filters=None,
               tags=None, local_file=None):
        """
        Return terms / translations

        filters - filter by self._filter_by
        tags - filter results by tags;
        local_file - save content into it. If None, save content into
            random temp file.

        >>> tags = 'name-of-tag'
        >>> tags = ["name-of-tag"]
        >>> tags = ["name-of-tag", "name-of-another-tag"]

        >>> filters = 'translated'
        >>> filters = ["translated"]
        >>> filters = ["translated", "not_fuzzy"]
        """
        if file_type not in self.FILE_TYPES:
            raise POEditorArgsException(
                u'content_type: file format {}'.format(self.FILE_TYPES))

        if filters and filters not in self.FILTER_BY:
            raise POEditorArgsException(
                u"filters - filter results by {}".format(self.FILTER_BY))

        data = self._run(
            action="export",
            id=project_id,
            language=language_code,
            type=file_type,
            filters=filters,
            tags=tags
        )
        file_url = data['item']

        # Download file content:
        res = requests.get(file_url, stream=True)
        if not local_file:
            tmp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix='.{}'.format(file_type))
            tmp_file.close()
            local_file = tmp_file.name

        with open(local_file, 'w+b') as po_file:
            for data in res.iter_content(chunk_size=1024):
                po_file.write(data)
        return file_url, local_file

    def _upload(self, project_id, updating, file_path, language_code=None,
                overwrite=False, sync_terms=False, tags=None, fuzzy_trigger=None):
        """
        Internal: updates terms / translations
        """
        options = [
            self.UPDATING_TERMS,
            self.UPDATING_TERMS_DEFINITIONS,
            self.UPDATING_DEFINITIONS
        ]
        if updating not in options:
            raise POEditorArgsException(
                u'Updating arg must be in {}'.format(options)
            )

        options = [
            self.UPDATING_TERMS_DEFINITIONS,
            self.UPDATING_DEFINITIONS
        ]
        if language_code is None and updating in options:
            raise POEditorArgsException(
                u'Language code is required only if updating is '
                u'terms_definitions or definitions)'
            )

        if updating == self.UPDATING_DEFINITIONS:
            tags = None
            sync_terms = None

        # Special content type:
        tags = tags or ''
        language_code = language_code or ''
        sync_terms = '1' if sync_terms else '0'
        overwrite = '1' if overwrite else '0'
        fuzzy_trigger = '1' if fuzzy_trigger else '0'
        project_id = str(project_id)

        data = self._run(
            action="upload",
            id=project_id,
            language=language_code,
            file=open(file_path, 'r+b'),
            updating=updating,
            tags=tags,
            sync_terms=sync_terms,
            overwrite=overwrite,
            fuzzy_trigger=fuzzy_trigger,
            headers=None
        )
        return data['details']

    def update_terms(self, project_id, file_path=None, language_code=None,
                     overwrite=False, sync_terms=False, tags=None, fuzzy_trigger=None):
        """
        Updates terms - No more than one request every 30 seconds

        overwrite: set it to True if you want to overwrite definitions
        sync_terms: set it to True if you want to sync your terms (terms that
            are not found in the uploaded file will be deleted from project
            and the new ones added).
        tags: add tags to the project terms. you can use the following keys:
            "all": for the all the imported terms,
            "new": for the terms which aren't already in the project and
            "obsolete": for the terms which are in the project but not in the
                imported file
        fuzzy_trigger: set it to True to mark corresponding translations from the
            other languages as fuzzy for the updated values
        """
        return self._upload(
            project_id=project_id,
            updating=self.UPDATING_TERMS,
            file_path=file_path,
            language_code=language_code,
            overwrite=overwrite,
            sync_terms=sync_terms,
            tags=tags,
            fuzzy_trigger=fuzzy_trigger
        )

    def update_terms_definitions(self, project_id, file_path=None,
                                 language_code=None, overwrite=False,
                                 sync_terms=False, tags=None, fuzzy_trigger=None):
        """
        Updates terms definitions - No more than one request every 30 seconds

        overwrite: set it to True if you want to overwrite definitions
        sync_terms: set it to True if you want to sync your terms (terms that
            are not found in the uploaded file will be deleted from project
            and the new ones added).
        tags: add tags to the project terms. you can use the following keys:
            "all": for the all the imported terms,
            "new": for the terms which aren't already in the project and
            "obsolete": for the terms which are in the project but not in the
                imported file
        fuzzy_trigger: set it to True to mark corresponding translations from the
            other languages as fuzzy for the updated values
        """
        return self._upload(
            project_id=project_id,
            updating=self.UPDATING_TERMS_DEFINITIONS,
            file_path=file_path,
            language_code=language_code,
            overwrite=overwrite,
            sync_terms=sync_terms,
            tags=tags,
            fuzzy_trigger=fuzzy_trigger
        )

    def update_definitions(self, project_id, file_path=None,
                           language_code=None, overwrite=False, fuzzy_trigger=None):
        """
        Updates terms definitions - No more than one request every 30 seconds

        overwrite: set it to True if you want to overwrite definitions
        fuzzy_trigger: set it to True to mark corresponding translations from the
            other languages as fuzzy for the updated values
        """
        return self._upload(
            project_id=project_id,
            updating=self.UPDATING_DEFINITIONS,
            file_path=file_path,
            language_code=language_code,
            overwrite=overwrite,
            fuzzy_trigger=fuzzy_trigger
        )

    def available_languages(self):
        """
        Returns a list containing all the available languages
        """
        data = self._run(
            action="available_languages"
        )
        return data.get('list', {})

    def list_contributors(self, project_id=None, language_code=None):
        """
        Returns the list of contributors
        """
        data = self._run(
            action="list_contributors",
            id=project_id,
            language=language_code
        )
        return data.get('list', [])

    def add_contributor(self, project_id, name, email, language_code):
        """
        Adds a contributor to a project language
        """
        self._run(
            action="add_contributor",
            id=project_id,
            name=name,
            email=email,
            language=language_code
        )
        return True

    def add_administrator(self, project_id, name, email):
        """
        Adds a contributor to a project language
        """
        self._run(
            action="add_contributor",
            id=project_id,
            name=name,
            email=email,
            admin=True
        )
        return True
