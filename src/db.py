# import modules
import logging
# import re

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

# helper 
from gql.transport.requests import log as requests_logger
requests_logger.setLevel(logging.WARNING)

logger = logging.getLogger("db_utils")

_client = None

def init_client(settings):
    global _client
    _client = Client(
        transport = RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
        fetch_schema_from_transport=True
    )

# _client = Client(
#     transport = RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
#     fetch_schema_from_transport=True
# )

def query_sdg_keywords(sdg): 
    return _client.execute(
        gql(
            """
            query($sdg: String!) {
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
            query($construct: String!) {
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
    
def query_keyword_matching_info_object(keyword, links = []):
    # empty keywords are forbidden
    if (keyword['keyword'] is None) or (keyword['keyword'] == ''):
        return []

    if links is None:
        links = []

    fields = ["title", "abstract", "extras"]
       
    if len(links) > 0:
        filter_template['filter']['and'].append({'link': {'in': links}})

    filter_template = {"filter":
        {"and": [
            {"language": {"eq": keyword['language']}},
            { 'or': [
                {'title': {'alloftext': keyword['keyword']}},
                {'abstract': {'alloftext': keyword['keyword']}},
                {'extras': {'alloftext': keyword['keyword']}}
                ]
            }
        ]}}
     
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

def query_info_object_by_link(link):
    return _client.execute(
        gql(
            """
            query getInfoObject($link: String!) {
                getInfoObject(link: $link) {
                    link
                    title
                    abstract
                    extras
                    language
                }
            }
            """
        ),
        variable_values={ "link": link }
    )["getInfoObject"]

def query_all_sdgMatch_where_keyword_contains_any_of(tokens, lang = "en"):
    return _client.execute(
        gql(
            """
            query querySdgMatch($filter: SdgMatchFilter) {
                querySdgMatch(filter: $filter) {
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
            "filter": {
                "and": [
                    {
                        "language": { "eq": lang }
                    },
                    { 
                        "keyword": {
                            "anyofterms": " ".join(tokens)
                        }
                    }
                ]
            }
        }
    )["querySdgMatch"]
