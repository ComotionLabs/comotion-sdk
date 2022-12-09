# comodash-api-client-lowlevel
Comotion Dash API

The `comodash_api_client_lowlevel` package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 2.0
- Package version: 1.0.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python >= 3.6

## Installation & Usage

This python library package is generated without supporting files like setup.py or requirements files

To be able to use it, you will need these dependencies in your own package that uses this library:

* urllib3 >= 1.25.3
* python-dateutil

## Getting Started

In your own code, to use this library to connect and interact with comodash-api-client-lowlevel,
you can run the following:

```python

import time
import comodash_api_client_lowlevel
from pprint import pprint
from comodash_api import queries_api
from comodash_api_client_lowlevel.model.error import Error
from comodash_api_client_lowlevel.model.query import Query
from comodash_api_client_lowlevel.model.query_id import QueryId
from comodash_api_client_lowlevel.model.query_result import QueryResult
from comodash_api_client_lowlevel.model.query_text import QueryText
# Defining the host is optional and defaults to https://training.api.comodash.io/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = comodash_api_client_lowlevel.Configuration(
    host = "https://training.api.comodash.io/v2"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): OAuth2Authorizer
configuration = comodash_api_client_lowlevel.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)


# Enter a context with an instance of the API client
with comodash_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = queries_api.QueriesApi(api_client)
    query_id = "06ba1d95-8c4f-460c-90b3-bc68fddf2fde" # str | Unique Identifier for the query

    try:
        # Download the csv result file of a query
        api_response = api_instance.download_csv(query_id)
        pprint(api_response)
    except comodash_api_client_lowlevel.ApiException as e:
        print("Exception when calling QueriesApi->download_csv: %s\n" % e)
```

## Documentation for API Endpoints

All URIs are relative to *https://training.api.comodash.io/v2*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*QueriesApi* | [**download_csv**](comodash_api_client_lowlevel/docs/QueriesApi.md#download_csv) | **GET** /query/{query_id}/csv | Download the csv result file of a query
*QueriesApi* | [**get_query**](comodash_api_client_lowlevel/docs/QueriesApi.md#get_query) | **GET** /query/{query_id} | Get information about a query
*QueriesApi* | [**get_query_results**](comodash_api_client_lowlevel/docs/QueriesApi.md#get_query_results) | **GET** /query/{query_id}/result | Get paginated results of a query
*QueriesApi* | [**run_query**](comodash_api_client_lowlevel/docs/QueriesApi.md#run_query) | **POST** /query | Run a query
*QueriesApi* | [**stop_query**](comodash_api_client_lowlevel/docs/QueriesApi.md#stop_query) | **DELETE** /query/{query_id} | Stop a running query


## Documentation For Models

 - [Error](comodash_api_client_lowlevel/docs/Error.md)
 - [Query](comodash_api_client_lowlevel/docs/Query.md)
 - [QueryId](comodash_api_client_lowlevel/docs/QueryId.md)
 - [QueryResult](comodash_api_client_lowlevel/docs/QueryResult.md)
 - [QueryResultResultSet](comodash_api_client_lowlevel/docs/QueryResultResultSet.md)
 - [QueryResultResultSetData](comodash_api_client_lowlevel/docs/QueryResultResultSetData.md)
 - [QueryResultResultSetMetaData](comodash_api_client_lowlevel/docs/QueryResultResultSetMetaData.md)
 - [QueryResultResultSetMetaDataColumnInfo](comodash_api_client_lowlevel/docs/QueryResultResultSetMetaDataColumnInfo.md)
 - [QueryResultResultSetRows](comodash_api_client_lowlevel/docs/QueryResultResultSetRows.md)
 - [QueryStatus](comodash_api_client_lowlevel/docs/QueryStatus.md)
 - [QueryText](comodash_api_client_lowlevel/docs/QueryText.md)


## Documentation For Authorization


## OAuth2Authorizer

- **Type**: Bearer authentication (JWT)


## Author




## Notes for Large OpenAPI documents
If the OpenAPI document is large, imports in comodash_api_client_lowlevel.apis and comodash_api_client_lowlevel.models may fail with a
RecursionError indicating the maximum recursion limit has been exceeded. In that case, there are a couple of solutions:

Solution 1:
Use specific imports for apis and models like:
- `from comodash_api_client_lowlevel.api.default_api import DefaultApi`
- `from comodash_api_client_lowlevel.model.pet import Pet`

Solution 2:
Before importing the package, adjust the maximum recursion limit as shown below:
```
import sys
sys.setrecursionlimit(1500)
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.apis import *
from comodash_api_client_lowlevel.models import *
```
