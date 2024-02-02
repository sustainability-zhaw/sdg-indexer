# import modules
import re
import string
import logging

import pandas as pd

# set up spaCy
import spacy

logger = logging.getLogger("indexer_utils")

# prefer gpu if available (which is not on our dev cluster)
spacy.prefer_gpu()

# load language classes for stopword manipulation
# cls_en = spacy.util.get_lang_class('en')
# cls_de = spacy.util.get_lang_class('de')
# cls_fr = spacy.util.get_lang_class('fr')
# cls_it = spacy.util.get_lang_class('it')

# load language models
# NOTE: all language modes are loaded here and remain persistent in memory
#    Any model updates are ephemeral and will be triggered by starting a new 
#    container. 
# TODO: Check memory load and consider to have configurable idexers for specific languages.
#    This will be necessary if the large models are used. 
nlp = {
    "en": spacy.load("en_core_web_sm"),
    "de": spacy.load("de_core_news_sm"),
    "fr": spacy.load("fr_core_news_sm"),
    "it": spacy.load("it_core_news_sm")
}

# from iso639 import Language

supportedLangs = ["en", "de", "fr", "it"]

# load UK vs US spelling differences
# This should be part of the container rather than loaded from the web
# Original source is https://gist.github.com/heiswayi/12ca9081ae1f18f6438b
# or raw: 
# https://gist.githubusercontent.com/heiswayi/12ca9081ae1f18f6438b/raw/4ca91f60a102265417783bbc013f73dc8841a3ac/spelling.csv
# check if needed

# EN_spelling = pd.read_csv(
#     'https://raw.githubusercontent.com/sustainability-zhaw/keywords/main/data/UK_vs_US.csv', 
#     sep=';'
# )

# def check_us_and_uk_spelling(item, us_uk=EN_spelling):
#     """
#     gets info about US and UK counterparts from external list and for each item finds counterpart
#     :param item: a keyword
#     :param us_uk_file:
#     :return: counterpart
#     """
#     # us_uk = pd.read_csv(us_uk_file, sep=';')

#     if (us_uk['UK'].eq(item)).any():
#         counterpart = us_uk.loc[(us_uk['UK'].eq(item)), 'US'].values[0]
#     elif (us_uk['US'].eq(item)).any():
#         counterpart = us_uk.loc[(us_uk['US'].eq(item)), 'UK'].values[0]
#     else:
#         counterpart = None
#     return counterpart

def process_sdg_match(sdg_match_record):
    """
    processes English phrases/keywords one by one (space separated), while keeping the phrase structure (comma separated)
    :param sdg_match_record: this is sdg_match object (record) from the database
    :return: sdg_match that contains both versions of english US and UK
    """
    sdg_match_record_updated = sdg_match_record.copy()
    for field in sdg_match_record.keys():
        if field in ['keyword', 'required_context', 'forbidden_context']:

            if sdg_match_record[field] is None: 
                continue

            # handle quoted expressions correctly
            if re.search(r"^['\"]", sdg_match_record[field]) is not None:
                sdg_match_record_updated[field] = sdg_match_record[field]
                continue

            phrases = re.split(r"[^\w\d]+", sdg_match_record[field])  # process comma separated phrases
            final_phrases = []

            for phrase in phrases:
                phrase = phrase.strip()
                items = phrase.split()
                counterparts = []

                for item in items:
                    counterpart = check_us_and_uk_spelling(item)
                    if counterpart is not None:
                        counterparts.append(counterpart)

                    else:
                        counterparts.append(item)
                counterparts = " ".join(map(str, counterparts))

                if phrase == counterparts:
                    final_phrases.append(phrase)
                else:
                    final_phrases.append(phrase)
                    final_phrases.append(counterparts)

            sdg_match_record_updated[field] = ' '.join(final_phrases)
    return sdg_match_record_updated


