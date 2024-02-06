import sys
sys.path.append("..")

from types import SimpleNamespace
import unittest
# import json

# import re

import app.db as db
import app.utils_spacy as utils

# This works only within integration tests
Settings = SimpleNamespace(DB_HOST="database:8080")

db.init_client(Settings)

class Test03DB(unittest.TestCase):
    def test_01_query_sdg_keywords(self):
        result = db.query_sdg_keywords("sdg_3")

        self.assertGreater(len(result), 0)
        # print(json.dumps(result, indent=2))
        self.assertEqual(result[0]['sdg']['id'], "sdg_3")

    def test_02_query_sdg_keywords_invalid_sdg(self):
        result = db.query_sdg_keywords("sdg_22")

        self.assertEqual(len(result), 0)

    def test_03_query_keyword_term(self):
        # Any sdg require at least one construct
        result = db.query_keyword_term("sdg3_en_c2")

        # print(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['sdg']['id'], "sdg_3")
        self.assertEqual(result[0]['language'], "en")

    def test_04_query_keyword_term_invalid_construct(self):
        # This works because the kw-importer use the row number as construct id 
        # and the first row is reserved for the headers
        result = db.query_keyword_term("sdg3_en_c1")

        self.assertEqual(len(result), 0)

    def test_05_query_keyword_matching_objects(self):
        keyword = {
            "keyword": "smart microgrid",
            "required_context": None,
            "forbidden_context": None,
            "language": "en"
        }
        result = db.query_keyword_matching_info_object(keyword)

        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]['language'], "en")

    def test_06_query_keyword_matching_objects_forbidden_context(self):
        keyword = {
            "keyword": "smart microgrid",
            "required_context": None,
            "forbidden_context": "control capabilities",
            "language": "en"
        }
        result = db.query_keyword_matching_info_object(keyword)

        self.assertEqual(len(result), 0)

    def test_07_query_object_matching_keywords(self):
        info_object = {
            "title": "Smart microgrid",
            "abstract": "A smart microgrid is a microgrid that is smart.",
            "extras": "This is a smart microgrid.",
            "language": "en"
        }

        content = " ".join([
            info_object[content_field] for content_field in ["title", "abstract", "extras"]
            if content_field in info_object and info_object[content_field] is not None
        ])

        tokens = utils.tokenize_text(content, info_object["language"])
        token_values = [token.text for token in tokens]

        result = db.query_all_sdgMatch_where_keyword_contains_any_of(
            token_values,
            info_object["language"]
        )

        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]['language'], "en")
