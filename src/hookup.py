# -*- coding: utf-8 -*-

# import modules

import settings
import logging
import db
import utils

logger = logging.getLogger("sdgindexer")

def checkNLPMatch(infoObject, keyword_item):
    """
    runs the position exact keyword matching using NLP normalisation. 
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

    # TODO: Implement token normalisation and then token based order verification
    return True
    
def handleKeywordItem(keyword_item):
    """
    handles one key word item. 
    :param item: a keyword item structure
    :return: counterpart

    This function 
    """

    logger.debug(f"handle one keyword item {keyword_item['construct']}")
    if keyword_item['language'] == 'en':
        keyword_item = utils.process_sdg_match(keyword_item)

    construct = keyword_item['construct']
    sdg_id = keyword_item['sdg']['id']

    info_objects = db.query_keyword_matching_info_object(keyword_item)

    links = []

    for info_object in info_objects:
        # check each info object whether or not it actually matches
        if checkNLPMatch(info_object, keyword_item): 
            links.append(info_object['link'])
        
    if len(links) > 0: 
        update_input = {
            "update_input": {
                "filter": {
                    "link": {
                        "in": links
                    }
                },
                "set": {
                    "sdg_matches": [{
                        "construct": construct
                    }],
                    "sdgs": [{
                        "id": sdg_id
                    }]
                }
            }
        }

        logger.debug(f"Updating info objects to SDG {sdg_id}: {update_input}")
        db.update_info_object(update_input)

def run(next, use_empty, limitTime):
    """
    runs the next iteration of indexing loop
    :param next: from where to start the next round
    :param use_empty: 
    :return: iterator for the next round
    """

    logger.debug("run service function")
    logger.debug(f"DB_HOST: {settings.DB_HOST}")
    logger.debug(f"Batch Size: {settings.BATCH_SIZE}")
    logger.debug(f"Batch Interval: {settings.BATCH_INTERVAL}")
    logger.debug(f"Log Level: {settings.LOG_LEVEL}")

    if use_empty == 1:
        keyword_chunk =  db.query_empty_keywords(settings.BATCH_SIZE, next, limitTime)
    else: 
        keyword_chunk =  db.query_keywords(settings.BATCH_SIZE, next, limitTime)

    for keyword_item in keyword_chunk:
        handleKeywordItem(keyword_item)

    if len(keyword_chunk) > 0:
        return next + len(keyword_chunk)

    return 0
