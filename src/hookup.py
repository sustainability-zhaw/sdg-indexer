# -*- coding: utf-8 -*-

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
    
def handleKeywordItem(keyword_item, links = []):
    """
    handles one key word item. 
    :param keyword_item: a keyword item structure
    :param links: a list constraining objects
    """
    if links is None:
        links = []

    logger.debug(f"handle one keyword item {keyword_item['construct']}")
    if keyword_item['language'] == 'en':
        keyword_item = utils.process_sdg_match(keyword_item)

    info_objects = db.query_keyword_matching_info_object(keyword_item, links)

    if len(info_objects) == 0: 
        return

    result_links = []

    for info_object in info_objects:
        # check each info object whether or not it actually matches
        if checkNLPMatch(info_object, keyword_item): 
            result_links.append(info_object['link'])

    update_input = ""

    if len(result_links) > 0: 
        construct = keyword_item['construct']
        sdg_id = keyword_item['sdg']['id']

        update_input = {
            "update_input": {
                "filter": {
                    "link": {
                        "in": result_links
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

def handleIndexChunk(body, keywords):
    if body['links'] is None: 
        list = []
    else:
        list = body['links']
    
    for keyword_item in keywords:
        handleKeywordItem(keyword_item, list)

def indexTopic(body):
    """
    Function to handle reindexing of a given topic (e.g., via an updated SDG keyword file).
    """ 
    keyword_chunk =  db.query_sdg_keywords(body['sdg'])
    handleIndexChunk(body, keyword_chunk)

def indexTerm(body):
    """
    Function to handle reindexing term that were added via the UI
    """
    keyword_chunk =  db.query_keyword_term(body['term'])
    handleIndexChunk(body, keyword_chunk)

mqRoutingFunctions = {
    "indexer.add":       indexTerm,
    "indexer.update":    indexTopic,
    "importer.object":   indexTopic,
    "importer.evento":   indexTopic,
    "importer.oai":      indexTopic,
    "importer.projects": indexTopic
}

def run(mqKey, mqPayload):    
    logger.info(f"changed indices for {mqKey}: {mqPayload}")
    mqRoutingFunctions[mqKey](mqPayload)
    logger.info(f"updated indices for {mqKey}: {mqPayload}")
    
