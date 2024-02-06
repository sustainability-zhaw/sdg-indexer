import sys
sys.path.append("..")

import unittest

# import re

import app.utils_spacy as utils


title = '''
Supervised exercises for patients with axial spondyloarthritis or rheumatoid arthritis: a systematic review of harms reporting in randomized controlled trials
'''

abstract = '''
To describe the quality of reporting and the nature of reported harms in clinical studies on the effectiveness of supervised exercises in patients with rheumatoid arthritis (RA) or axial spondyloarthritis (axSpA). We performed a systematic review, searching eight databases up to February 2023. Randomized controlled trials (RCTs) evaluating supervised exercises in adults with RA or axSpA were considered eligible. Data on harms were extracted according to the CONSORT Harms 2022 Checklist. Among others, it was recorded if harms were prespecified or non-prespecified. Moreover, the nature of reported harms was listed. Forty RCTs were included for RA and 25 for axSpA, of which 29 (73%) and 13 (52%) reported information on harms. In 13 (33%) RCTs in RA and four (16%) in axSpA, the collection of harms outcomes was described in the methods section. Prespecified outcomes were reported by eight (RA) and two (axSpA) RCTs. Non-specified harms outcomes were reported by six (RA) and four (axSpA) RCTs. Prespecified harms outcomes included measures of pain, disease activity, inflammation, and structural joint changes. The nature of non-prespecified harms outcomes varied largely, with pain being most common. A considerable proportion of trials on supervised exercise in RA or axSpA does not or inadequately report harms outcomes. Pain was the most commonly reported prespecified or non-specified harm. For a considerate interpretation of the balance between benefits and harms of supervised exercise in RA or axSpA, use of the CONSORT Harms 2022 Checklist for the design, conduct and reporting of trials is advocated.
'''

infoObject = {
    "title": title,
    "abstract": abstract,
    "language": "en"
}

class TestSpacy(unittest.TestCase):
    def test_01_token(self):
        result = utils.tokenize_text(abstract, "en")

        tlist = dict()
        for token in result:
            if token.lemma_ not in tlist:
                tlist[token.lemma_] = 0
            
            tlist[token.lemma_] += 1

            # print(f"{token.i} {token.lemma_} {token.shape_} {token.pos_} {token.tag_}")   
        #    print(f"{token} {token.lemma_} {token.shape_} {token.pos_} {token.tag_} {token.dep_} {token.is_alpha}")


        # print(tlist)
        
        self.assertEqual(len(result), 115)


