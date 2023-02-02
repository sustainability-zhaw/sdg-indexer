# -*- coding: utf-8 -*-
"""
=====================================
Created on Wed Feb 01 2023 11:16
@author: Martin Rerabek, martin.rerabek@zhaw.ch
Copyright © 2023, Predictive Analytics Group, ICLS, ZHAW. All rights reserved.
=====================================

"""
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
