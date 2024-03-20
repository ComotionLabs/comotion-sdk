# comodash_api_client_lowlevel.MigrationsApi

All URIs are relative to *https://training.api.comodash.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_migration**](MigrationsApi.md#get_migration) | **GET** /migration | Get status of lake migration
[**start_migration**](MigrationsApi.md#start_migration) | **POST** /migration | Run migration from Lake V1 to Lake V2


# **get_migration**
> MigrationStatus get_migration()

Get status of lake migration

The migration job converts the lake v1 data to lake v2 data.  It can only be run once, after which the old lake will be disabled. Migrations can take a number of hours to complete. So get a cup of coffee. Use the /migration GET endpoint to monitor the progress of the migration 

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.migration_status import MigrationStatus
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
    api_instance = comodash_api_client_lowlevel.MigrationsApi(api_client)

    try:
        # Get status of lake migration
        api_response = api_instance.get_migration()
        print("The response of MigrationsApi->get_migration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MigrationsApi->get_migration: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**MigrationStatus**](MigrationStatus.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Migration started successfully. |  -  |
**400** | Invalid request. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**5XX** | Internal server error or unhandled exception. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_migration**
> str start_migration(migration)

Run migration from Lake V1 to Lake V2

The migration job converts the lake v1 data to lake v2 data.  It can only be run once, after which the old lake will be disabled. Migrations can take a number of hours to complete. So get a cup of coffee. Use the /migration GET endpoint to monitor the progress of the migration 

### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):
```python
import time
import os
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.models.migration import Migration
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
    api_instance = comodash_api_client_lowlevel.MigrationsApi(api_client)
    migration = comodash_api_client_lowlevel.Migration() # Migration | 

    try:
        # Run migration from Lake V1 to Lake V2
        api_response = api_instance.start_migration(migration)
        print("The response of MigrationsApi->start_migration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MigrationsApi->start_migration: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **migration** | [**Migration**](Migration.md)|  | 

### Return type

**str**

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/plain, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Migration started successfully. |  -  |
**400** | Invalid request. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**409** | Migration cannot be started.  There may already be a migration running. |  -  |
**5XX** | Internal server error or unhandled exception. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