# sentence level tokens https://stackoverflow.com/questions/58197863/how-to-get-sentence-number-in-spacy
        
    def test_02_matches_1(self):
        required_context = "family"
        result = utils.tokenize_text(required_context, "en")

        tlist = dict()
        for token in result:
            if token.lemma_ not in tlist:
                tlist[token.lemma_] = 0
            
            tlist[token.lemma_] += 1

            # print(f"{token.i} {token.lemma_} {token.shape_} {token.pos_} {token.tag_}")   
        #    print(f"{token} {token.lemma_} {token.shape_} {token.pos_} {token.tag_} {token.dep_} {token.is_alpha}")

        # print(tlist)

        self.assertEqual(len(result), 1)

    def test_03_matches_2(self):
        required_context = "developing countries"
        result = utils.tokenize_text(required_context, "en")

        tlist = dict()
        for token in result:
            if token.lemma_ not in tlist:
                tlist[token.lemma_] = 0
            
            tlist[token.lemma_] += 1

            # print(f"{token.i} {token.lemma_} {token.shape_} {token.pos_} {token.tag_}")   
        #    print(f"{token} {token.lemma_} {token.shape_} {token.pos_} {token.tag_} {token.dep_} {token.is_alpha}")

        # print(tlist)

        self.assertEqual(len(result), 2)

    def test_04_matches_3(self):
        required_context = '" shanty towns "'
        result = utils.tokenize_text(required_context, "en")

        tlist = dict()
        for token in result:
            if token.lemma_ not in tlist:
                tlist[token.lemma_] = 0
            
            tlist[token.lemma_] += 1

            # print(f"{token.i} {token.lemma_} {token.shape_} {token.pos_} {token.tag_}")   
        #    print(f"{token} {token.lemma_} {token.shape_} {token.pos_} {token.tag_} {token.dep_} {token.is_alpha}")

        # print(tlist)

        self.assertEqual(len(result), 2)


    def test_05_matching_noquotes_1(self):
        keyword_item = {
            "keyword": "exercise",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))

    def test_06_matching_noquotes_2(self):
        keyword_item = {
            "keyword": "exercise",
            "required_context": "harms pain",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))

    def test_07_matching_noquotes_3(self):
        keyword_item = {
            "keyword": "exercise",
            "forbidden_context": "family household",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))
    
    def test_08_nomatching_noquotes_1(self):
        keyword_item = {
            "keyword": "exercise",
            "required_context": "family household",
            "language": "en"
        }

        self.assertFalse(utils.match(infoObject, keyword_item))

    def test_09_nomatching_noquotes_2(self):
        keyword_item = {
            "keyword": "exercise",
            "forbidden_context": "harms pain",
            "language": "en"
        }

        self.assertFalse(utils.match(infoObject, keyword_item))

    def test_10_nomatching_noquotes_3(self):
        keyword_item = {
            "keyword": "exercise",
            "required_context": "family pain",
            "language": "en"
        }
        self.assertFalse(False)
    
    def test_11_matching_quotes_1(self):
        keyword_item = {
            "keyword": "'prespecified nature ",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))

    def test_12_matching_quotes_2(self):
        keyword_item = {
            "keyword": "'prespecified nature ",
            "required_context": "' systematic review ",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))

    def test_13_matching_quotes_3(self):
        keyword_item = {
            "keyword": "'prespecified nature ",
            "forbidden_context": "' family afairs ",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))

    def test_14_nomatching_quotes_1(self):
        keyword_item = {
            "keyword": "'prespecified nature ",
            "required_context": "' family afairs ",
            "language": "en"
        }

        self.assertFalse(utils.match(infoObject, keyword_item))

    def test_15_nomatching_quotes_2(self):
        keyword_item = {
            "keyword": "'undefined nature ",
            "language": "en"
        }

        self.assertFalse(utils.match(infoObject, keyword_item))

    def test_16_nomatching_quotes_3(self):
        keyword_item = {
            "keyword": "' prespecified nature ",
            "forbidden_context": "' disease activity ",
            "language": "en"
        }

        self.assertFalse(utils.match(infoObject, keyword_item))

    def test_17_matching_mixed_1(self):
        keyword_item = {
            "keyword": "'prespecified nature ",
            "required_context": "outcome activity",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))
        self.assertTrue(True)

    def test_18_matching_mixed_2(self):
        keyword_item = {
            "keyword": "structural nature ",
            "forbidden_context": "' family afairs ",
            "language": "en"
        }

        self.assertTrue(utils.match(infoObject, keyword_item))
        
    def test_19_nomatching_mixed_1(self):
        keyword_item = {
            "keyword": "' prespecified nature ",
            "forbidden_context": "outcome activity ",
            "language": "en"
        }

        self.assertFalse(utils.match(infoObject, keyword_item))

    def test_20_nomatching_mixed_2(self):
        keyword_item = {
            "keyword": " prespecified harms ",
            "forbidden_context": "' disease activity ",
            "language": "en"
        }

        self.assertFalse(utils.match(infoObject, keyword_item))

    def test_21_fuzzy_check_partmatch_tail(self):
        text_tokens = utils.tokenize_text(abstract, "en")
        fuzzy_tokens = utils.tokenize_text("family exercise", "en")
        
        self.assertFalse(utils.checkFuzzyMatch(text_tokens, {"tokens": fuzzy_tokens}))

    def test_22_fuzzy_check_partmatch_front(self):   
        text_tokens = utils.tokenize_text(abstract, "en")
        fuzzy_tokens = utils.tokenize_text("exercise family", "en")
        
        self.assertFalse(utils.checkFuzzyMatch(text_tokens, {"tokens": fuzzy_tokens}))

    def test_23_fuzzy_tokenize(self):
        # Some tokens are not properly recognized
        # One is trophic, which is recognized as a proper noun
        tokens = utils.tokenize_text("trophic web", "en")

        self.assertEqual(len(tokens), 2)

    def test_24_fuzzy_tokenize(self):
        # Some tokens are not properly recognized
        # One is trophic, which is recognized as a proper noun
        tokens = utils.tokenize_text("Foreign Development Investment", "en")

        self.assertEqual(len(tokens), 3)