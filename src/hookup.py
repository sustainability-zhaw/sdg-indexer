# -*- coding: utf-8 -*-

# import modules

import settings
import logging
import db
import utils

# logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level='DEBUG')

logger = logging.getLogger("sdgindexer")

def checkNLPMatch(infoObject, keyword_item):
    # TODO: Implement token normalisation and then token based order verification
    return True
    
def handleKeywordItem(keyword_item):
    logger.debug("handle one keyword item ")
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

def run(next):
    logger.debug("run service function")
    logger.debug(f"DB_HOST: {settings.DB_HOST}")
    logger.debug(f"Batch Size: {settings.BATCH_SIZE}")
    logger.debug(f"Batch Interval: {settings.BATCH_INTERVAL}")
    logger.debug(f"Log Level: {settings.LOG_LEVEL}")

    keyword_chunk =  db.query_keywords(next)

    for keyword_item in keyword_chunk:
        handleKeywordItem(keyword_item)

    if len(keyword_chunk) > 0:
        return next + len(keyword_chunk)

    return 0
