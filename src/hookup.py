import logging
import db
import utils_spacy as utils

import json

logger = logging.getLogger("sdgindexer")

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

    # if keyword_item['language'] == 'en':
    #     keyword_item = utils.process_sdg_match(keyword_item)

    info_objects = db.query_keyword_matching_info_object(keyword_item, links)

    if len(info_objects) == 0: 
        logger.debug(f"no protential objects for keyword item {keyword_item['construct']}")
        return

    logger.debug(f"found {len(info_objects)} protential objects for keyword item {keyword_item['construct']}")
    
    result_links = []

    for info_object in info_objects:
        # check each info object whether or not it actually matches
        if utils.match(info_object, keyword_item):
            logger.debug(
                f"found match for keyword item {keyword_item['construct']} in info object {info_object['link']}"
            )
            result_links.append(info_object['link'])

    update_input = ""

    logger.debug(result_links)

    if len(result_links) > 0: 
        update_input = {
            "update_input": {
                "filter": {
                    "link": {
                        "in": result_links
                    }
                },
                "set": {
                    "sdg_matches": [{
                        "construct": keyword_item['construct']
                    }],
                    "sdgs": [{
                        "id": keyword_item['sdg']['id']
                    }]
                }
            }
        }

        logger.debug(f"Updating info objects to SDG {keyword_item['sdg']['id']}: {update_input}")
        db.update_info_object(update_input)

def handleIndexChunk(body, keywords):
    list = []

    if ('links' in body) and (body['links'] is not None):
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

def indexObject(body):
    """
    Function to handle (re)indexing of a given object whenever an importer reports a single new object.
    The body contains the link to the infoObject in the database.
    """
    info_object = db.query_info_object_by_link(body["link"])

    if not info_object:
        return
    
    content = " ".join([
        info_object[content_field] for content_field in ["title", "abstract", "extras"]
        if content_field in info_object and info_object[content_field] is not None
    ])

    tokens = utils.tokenize_text(content, info_object["language"])

    # if the language is not supported, no tokenization is performed
    if tokens is None:
        return

    # select candidate SDG matches
    sdg_matches =  db.query_all_sdgMatch_where_keyword_contains_any_of(
        [token.text for token in tokens], 
        info_object["language"]
    )

    sdg_results = []

    for sdg_match in sdg_matches:
        # because of the tokenization, this loop won't work as comprehension
        if utils.match(info_object, sdg_match):
            sdg_results.append(sdg_match)

    # only update the object if there are any matches
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
    
