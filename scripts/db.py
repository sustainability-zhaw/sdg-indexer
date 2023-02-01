# -*- coding: utf-8 -*-
"""
=====================================
Created on Thu Jan 26 2023 09:55
@author: Martin Rerabek, martin.rerabek@zhaw.ch
Copyright © 2023, Predictive Analytics Group, ICLS, ZHAW. All rights reserved.
=====================================

"""
# import modules
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings

_client = Client(
    transport=RequestsHTTPTransport(url=f"http://localhost:8080/graphql"),
    fetch_schema_from_transport=True
)


def query_keywords():
    return _client.execute(
        gql(
            """
            query{
                querySdgMatch
                {
                    construct
                    keyword
                    required_context
                    forbidden_context
                    language
                    sdg{ 
                        id 
                    }


                }
            }
            """
        ))['querySdgMatch']


def query_unchecked_keywords():
    return _client.execute(
        gql(
            """
            query($batchSize:Int){
                querySdgMatch(filter: { keyword_check: { eq: null } }, first:$batchSize) {
                    construct
                    keyword
                    required_context
                    forbidden_context
                    language
                    sdg{ 
                        id 
                    }


                }
            }
            """
        ),
        variable_values={"batchSize": settings.BATCH_SIZE}
    )['querySdgMatch']


def query_keyword_matching_info_object(keyword):
    fields = ["title", "abstract", "extras"]

    filter_template = {"filter":
        {"and": [
            {"language": {"eq": keyword['language']}},
            {"or": [
                {"and": []},
                {"and": []},
                {"and": []}
            ]}
        ]}}

    if (keyword['keyword'] is not None) or (keyword['keyword'] != ''):
        for ind, field in enumerate(fields):
            filter_template['filter']['and'][1]['or'][ind]['and'].append(
                {field: {"alloftext": keyword['keyword']}})

    if (keyword['required_context'] is not None) or (keyword['required_context'] != ''):
        for ind, field in enumerate(fields):
            filter_template['filter']['and'][1]['or'][ind]['and'].append(
                {field: {"alloftext": keyword['required_context']}})

    if (keyword['forbidden_context'] is not None) or (keyword['forbidden_context'] != ''):
        for ind, field in enumerate(fields):
            filter_template['filter']['and'][1]['or'][ind]['and'].append(
                {"not": {field: {"alloftext": keyword['forbidden_context']}}})
    #
    # {"filter":
    #     {"and": [
    #         {"language": {"eq": keyword['language']}},
    #         {"or": [
    #             {"and": [
    #                 {"title": {"alloftext": keyword['keyword']}},
    #                 {"title": {"alloftext": keyword['required_context']}},
    #                 {"not": {"title": {"alloftext": keyword['forbidden_context']}}}
    #             ]},
    #             {"and": [
    #                 {"abstract": {"alloftext": keyword['keyword']}},
    #                 {"abstract": {"alloftext": keyword['required_context']}},
    #                 {"not": {"abstract": {"alloftext": keyword['forbidden_context']}}}
    #             ]},
    #             {"and": [
    #                 {"extras": {"alloftext": keyword['keyword']}},
    #                 {"extras": {"alloftext": keyword['required_context']}},
    #                 {"not": {"extras": {"alloftext": keyword['forbidden_context']}}}
    #             ]}
    #         ]}
    #     ]
    #     }
    # }

    return _client.execute(
        gql(
            """
                query infoObject($filter: InfoObjectFilter) {
                    queryInfoObject(filter: $filter){
                        title
                        abstract
                        language
                        link
                        keywords{
                            name
                            }
                        sdgs{
                            id
                            }
                        sdg_check
                        sdg_matches{
                            construct
                            keyword
                            required_context
                            forbidden_context
                            language
                            sdg{
                                id
                            }
                            }
                    }
                }
                """
        ),
        variable_values=filter_template
        # {
        #     "filter": {
        #         "or": [
        #             {"and": [
        #                 {"language": {"eq": keyword['language']}},
        #                 {"title": {"alloftext": keyword['keyword']}}
        #             ]},
        #             {"and": [
        #                 {"language": {"eq": keyword['language']}},
        #                 {"abstract": {"alloftext": keyword['keyword']}}
        #             ]},
        #             {"and": [
        #                 {"language": {"eq": keyword['language']}},
        #                 {"extras": {"alloftext": keyword['keyword']}}
        #             ]}
        #             # ,
        #             # {"and": [
        #             #     {"language": {"eq": keyword['language']}},
        #             #     {"keywords": {"name": {"anyofterms": keyword['keyword']}}}
        #             # ]}
        #         ]
        #     }
        # }
    )['queryInfoObject']


def update_info_object(update_input):
    # insert sdg based on link
    _client.execute(
        gql(
            """
            mutation updateInfoObject($update_input: UpdateInfoObjectInput!){
                updateInfoObject(input: $update_input) {
                    infoObject {
                        link 
                        sdgs{
                        id
                        }
                        sdg_matches{
                            construct
                            keyword
                            required_context
                            forbidden_context
                            language
                            sdg{
                                id
                            }
                            }
                        }
                }
            }
            """
        ),
        variable_values=update_input
    )
