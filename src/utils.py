# import modules
import re
import string

import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from iso639 import Language

def check_us_and_uk_spelling(item, us_uk_file='https://raw.githubusercontent.com/sustainability-zhaw/keywords/main/data/UK_vs_US.csv'):
    """
    gets info about US and UK counterparts from external list and for each item finds counterpart
    :param item: a keyword
    :param us_uk_file:
    :return: counterpart
    """
    us_uk = pd.read_csv(us_uk_file, sep=';')

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
    is_quoted = quote_match is not None

    if is_quoted:
        quote_char = quote_match.group(1)

        # strip quotes from the value
        value = re.sub(f"^{quote_char}([^{quote_char}]*)(?:{quote_char}.*)?$", "\\1", value)
        value = re.sub("\s+", " " , value) # normalize inner whitespace
        value = re.escape(value) # escape special characters
        # replace leading and trailing whitespace with word boundary
        value = re.sub("^\\\\\\s|\\\\\\s$", "\\\\b", value)

    return value if is_quoted else None


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
