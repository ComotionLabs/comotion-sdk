# comodash_api_client_lowlevel.QueriesApi

All URIs are relative to *https://training.api.comodash.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**download_csv**](QueriesApi.md#download_csv) | **GET** /query/{query_id}/csv | Download the csv result file of a query
[**get_query**](QueriesApi.md#get_query) | **GET** /query/{query_id} | Get information about a query
[**get_query_results**](QueriesApi.md#get_query_results) | **GET** /query/{query_id}/result | Get paginated results of a query
[**run_query**](QueriesApi.md#run_query) | **POST** /query | Run a query
[**stop_query**](QueriesApi.md#stop_query) | **DELETE** /query/{query_id} | Stop a running query


# **download_csv**
> file_type download_csv(query_id)

Download the csv result file of a query

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import comodash_api_client_lowlevel
from comodash_api import queries_api
from comodash_api_client_lowlevel.model.error import Error
from pprint import pprint
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

    # example passing only required values which don't have defaults set
    try:
        # Download the csv result file of a query
        api_response = api_instance.download_csv(query_id)
        pprint(api_response)
    except comodash_api_client_lowlevel.ApiException as e:
        print("Exception when calling QueriesApi->download_csv: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_id** | **str**| Unique Identifier for the query |

### Return type

**file_type**

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: binary/octet-stream, application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful redirect will result in a 200 from the download endpoint |  -  |
**302** | A redirect to a temporary file download link for the results |  -  |
**400** | Bad request. Query Id of a valid query must be provided. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**404** | A query with the specified ID was not found. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_query**
> Query get_query(query_id)

Get information about a query

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import comodash_api_client_lowlevel
from comodash_api import queries_api
from comodash_api_client_lowlevel.model.error import Error
from comodash_api_client_lowlevel.model.query import Query
from pprint import pprint
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

    # example passing only required values which don't have defaults set
    try:
        # Get information about a query
        api_response = api_instance.get_query(query_id)
        pprint(api_response)
    except comodash_api_client_lowlevel.ApiException as e:
        print("Exception when calling QueriesApi->get_query: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_id** | **str**| Unique Identifier for the query |

### Return type

[**Query**](Query.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Details of query status |  -  |
**400** | Bad request. Query Id of a valid query must be provided. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**404** | A query with the specified ID was not found. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_query_results**
> QueryResult get_query_results(query_id)

Get paginated results of a query

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import comodash_api_client_lowlevel
from comodash_api import queries_api
from comodash_api_client_lowlevel.model.error import Error
from comodash_api_client_lowlevel.model.query_result import QueryResult
from pprint import pprint
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
    next_token = "ASevTwsuuWcDHMZcOF7qV32rDnXKzAI1renA2ZVPdqd2Em2scsyxFLuFiFi+ra/nF5Sw+ME8nj6Hs1G9JRC8fKaLy3913htbKw==" # str | token to get next page of query results.  Will be supplied in the response of the previous call if the result set is truncated. (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get paginated results of a query
        api_response = api_instance.get_query_results(query_id)
        pprint(api_response)
    except comodash_api_client_lowlevel.ApiException as e:
        print("Exception when calling QueriesApi->get_query_results: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get paginated results of a query
        api_response = api_instance.get_query_results(query_id, next_token=next_token)
        pprint(api_response)
    except comodash_api_client_lowlevel.ApiException as e:
        print("Exception when calling QueriesApi->get_query_results: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_id** | **str**| Unique Identifier for the query |
 **next_token** | **str**| token to get next page of query results.  Will be supplied in the response of the previous call if the result set is truncated. | [optional]

### Return type

[**QueryResult**](QueryResult.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query results page |  -  |
**400** | Bad request. Query Id of a valid query must be provided. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**404** | A query with the specified ID was not found. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **run_query**
> QueryId run_query(query_text)

Run a query

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel import queries_api
from comodash_api_client_lowlevel.model.query_id import QueryId
from comodash_api_client_lowlevel.model.error import Error
from comodash_api_client_lowlevel.model.query_text import QueryText
from pprint import pprint
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
    query_text = QueryText(
        query="select 'hello' --should not be multiline",
    ) # QueryText |

    # example passing only required values which don't have defaults set
    try:
        # Run a query
        api_response = api_instance.run_query(query_text)
        pprint(api_response)
    except comodash_api_client_lowlevel.ApiException as e:
        print("Exception when calling QueriesApi->run_query: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_text** | [**QueryText**](QueryText.md)|  |

### Return type

[**QueryId**](QueryId.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Query successfully started |  -  |
**400** | Bad request. Problem with query string. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**500** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stop_query**
> stop_query(query_id)

Stop a running query

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import comodash_api_client_lowlevel
from comodash_api import queries_api
from comodash_api_client_lowlevel.model.error import Error
from pprint import pprint
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

    # example passing only required values which don't have defaults set
    try:
        # Stop a running query
        api_instance.stop_query(query_id)
    except comodash_api_client_lowlevel.ApiException as e:
        print("Exception when calling QueriesApi->stop_query: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_id** | **str**| Unique Identifier for the query |

### Return type

void (empty response body)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully stopped query |  -  |
**400** | Bad request. Query Id of a valid query must be provided. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**404** | A query with the specified ID was not found. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

