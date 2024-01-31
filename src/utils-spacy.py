# import modules
import re
import string

import pandas as pd

# set up spaCy
import spacy

# prefer gpu if available (which is not on our dev cluster)
spacy.prefer_gpu()

# load language models
# NOTE: all language modes are loaded here and remain persistent in memory
#    Any model updates are ephemeral and will be triggered by starting a new 
#    container. 
# TODO: Check memory load and consider to have configurable idexers for specific languages.
#    This will be necessary if the large models are used. 
nlp_en = spacy.load("en_core_web_sm")
nlp_de = spacy.load("de_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")
nlp_it = spacy.load("it_core_news_sm")

from iso639 import Language

# load UK vs US spelling differences
EN_spelling = pd.read_csv(
    'https://raw.githubusercontent.com/sustainability-zhaw/keywords/main/data/UK_vs_US.csv', 
    sep=';'
)

def check_us_and_uk_spelling(item, us_uk=EN_spelling):
    """
    gets info about US and UK counterparts from external list and for each item finds counterpart
    :param item: a keyword
    :param us_uk_file:
    :return: counterpart
    """
    # us_uk = pd.read_csv(us_uk_file, sep=';')

    if (us_uk['UK'].eq(item)).any():
        counterpart = us_uk.loc[(us_uk['UK'].eq(item)), 'US'].values[0]
    elif (us_uk['US'].eq(item)).any():
        counterpart = us_uk.loc[(us_uk['US'].eq(item)), 'UK'].values[0]
    else:
        counterpart = None
    return counterpart

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

            phrases = re.split("[^\w\d]+", sdg_match_record[field])  # process comma separated phrases
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


def parse_quoted_expression(expression: str):
    value = expression.lstrip() # ensure no leading whitespaces
    quote_match = re.match(r"^(['\"])", value)

    if quote_match is None:
        return None

    value = re.sub("\s+", " " , value) # normalize inner whitespace

    quote_char = quote_match.group(1)

    # strip quotes from the value
    value = re.sub(f"^{quote_char}([^{quote_char}]*)(?:{quote_char}.*)?$", "\\1", value)
    value = re.escape(value) # escape special characters
    # replace leading and trailing whitespace with word boundary
    value = re.sub("^\\\\\\s|\\\\\\s$", "\\\\b", value)
    return value


def normalize_text(text, lang_code):
    language = Language.from_part1(lang_code).name.lower()
    words = word_tokenize(text, language)
    stemmer = SnowballStemmer(language, ignore_stopwords=True)
    words = [stemmer.stem(word) for word in words if word not in string.punctuation]
    return " ".join(words)


def tokenize_text(text, lang_code):
    language = Language.from_part1(lang_code).name.lower()
    tokens = word_tokenize(text, language)
    stop_words = stopwords.words(language)
    tokens = [token for token in tokens if token not in stop_words and token not in string.punctuation and len(token) > 1]
    return set(tokens)
