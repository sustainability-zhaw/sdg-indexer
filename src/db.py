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
    transport = RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)

# _client = Client(
#     transport=RequestsHTTPTransport(url=f"http://localhost:8080/graphql"),
#     fetch_schema_from_transport=True
# )


def query_keywords(offset):
    return _client.execute(
        gql(
            """
            query($offset: Int) {
                querySdgMatch(first: 100, offset: $offset)
                {
                    construct
                    keyword
                    required_context
                    forbidden_context
                    language
                    sdg { 
                        id 
                    }
                }
            }
            """
        ),
        variable_values = {
            "offset": offset
        })['querySdgMatch']


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
                    sdg { 
                        id 
                    }
                }
            }
            """,
            variable_values={"batchSize": settings.BATCH_SIZE}
        )
    )['querySdgMatch']


def query_keyword_matching_info_object(keyword):
    fields = ["title", "abstract", "extras"]

    filter_template = {"filter":
        {"and": [
            {"language": {"eq": keyword['language']}}
        ]}}

    if (keyword['keyword'] is not None) and (keyword['keyword'] != ''):
        filter_template['filter']['and'].append(
            { 'or': [
                {'title': {'alloftext': keyword['keyword']}},
                {'abstract': {'alloftext': keyword['keyword']}},
                {'extras': {'alloftext': keyword['keyword']}}
                ]
            }
        )
        
    if (keyword['required_context'] is not None) and (keyword['required_context'] != ''):
        filter_template['filter']['and'].append(
            { 'or': [
                {'title': {'alloftext': keyword['required_context']}},
                {'abstract': {'alloftext': keyword['required_context']}},
                {'extras': {'alloftext': keyword['required_context']}}
                ]
            }
        )

    if (keyword['forbidden_context'] is not None) and (keyword['forbidden_context'] != ''):
        filter_template['filter']['and'].append(
            { 'not': { 'or': [
                {'title': {'alloftext': keyword['forbidden_context']}},
                {'abstract': {'alloftext': keyword['forbidden_context']}},
                {'extras': {'alloftext': keyword['forbidden_context']}}
                ]
            } }
        )

    return _client.execute(
        gql(
            """
                query infoObject($filter: InfoObjectFilter) {
                    queryInfoObject(filter: $filter){
                        title
                        abstract
                        extras
                        language
                        link
                    }
                }
                """
        ),
        variable_values=filter_template
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
