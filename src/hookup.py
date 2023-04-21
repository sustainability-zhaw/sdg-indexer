# -*- coding: utf-8 -*-

import logging
import re
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
    normalized_content = None
    keyword_fields = list(filter(
        lambda keyword_field: keyword_field[0] in keyword_item and keyword_item[keyword_field[0]] is not None,
        [ # Order is important. It defines the exit condition for the loop.
            ("forbidden_context", lambda found: bool(found)) , # Exclude if match
            ("required_context", lambda found: not bool(found)), # Exclude if no match
            ("keyword", lambda found: not bool(found)) # Exclude if no match
        ]
    ))

    for keyword_field, should_be_excluded in keyword_fields:
        match = False
        quoted_expression = utils.parse_quoted_expression(keyword_item[keyword_field])
        content = " ".join([
            infoObject[content_field] for content_field in ["title", "abstract", "extras"]
            if content_field in infoObject and infoObject[content_field] is not None
        ])

        if quoted_expression:
            match = re.search(re.escape(quoted_expression), content, re.I) is not None
        else:
            if normalized_content is None:
                normalized_content = utils.normalize_text(content, infoObject["language"])
            normalized_keyword = utils.normalize_text(keyword_item[keyword_field], keyword_item["language"])
            expression = ".*".join(normalized_keyword.split())
            match = re.search(re.escape(expression), normalized_content, re.I) is not None

        if should_be_excluded(match):
            return False

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
    if ('links' in body) and (body['links'] is not None):
        list = body['links']
    else:
        list = []
    
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
    