def match(infoObject, keyword_item):
    """
    Checks if a keyword object matches an infoobject. 

    The keyword_item and the infoObject are both expected to be in the same language.

    Matching is only performed if the language is supported (that is: de, en, fr, it)
    
    Runs the position exact keyword matching using NLP normalisation. 
    :param infoObject: an information object to check
    :param item: a keyword to match
    :return: boolean: True if the keyword matches for the information object, False otherwise.

    The database query returns a fuzzy matching, which is a super set of the 
    actual index terms. This function reduces this super set by narrowing the 
    results to include only the terms in sequence. For this purpose, the tokens
    need to be normalised to their word-stem and then the word stems must appear
    in the order that is given in the keyword_item.

    If the query term is quoted no normalisation MUST take place, but the term 
    must exist AS IS.
    """
    if len(infoObject["language"]) > 2:
        logger.warn(f"Excessive language String {info_object['language']}")
        return False
  
    # skip NLP Matching for unsupported languages
    if infoObject["language"] not in supportedLangs:
        logger.warn(f"Unsupported language {info_object['language']}")
        return False
    

    if infoObject["language"] != keyword_item["language"]:
        logger.warn("language mismatch")
        return False

    content = " ".join([
        infoObject[content_field] for content_field in ["title", "abstract", "extras"]
        if content_field in infoObject and infoObject[content_field] is not None
    ])

    content_tokens = tokenize_text(content, infoObject["language"])
    keyword_tokens = parse_keyword_item(keyword_item, infoObject["language"])

    matches = True

    verifier = {
        "forbidden_context": lambda found: not bool(found),
        "required_context": lambda found: bool(found),
        "keyword": lambda found: bool(found)
    }

    matching = {
        True: checkExactMatch,
        False: checkFuzzyMatch
    }

    for keyword_field in ["keyword", "required_context", "forbidden_context"]:
        if keyword_field not in keyword_tokens:
            continue

        matches = matches and verifier[keyword_field](
            matching[keyword_tokens[keyword_field]["quote"]](
                content_tokens, 
                keyword_tokens[keyword_field]
            )
        )
        
    return matches

def parse_keyword_item(keyword_item, lang_code):
    """
    Parses a keyword item and returns a list of tokens. 
    """
    if keyword_item is None:
        return None

    if lang_code not in nlp:
        return None
    
    retval = {}

    for keyword_field in ["keyword", "required_context", "forbidden_context"]:
        if keyword_field not in keyword_item or keyword_item[keyword_field] is None:
            continue

        # logger.debug(keyword_item)

        retval[keyword_field] = parse_quoted_expression(keyword_item[keyword_field])

        if retval[keyword_field] is not None:
            retval[keyword_field]["tokens"] = tokenize_text(retval[keyword_field]["value"], lang_code, True)
       
    return retval


def parse_quoted_expression(expression: str):
    # logger.debug(expression)

    value = expression.lstrip() # ensure no leading whitespaces
    quote_match = re.search(r"^(['\"])", value)

    # logger.debug(f"{value} -> {quote_match}")

    if quote_match is None:
        return {
        "value": value.strip(),
        "quote": False,
        "match_start": False,
        "match_end": False
    }

    value = re.sub(r"\s+", " " , value) # normalize inner whitespace

    quote_char = quote_match.group(1)

    # strip quotes from the value
    value = re.sub(f"^{quote_char}([^{quote_char}]*)(?:{quote_char}.*)?$", r"\1", value)

    match_start = re.search(r"^\s", value) is not None
    match_end = re.search(r"\s+$", value) is not None

    retval = {
        "value": value.strip(),
        "quote": True,
        "match_start": match_start,
        "match_end": match_end
    }

    return retval

def checkFuzzyMatch(texttokens, keyword):
    textTokens = [token.lemma_ for token in texttokens]
    keywordTokens = [token.lemma_ for token in keyword["tokens"]]

    retval = True

    for keywordToken in keywordTokens:
        retval = retval and (keywordToken in textTokens)

    return retval

def checkExactMatch(texttokens, keyword):
    object_text = " ".join([token.lemma_ for token in texttokens])
    keyword_text = " ".join([token.lemma_ for token in keyword["tokens"]])

    rawkeyword = keyword["value"]

    if keyword["match_start"]:
        keyword_text = r"\b" + keyword_text
        rawkeyword = r"\b" + rawkeyword
    
    if keyword["match_end"]:
        keyword_text = keyword_text + r"\b"
        rawkeyword = rawkeyword + r"\b"

    if re.search(rawkeyword, object_text, re.I) is not None:
        return True
    
    return re.search(keyword_text, object_text, re.I) is not None
      
def tokenize_text(text, lang_code, mode = False):
    if (lang_code not in nlp):
        return None
    
    doc = nlp[lang_code](text)

    # strip words with little information for the sdg indexing. 
    # - stop words
    # - punctuation
    # - numbers
    # - symbols
    # - spaces
    # 
    # Following tokens are not stripped:
    # - all capital words
    # - proper names (PROPN)
    return [token for token in doc if not token.is_punct 
                                      and token.pos_ != "NUM"
                                      and token.pos_ != "SYM"
                                      and token.pos_ != "NUM"
                                      # and token.pos_ != "PROPN"
                                      and not token.is_stop
                                      # and not re.match(r"^X+x?$", token.shape_)
                                      and not token.is_space]
