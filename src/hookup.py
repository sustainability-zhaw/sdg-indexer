# -*- coding: utf-8 -*-

# import modules

import settings
import logging
import db
import utils
import json

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
        
    update_input = ""
    
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


def indexTopic(body):
    """
    Function to handle reindexing of a given topic (e.g., via an updated SDG keyword file).
    """ 
    logger.debug(f"got body: {body}")

    keyword_chunk =  db.query_sdg_keywords(body[0]['sdg'])
    for keyword_item in keyword_chunk:
        handleKeywordItem(keyword_item)


def indexObjects(body):
    """
    Function to handle reindexing of one or more objects
    """

    
def indexTerm(body):
    """
    Function to handle reindexing term that were added via the UI
    """
    keyword_chunk =  db.query_keyword_term(body['term'])
    for keyword_item in keyword_chunk:
        handleKeywordItem(keyword_item)


mqRoutingFunctions = {
    "indexer.add": indexTerm,
    "indexer.update": indexTopic,
    "importer.object": indexObjects
}

def handler(ch, method, properties, body):
    mqKey = method.routing_key
    mqPayload = json.loads(body)
    
    logger.info(f"changed indices for {mqKey}: {body}")
    
    mqRoutingFunctions[mqKey](mqPayload)

    logger.info(f"updated indices for {mqKey}: {body}")
