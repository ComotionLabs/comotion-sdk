# comodash_api_client_lowlevel.LoadsApi

All URIs are relative to *https://training.api.comodash.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**commit_load**](LoadsApi.md#commit_load) | **POST** /load/{load_id}/commit | Commit a load operation
[**create_load**](LoadsApi.md#create_load) | **POST** /load | Create a new load
[**generate_presigned_url_for_file_upload**](LoadsApi.md#generate_presigned_url_for_file_upload) | **POST** /load/{load_id}/file | Generate presigned URL for file upload
[**get_load**](LoadsApi.md#get_load) | **GET** /load/{load_id} | Get load metadata


# **commit_load**
> CommitLoad202Response commit_load(load_id, load_commit)

Commit a load operation

Initiates a commit operation for a given load, identified by the load_id.

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.commit_load202_response import CommitLoad202Response
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
with comodash_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_api_client_lowlevel.LoadsApi(api_client)
    load_id = '20231117085806_355d42f6_0684_4b8f_b274_225bf7237494' # str | Unique identifier for the load operation
    load_commit = comodash_api_client_lowlevel.LoadCommit() # LoadCommit | 

    try:
        # Commit a load operation
        api_response = api_instance.commit_load(load_id, load_commit)
        print("The response of LoadsApi->commit_load:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LoadsApi->commit_load: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **load_id** | **str**| Unique identifier for the load operation | 
 **load_commit** | [**LoadCommit**](LoadCommit.md)|  | 

### Return type

[**CommitLoad202Response**](CommitLoad202Response.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Commit initiated successfully. |  -  |
**400** | Invalid request, such as invalid checksum data. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**5XX** | Internal server error or unhandled exception. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_load**
> LoadId create_load(load)

Create a new load

Creates a new load with the given parameters.

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.load import Load
from comodash_api_client_lowlevel.models.load_id import LoadId
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
with comodash_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_api_client_lowlevel.LoadsApi(api_client)
    load = comodash_api_client_lowlevel.Load() # Load | 

    try:
        # Create a new load
        api_response = api_instance.create_load(load)
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

[**LoadId**](LoadId.md)

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

# **generate_presigned_url_for_file_upload**
> FileUploadResponse generate_presigned_url_for_file_upload(load_id, file_upload_request=file_upload_request)

Generate presigned URL for file upload

Generates a presigned URL and STS credentials for uploading a file to a specified load.

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.file_upload_request import FileUploadRequest
from comodash_api_client_lowlevel.models.file_upload_response import FileUploadResponse
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
with comodash_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_api_client_lowlevel.LoadsApi(api_client)
    load_id = '20231117085806_355d42f6_0684_4b8f_b274_225bf7237494' # str | Unique identifier for the load operation
    file_upload_request = comodash_api_client_lowlevel.FileUploadRequest() # FileUploadRequest | Optional parameters for file upload (optional)

    try:
        # Generate presigned URL for file upload
        api_response = api_instance.generate_presigned_url_for_file_upload(load_id, file_upload_request=file_upload_request)
        print("The response of LoadsApi->generate_presigned_url_for_file_upload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LoadsApi->generate_presigned_url_for_file_upload: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **load_id** | **str**| Unique identifier for the load operation | 
 **file_upload_request** | [**FileUploadRequest**](FileUploadRequest.md)| Optional parameters for file upload | [optional] 

### Return type

[**FileUploadResponse**](FileUploadResponse.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Presigned URL generated successfully. |  -  |
**400** | Invalid request. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**5XX** | Internal server error or unhandled exception. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_load**
> LoadMetaData get_load(load_id)

Get load metadata

Retrieves metadata for a specific load based on the provided load_id.

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.load_meta_data import LoadMetaData
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
with comodash_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_api_client_lowlevel.LoadsApi(api_client)
    load_id = '20231117085806_355d42f6_0684_4b8f_b274_225bf7237494' # str | Unique identifier for the load operation

    try:
        # Get load metadata
        api_response = api_instance.get_load(load_id)
        print("The response of LoadsApi->get_load:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LoadsApi->get_load: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **load_id** | **str**| Unique identifier for the load operation | 

### Return type

[**LoadMetaData**](LoadMetaData.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Load metadata retrieved successfully. |  -  |
**400** | Invalid request. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**5XX** | Internal server error or unhandled exception. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

