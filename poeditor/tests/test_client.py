import re
import os
import unittest
import logging

from poeditor.client import POEditorAPI, POEditorException, POEditorArgsException


logger = logging.getLogger(__name__)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.API_TOKEN = os.environ.get('POEDITOR_TOKEN', None)

    def test_authentication(self):
        # bad token
        client = POEditorAPI(api_token="BAD_TOKEN")

        with self.assertRaises(POEditorException) as context:
            client.list_projects()
        self.assertEqual(
            context.exception.message,
            "Status 'fail', code 4011: Invalid API Token"
        )

        # good token
        client = POEditorAPI(api_token=self.API_TOKEN)
        client.list_projects()

    def test_scenario(self):

        client = POEditorAPI(api_token=self.API_TOKEN)

        # Project:
        projects = client.list_projects()
        self.assertTrue(isinstance(projects, list))

        self.new_project_id = client.create_project(
            name='test project',
            description='Created by test_scenario method'
        )

        project_details = client.view_project_details(
            self.new_project_id
        )
        self.assertEqual(project_details['name'], "test project")
        self.assertEqual(project_details['id'], self.new_project_id)
        self.assertEqual(project_details['open'], False)
        self.assertEqual(project_details['public'], False)

        project_languages = client.list_project_languages(
            self.new_project_id
        )
        self.assertEqual(project_languages, [])

        result = client.add_language_to_project(
            project_id=self.new_project_id,
            language_code='fr'
        )
        self.assertTrue(result)

        result = client.add_language_to_project(
            project_id=self.new_project_id,
            language_code='de'
        )
        self.assertTrue(result)

        result = client.delete_language_from_project(
            project_id=self.new_project_id,
            language_code='de'
        )
        self.assertTrue(result)

        project_languages = client.list_project_languages(
            self.new_project_id
        )
        self.assertEqual(len(project_languages), 1)
        project_language_fr = project_languages[0]
        self.assertEqual(project_language_fr['percentage'], 0)
        self.assertEqual(project_language_fr['code'], 'fr')
        self.assertEqual(project_language_fr['name'], 'French')

        result = client.set_reference_language(
            project_id=self.new_project_id,
            language_code='fr'
        )
        self.assertTrue(result)

        result = client.clear_reference_language(
            project_id=self.new_project_id
        )
        self.assertTrue(result)

        # Plays with terms:
        terms = client.view_project_terms(
            project_id=self.new_project_id,
            language_code='fr'
        )
        self.assertEqual(terms, [])

        details = client.add_terms(
            project_id=self.new_project_id,
            data=[
                {
                    "term": "Welcome to my new website",
                    "context": "",
                    "reference": "Homepage title",
                    "plural": ""
                },
                {
                    "term": "There is 1 student in the band",
                    "context": "",
                    "reference": "Band count",
                    "plural": "there are {count} students in the band"
                },
            ]
        )
        self.assertEqual(details['parsed'], 2)
        self.assertEqual(details['added'], 2)

        details = client.delete_terms(
            project_id=self.new_project_id,
            data=[
                {
                    "term": "There is 1 student in the band",
                    "context": ""
                }
            ]
        )
        self.assertEqual(details['parsed'], 1)
        self.assertEqual(details['deleted'], 1)

        details = client.sync_terms(
            project_id=self.new_project_id,
            data=[
                {
                    "term": "Welcome to my new website",
                    "context": "",
                    "reference": "Homepage title",
                    "plural": ""
                },
                {
                    "term": "New term",
                    "context": "",
                    "reference": "",
                    "plural": "",
                    "tags": [
                        "first_tag",
                        "second_tag"
                    ]
                },
            ]
        )
        self.assertEqual(details['parsed'], 2)
        self.assertEqual(details['added'], 1)
        self.assertEqual(details['updated'], 0)
        self.assertEqual(details['deleted'], 0)

        # Plays with translations
        details = client.update_project_language(
            project_id=self.new_project_id,
            language_code='fr',
            data=[
                {
                    "term": "Welcome to my new website",
                    "context": "",
                    "translation": {
                        "content": "Bienvenue sur mon site",
                        "fuzzy": 1
                    }
                }
            ]
        )
        self.assertEqual(details['parsed'], 1)
        self.assertEqual(details['added'], 1)
        self.assertEqual(details['updated'], 0)

        # Export
        file_url, self.file_path = client.export(
            project_id=self.new_project_id,
            language_code='fr',
            file_type='po'
        )

        self.assertTrue(
            file_url.startswith('https://api.poeditor.com/v2/download/file/'))
        self.assertTrue(os.path.isfile(self.file_path))
        with open(self.file_path, 'r') as file_read:
            data = file_read.read()
        self.assertIn('Welcome to my new website', data)
        self.assertIn('Bienvenue sur mon site', data)

        # Export with filters
        with self.assertRaises(POEditorArgsException) as context:
            client.export(
                project_id=self.new_project_id,
                language_code='fr',
                file_type='po',
                filters=["translated", "maybe_fuzzy"]
            )
        self.assertIn("filters - filter results by", context.exception.message)

        file_url, not_fuzzy_path = client.export(
            project_id=self.new_project_id,
            language_code='fr',
            file_type='po',
            filters=["translated", "not_fuzzy"]
        )

        with open(not_fuzzy_path, 'r') as file_read:
            data = file_read.read()
        self.assertNotIn('Welcome to my new website', data)
        self.assertNotIn('Bienvenue sur mon site', data)

        # Import
        # Just a quick update before:
        with open(self.file_path, "r") as sources:
            lines = sources.readlines()
        with open(self.file_path, "w") as sources:
            for line in lines:
                sources.write(
                    re.sub(r'^msgstr "Bienvenue sur mon site"', 'msgstr "Bienvenue!"', line)
                )

        details = client.update_terms_translations(
            project_id=self.new_project_id,
            file_path=self.file_path,
            language_code='fr',
            overwrite=True,
            sync_terms=True
        )

        expected_dict = {
            'translations': {
                'added': 0,
                'parsed': 1,
                'updated': 1
            },
            'terms': {
                'added': 0,
                'deleted': 0,
                'parsed': 2
            }
        }
        self.assertDictEqual(details, expected_dict)

        # Languages:
        languages = client.available_languages()
        self.assertTrue(isinstance(languages, list))
        self.assertIn('French', [lang['name'] for lang in languages])

        # Contributors
        contributors = client.list_contributors(
            project_id=self.new_project_id)
        self.assertEqual(contributors, [])

        result = client.add_contributor(
            project_id=self.new_project_id,
            name="Peter",
            email="peter@example.org",
            language_code='fr'
        )
        self.assertTrue(result)

        result = client.add_administrator(
            project_id=self.new_project_id,
            name="John",
            email="john@example.org"
        )
        self.assertTrue(result)

    def tearDown(self):
        if hasattr(self, 'new_project_id'):
            client = POEditorAPI(api_token=self.API_TOKEN)
            logger.info(
                "Deleting test project project_id={}. ".format(
                    self.new_project_id
                )
            )
            client.delete_project(self.new_project_id)

        if hasattr(self, 'file_path'):
            try:
                logger.info(
                    "Removing temp test file file_path={}. ".format(
                        self.file_path
                    )
                )
                os.remove(self.file_path)
            except:
                pass


if __name__ == '__main__':
    unittest.main()
