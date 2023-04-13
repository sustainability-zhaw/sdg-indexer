# -*- coding: utf-8 -*-

# import modules
import pandas as pd
import re

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
    value = expression.lstrip()
    
    negation_match = re.match(r"^not:(.*)", value, re.I)
    is_negated = negation_match is not None
    # lstrip result because 'not:' could be followed by one or multiple whitespace(s).
    value = negation_match.group(1).lstrip() if is_negated else value
        
    quote_match = re.match(r"^(['\"])", value)
    is_quoted = quote_match is not None

    if is_quoted:
        quote_char = quote_match.group(1)
        quoted_term_match = re.match(f"^{quote_char}(.*){quote_char}|^{quote_char}(.*)", value)
        has_closing_quote = quoted_term_match.group(1) is not None
        # Trailing whitespaces are kept only if a matching closing quote is present.
        value = quoted_term_match.group(1) if has_closing_quote else quoted_term_match.group(2).rstrip()
    else:
        value = value.strip()

    return (value, is_negated) if is_quoted else None
