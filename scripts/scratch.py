# -*- coding: utf-8 -*-
"""
=====================================
Created on Wed Jan 11 2023 12:00
@author: Martin Rerabek, martin.rerabek@zhaw.ch
Copyright © 2023, Predictive Analytics Group, ICLS, ZHAW. All rights reserved.
=====================================

"""
# import modules
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
# import settings


_client = Client(
    transport=RequestsHTTPTransport(url=f"http://localhost:8080/graphql"),
    fetch_schema_from_transport=True
)
# data = _client.execute(
#         gql(
#             """
#             query ($batchSize:Int) {
#                 queryInfoObject(first:$batchSize) {
#                     title
#                     abstract
#                     language
#                     keywords{
#                         name
#                     }
#                     sdgs {
#                         id
#                     }
#                 }
#             }
#             """
#         ),
#         variable_values={"batchSize": 10}
#     )['queryInfoObject']

# query for non empty sdgs
data = _client.execute(
        gql(
            """
            query{
                queryInfoObject(filter: {not: { has:sdg_check }})
                {
                    title
                    abstract
                    language
                    keywords{
                        name
                        }
                    sdgs{ 
                        id 
                    }
                    sdg_check

                }
            }
            """
        ))['queryInfoObject']

sdg_match = _client.execute(
        gql(
            """
            query{
                querySdgMatch(filter: { construct: {between: {min: "sdg8_c1_aa", max: "sdg8_c1_zz"}} })
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

# data = _client.execute(
#         gql(
#             """
#             query{
#                 queryInfoObject{
#                     title
#                     abstract
#                     language
#                     keywords{
#                         name
#                         }
#                     sdgs(filter: {id: {eq: null}},){
#                     id}
#                 }
#             }
#             """
#         ))['queryInfoObject']


print('done')

# insert sdg based on link
_client.execute(
    gql(
        """
        mutation updateInfoObject($var: UpdateInfoObjectInput!){
            updateInfoObject(input: $var) {
                infoObject {
                    link 
                    sdgs{
                    id
                    }
                    }
            }
        }
        """
    ),
    variable_values={
        "var": {
            "filter": {"link": {"eq": "https://digitalcollection.zhaw.ch/handle/11475/24961"}},
            # "filter": {"title": {"alloftext": "Modelling"}},
            # "filter": {"year" : {"eq": 2022}},

            "set": {"sdgs": [{"id": "sdg_1"}, {"id": "sdd_2"}]}
            # "set": {"sdgs" : [{"id" : "d"}, {"id": "sd"}]}

            # "remove": {"sdgs": [{"id" : "sdg_1"}, {"id": "sdd_2"}]}

        }
    }
)

def updatePerson(ldapdn, input):
    _client.execute(
        gql(
            """
            mutation updatePerson($personUpdate: UpdatePersonInput!){ 
                updatePerson(input: $personUpdate) {
                    person { LDAPDN }
                }
            }
            """
        ),
        variable_values={"personUpdate": {
            "filter": { "LDAPDN": { "eq": ldapdn } },
            "set": input
        }}
    )



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


def query_keword_matching_InfoObject(keyword):

    return _client.execute(
        gql(
            """
            query infoObject($filter: InfoObjectFilter) {
                queryInfoObject(filter: $filter){
                    title
                    abstract
                    language
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
        variable_values={
            "$filter": {
                    "title": {"alloftext": keyword['keyword']}
            }
        }
    )['queryInfoObject']
