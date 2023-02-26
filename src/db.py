# -*- coding: utf-8 -*-

# import modules
import logging

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings

# helper 
from gql.transport.requests import log as requests_logger
requests_logger.setLevel(logging.WARNING)

_client = Client(
    transport = RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)

def query_sdg_keywords(sdg): 
    return _client.execute(
        gql(
            """
            query($sdg: String) {
                querySdgMatch @cascade(fields: ["sdg", "language", "construct"])
                {
                    construct
                    keyword
                    required_context
                    forbidden_context
                    language
                    sdg(filter: {id: { eq: $sdg }}) { 
                        id 
                    }
                }
            }
            """
        ),
        variable_values = {
            "sdg": sdg
        })['querySdgMatch']

def query_keyword_term(construct): 
    return _client.execute(
        gql(
            """
            query($sdg: String) {
                querySdgMatch(filter: {construct: {eq: $construct}}) @cascade(fields: ["sdg", "language", "construct"])
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
            "construct": construct
        })['querySdgMatch']

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
    if len(update_input) > 0:
        # insert sdg based on link
        _client.execute(
            gql(
                """
                mutation updateInfoObject($update_input: UpdateInfoObjectInput!) {
                    updateInfoObject(input: $update_input) {
                        infoObject {
                            link     
                        }
                    }
                }
                """
            ),
            variable_values=update_input
        )
