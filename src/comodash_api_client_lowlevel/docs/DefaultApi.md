# comodash_api_client_lowlevel.DefaultApi

All URIs are relative to *https://training.api.comodash.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**commit_load**](DefaultApi.md#commit_load) | **POST** /load/{load_id}/commit | Commit a load operation
[**create_load**](DefaultApi.md#create_load) | **POST** /load | Create a new load


# **commit_load**
> CommitLoad200Response commit_load(load_id, load_commit)

Commit a load operation

Initiates a commit operation for a given load, identified by the load_id.

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.commit_load200_response import CommitLoad200Response
from comodash_api_client_lowlevel.models.load_commit import LoadCommit
from comodash_api_client_lowlevel.rest import ApiException
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
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with comodash_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_api_client_lowlevel.DefaultApi(api_client)
    load_id = '20231117085806_355d42f6_0684_4b8f_b274_225bf7237494' # str | Unique identifier for the load operation
    load_commit = comodash_api_client_lowlevel.LoadCommit() # LoadCommit | 

    try:
        # Commit a load operation
        api_response = await api_instance.commit_load(load_id, load_commit)
        print("The response of DefaultApi->commit_load:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->commit_load: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **load_id** | **str**| Unique identifier for the load operation | 
 **load_commit** | [**LoadCommit**](LoadCommit.md)|  | 

### Return type

[**CommitLoad200Response**](CommitLoad200Response.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Commit initiated successfully. |  -  |
**400** | Invalid request, such as invalid checksum data. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**5XX** | Internal server error or unhandled exception. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_load**
> QueryId create_load(load)

Create a new load

Creates a new load with the given parameters.

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.load import Load
from comodash_api_client_lowlevel.models.query_id import QueryId
from comodash_api_client_lowlevel.rest import ApiException
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
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with comodash_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_api_client_lowlevel.DefaultApi(api_client)
    load = comodash_api_client_lowlevel.Load() # Load | 

    try:
        # Create a new load
        api_response = await api_instance.create_load(load)
        print("The response of DefaultApi->create_load:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_load: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **load** | [**Load**](Load.md)|  | 

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
**202** | Load successfully created |  -  |
**400** | Bad request |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

