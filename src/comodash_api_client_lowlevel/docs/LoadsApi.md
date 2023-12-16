# comodash_api_client_lowlevel.LoadsApi

All URIs are relative to *https://training.api.comodash.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_load**](LoadsApi.md#create_load) | **POST** /load | Create a new load


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
    api_instance = comodash_api_client_lowlevel.LoadsApi(api_client)
    load = comodash_api_client_lowlevel.Load() # Load | 

    try:
        # Create a new load
        api_response = await api_instance.create_load(load)
        print("The response of LoadsApi->create_load:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LoadsApi->create_load: %s\n" % e)
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

