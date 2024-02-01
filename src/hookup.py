import logging
import re
import db
import utils

import json

logger = logging.getLogger("sdgindexer")

supportedLangs = ["en", "de", "fr", "it"]

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

    # skip NLP Matching for invalid language markers
    if len(infoObject["language"]) > 2:
        logger.warn(f"Excessive language String {info_object['language']}")
        return False
  
    # skip NLP Matching for unsupported languages
    if infoObject["language"] not in supportedLangs:
        logger.warn(f"Unsupported language {info_object['language']}")
        return False
    
    keyword_fields = list(filter(
        lambda keyword_field: keyword_field[0] in keyword_item and keyword_item[keyword_field[0]] is not None,
        [ # Order affects the exclude behaviour.
            ("forbidden_context", lambda found: bool(found)) , # Exclude if match
            ("required_context", lambda found: not bool(found)), # Exclude if no match
            ("keyword", lambda found: not bool(found)) # Exclude if no match
        ]
    ))

    content = " ".join([
        infoObject[content_field] for content_field in ["title", "abstract", "extras"]
        if content_field in infoObject and infoObject[content_field] is not None
    ])

    normalized_content = utils.normalize_text(content, infoObject["language"])

    for keyword_field, should_exclude_on_match in keyword_fields:
        is_match = False
        quoted_expression = utils.parse_quoted_expression(keyword_item[keyword_field])

        if quoted_expression is not None:
            logger.debug(f"index with quoted expression: {quoted_expression}")
            is_match = re.search(quoted_expression, content, re.I) is not None

            logger.debug(f"index with quoted expression: {quoted_expression} is {is_match}")
        else:
            logger.debug(f"index with NLP normalisation: {keyword_item[keyword_field]}")
            normalized_keyword = utils.normalize_text(keyword_item[keyword_field], keyword_item["language"])
            expression = ".*".join([re.escape(word) for word in normalized_keyword.split()])
            is_match = re.search(expression, normalized_content, re.I) is not None

        if should_exclude_on_match(is_match):
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

    logger.debug(f"handle one keyword item {json.dumps(keyword_item)}")
    # logger.debug(f"handle one keyword item {keyword_item['construct']}")

    if keyword_item['language'] == 'en':
        keyword_item = utils.process_sdg_match(keyword_item)

    info_objects = db.query_keyword_matching_info_object(keyword_item, links)

    if len(info_objects) == 0: 
        return

    logger.debug(f"found {len(info_objects)} protential objects for keyword item {keyword_item['construct']}")
    
    result_links = []

    for info_object in info_objects:
        # check each info object whether or not it actually matches
        if checkNLPMatch(info_object, keyword_item):
            logger.debug(f"found match for keyword item {keyword_item['construct']} in info object {info_object['link']}")
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

def indexObject(body):
    """
    Function to handle reindexing of a given object whenever an importer reports a single new object.
    The body contains the link to the infoObject in the database.
    """
    info_object = db.query_info_object_by_link(body["link"])

    if not info_object:
        return

    # skip NLP Matching for invalid language markers
    if len(info_object["language"]) > 2:
        logger.warn(f"Excessive language string {info_object['language']}")
        return
  
    # skip NLP Matching for unsupported languages
    if info_object["language"] not in supportedLangs:
        logger.warn(f"Unsupported language {info_object['language']}")
        return
    
    content = " ".join([
        info_object[content_field] for content_field in ["title", "abstract", "extras"]
        if content_field in info_object and info_object[content_field] is not None
    ])

    tokens = utils.tokenize_text(content, info_object["language"])
    sdg_matches =  db.query_all_sdgMatch_where_keyword_contains_any_of(tokens)

    # the following comprehension does not deliver what it promises
    # sdg_results = [sdg_match for sdg_match in sdg_matches if checkNLPMatch(info_object, sdg_match)]

    # This delivers :)
    sdg_results = []

    for sdg_match in sdg_matches:
        if checkNLPMatch(info_object, sdg_match):
            sdg_results.append(sdg_match)

    if (len(sdg_results) > 0):
        db.update_info_object({
            "update_input": {
                "filter": { "link": { "eq": info_object["link"] } },
                "set": { 
                    "sdg_matches": sdg_results,
                    "sdgs": list([{ "id": sdg_match["sdg"]["id"] } for sdg_match in sdg_results])
                 }
            }
        })

mqRoutingFunctions = {
    "indexer.add":       indexTerm,  # sent by UI changes
    "indexer.update":    indexTopic, # sent by GitHub webhook
    "importer.object":   indexObject, # all importer services send this topic
}

def run(mqKey, mqPayload):    
    logger.info(f"changed indices for {mqKey}: {mqPayload}")
    mqRoutingFunctions[mqKey](mqPayload)
    logger.info(f"updated indices for {mqKey}: {mqPayload}")
    
