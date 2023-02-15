# -*- coding: utf-8 -*-

# import modules
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings

_client = Client(
    transport = RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)

def query_keywords(size, offset, limit):
    return _client.execute(
        gql(
            """
            query($offset: Int, $first: Int, $limitdate: DateTime) {
                querySdgMatch(filter: {and: [{has: objects}, {has: sdg}, {dateUpdate: {gt: $limitdate}}]}, first: $first, offset: $offset)
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
            "offset": offset,
            "first": size,
            "limitdate": limit.isoformat()
        })['querySdgMatch']

def query_empty_keywords(size, offset, limit):
    return _client.execute(
        gql(
            """
            query($offset: Int, $first: Int, $limitdate: DateTime) {
                querySdgMatch(filter: {and: [{not: {has: objects}}, {has: sdg}, {dateUpdate: {gt: $limitdate}}]}, first: $first, offset: $offset)
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
            "offset": offset,
            "first": 2*size,
            "limitdate": limit.isoformat()
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
