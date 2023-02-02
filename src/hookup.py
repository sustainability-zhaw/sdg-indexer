# -*- coding: utf-8 -*-
"""
=====================================
Created on Tue Jan 10 2023 09:40
@author: Martin Rerabek, martin.rerabek@zhaw.ch
Copyright © 2023, Predictive Analytics Group, ICLS, ZHAW. All rights reserved.
=====================================

"""
# import modules

import settings
import logging
import db
import utils
import datetime

# logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level='DEBUG')

logger = logging.getLogger("sdgindexer")

def run():
    logger.debug("run service function")
    logger.debug(f"DB_HOST: {settings.DB_HOST}")
    logger.debug(f"Batch Size: {settings.BATCH_SIZE}")
    logger.debug(f"Batch Interval: {settings.BATCH_INTERVAL}")
    logger.debug(f"Log Level: {settings.LOG_LEVEL}")

    for keyword_item in db.query_keywords():

        if keyword_item['language'] == 'en':
            keyword_item = utils.process_sdg_match(keyword_item)

        construct = keyword_item['construct']
        sdg_id = keyword_item['sdg']['id']

        # keywords = keyword_item['keyword'] # .split(",")
        # required_context = keyword_item['required_context'] # .split(",")
        # forbidden_context = keyword_item['forbidden_context'] # .split(",")

        # assume keywords comma separated
        # print(keyword_item)
        # for keyword in keywords:
        # keyword = keyword.strip()  # remove commas from strings and treat comma separated as one phrase

        #   #   for required_context in required_contexts:
        # if len(required_context): 
        #     required_context = required_context.strip()  # remove commas from strings and treat comma separated as one phrase

        # if len(forbidden_context):
        #     forbidden_context = forbidden_context.strip()  # remove commas from strings and treat comma separated as one phrase

                    # print(keyword, '\n', required_context, '\n', forbidden_context, '\n', sep='')

        info_objects = db.query_keyword_matching_info_object(keyword_item)
        if len(info_objects) > 0:
            # print(info_objects)
            update_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

            for info_object in info_objects:
                update_input = {
                    "update_input": {
                        "filter": {
                            "link": {
                                "eq": info_object['link']
                            }
                        },
                        "set": {
                            "sdg_matches": [{
                                "construct": construct
                            }],
                            "sdgs": [{
                                "id": sdg_id
                            }],
                            "sdg_check": update_time
                        }
                    }
                }

                # if keyword_item['sdg']['id'] not in info_object['sdgs']:    # if sdg does not exist
                #     update_input['update_input']['set'].update({"sdgs": [{"id": keyword_item['sdg']['id']}]})

                # update_input['update_input']['set'].update({"sdg_check": update_time})

                logger.debug(f"Updating person: {update_input}")
                db.update_info_object(update_input)
                # print(keyword_item)
