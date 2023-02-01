# -*- coding: utf-8 -*-
"""
=====================================
Created on Tue Jan 10 2023 09:40
@author: Martin Rerabek, martin.rerabek@zhaw.ch
Copyright © 2023, Predictive Analytics Group, ICLS, ZHAW. All rights reserved.
=====================================

"""
# import modules
import db
import utils
import datetime


for keyword_item in db.query_keywords():

    if keyword_item['language'] == 'en':
        keyword_item = utils.process_sdg_match(keyword_item)

    construct = keyword_item['construct']
    keywords = keyword_item['keyword'].split(",")
    required_contexts = keyword_item['required_context'].split(",")
    forbidden_contexts = keyword_item['forbidden_context'].split(",")

    # assume keywords comma separated
    # print(keyword_item)
    for keyword in keywords:
        keyword = keyword.strip()  # remove commas from strings and treat comma separated as one phrase

        for required_context in required_contexts:
            required_context = required_context.strip()  # remove commas from strings and treat comma separated as one phrase

            for forbidden_context in forbidden_contexts:
                forbidden_context = forbidden_context.strip()  # remove commas from strings and treat comma separated as one phrase

                # print(keyword, '\n', required_context, '\n', forbidden_context, '\n', sep='')

                info_objects = db.query_keyword_matching_info_object(keyword_item)
                if len(info_objects) > 0:
                    print(info_objects)

                    for info_object in info_objects:

                        update_input = {
                            "update_input": {
                                "filter": {
                                    "link": {"eq": info_object['link']}},
                                "set": {
                                    "sdg_matches": {
                                        "construct": construct,
                                        "keyword": keyword,
                                        "required_context": required_context,
                                        "forbidden_context": forbidden_context,
                                        "language": keyword_item['language']
                                    }
                                }
                            }
                        }

                        if keyword_item['sdg']['id'] not in info_object['sdgs']:    # if sdg does not exist
                            update_input['update_input']['set'].update({"sdgs": [{"id": keyword_item['sdg']['id']}]})

                        update_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                        update_input['update_input']['set'].update({"sdg_check": update_time})

                        db.update_info_object(update_input)
                        print(keyword_item)

