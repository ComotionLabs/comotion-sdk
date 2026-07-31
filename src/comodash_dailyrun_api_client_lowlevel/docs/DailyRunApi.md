# comodash_dailyrun_api_client_lowlevel.DailyRunApi

All URIs are relative to *https://api.training.comodash.io/superset*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_daily_run_enabled**](DailyRunApi.md#get_daily_run_enabled) | **GET** /dailyRun/dailyRun_enabled | Get whether the daily run is enabled
[**get_daily_run_execution_status**](DailyRunApi.md#get_daily_run_execution_status) | **GET** /dailyRun/execution_status | Get Daily ETL pipeline execution information
[**start_daily_run_execution**](DailyRunApi.md#start_daily_run_execution) | **POST** /dailyRun/start_execution | Start a Daily ETL pipeline execution
[**update_daily_run_enabled**](DailyRunApi.md#update_daily_run_enabled) | **POST** /dailyRun/dailyRun_enabled | Enable or disable the daily run


# **get_daily_run_enabled**
> DailyRunEnabled get_daily_run_enabled()

Get whether the daily run is enabled

Returns whether the scheduled nightly Daily ETL kickoff is enabled for this organisation.  This flag does not affect manually started runs.


### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):

```python
import comodash_dailyrun_api_client_lowlevel
from comodash_dailyrun_api_client_lowlevel.models.daily_run_enabled import DailyRunEnabled
from comodash_dailyrun_api_client_lowlevel.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.training.comodash.io/superset
# See configuration.py for a list of all supported configuration parameters.
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    host = "https://api.training.comodash.io/superset"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): OAuth2Authorizer
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with comodash_dailyrun_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_dailyrun_api_client_lowlevel.DailyRunApi(api_client)

    try:
        # Get whether the daily run is enabled
        api_response = api_instance.get_daily_run_enabled()
        print("The response of DailyRunApi->get_daily_run_enabled:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DailyRunApi->get_daily_run_enabled: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**DailyRunEnabled**](DailyRunEnabled.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The current daily run setting. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**403** | The token is not entitled to perform this operation. |  -  |
**404** | No daily run setting is recorded against this organisation. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_daily_run_execution_status**
> ExecutionStatus get_daily_run_execution_status(mode=mode, limit=limit)

Get Daily ETL pipeline execution information

Returns information about this organisation's Daily ETL pipeline executions.  The shape of the response depends on the `mode` parameter:
* `list` returns an object with an `executions` array.
* `latest` returns the most recent execution, or a null body when there are none.
* `last_successful` returns the most recent succeeded execution, or an object with only a `message` when there are none.
All three shapes are described by the single `ExecutionStatus` schema, in which every field is optional.


### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):

```python
import comodash_dailyrun_api_client_lowlevel
from comodash_dailyrun_api_client_lowlevel.models.execution_status import ExecutionStatus
from comodash_dailyrun_api_client_lowlevel.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.training.comodash.io/superset
# See configuration.py for a list of all supported configuration parameters.
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    host = "https://api.training.comodash.io/superset"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): OAuth2Authorizer
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with comodash_dailyrun_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_dailyrun_api_client_lowlevel.DailyRunApi(api_client)
    mode = list # str | Which view of the execution history to return. (optional) (default to list)
    limit = 50 # int | Maximum number of executions to consider.  The API clamps this to between 1 and 200 rather than rejecting out of range values, and defaults to 50.  (optional) (default to 50)

    try:
        # Get Daily ETL pipeline execution information
        api_response = api_instance.get_daily_run_execution_status(mode=mode, limit=limit)
        print("The response of DailyRunApi->get_daily_run_execution_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DailyRunApi->get_daily_run_execution_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mode** | **str**| Which view of the execution history to return. | [optional] [default to list]
 **limit** | **int**| Maximum number of executions to consider.  The API clamps this to between 1 and 200 rather than rejecting out of range values, and defaults to 50.  | [optional] [default to 50]

### Return type

[**ExecutionStatus**](ExecutionStatus.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Execution information, in the shape selected by &#x60;mode&#x60;. |  -  |
**400** | The &#x60;mode&#x60; parameter is not one of the supported values. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**403** | The token is not entitled to perform this operation. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_daily_run_execution**
> StartExecutionResponse start_daily_run_execution()

Start a Daily ETL pipeline execution

Starts a new execution of the Daily ETL pipeline for this organisation.
Starting a run this way is not gated by the daily run enabled flag, which only controls the scheduled nightly kickoff.  A run is started unless one is already in progress, in which case the API responds with 409 and a body in which `started` is false and `runningExecution` describes the in-flight run.
The 200 and 409 bodies share the `StartExecutionResponse` schema, so callers can inspect `started` to tell the two outcomes apart.


### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):

```python
import comodash_dailyrun_api_client_lowlevel
from comodash_dailyrun_api_client_lowlevel.models.start_execution_response import StartExecutionResponse
from comodash_dailyrun_api_client_lowlevel.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.training.comodash.io/superset
# See configuration.py for a list of all supported configuration parameters.
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    host = "https://api.training.comodash.io/superset"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): OAuth2Authorizer
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with comodash_dailyrun_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_dailyrun_api_client_lowlevel.DailyRunApi(api_client)

    try:
        # Start a Daily ETL pipeline execution
        api_response = api_instance.start_daily_run_execution()
        print("The response of DailyRunApi->start_daily_run_execution:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DailyRunApi->start_daily_run_execution: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**StartExecutionResponse**](StartExecutionResponse.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A new pipeline execution was started. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**403** | The token is not entitled to perform this operation. |  -  |
**409** | A pipeline run is already in progress for this organisation, so no execution was started.  |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_daily_run_enabled**
> DailyRunEnabled update_daily_run_enabled(daily_run_enabled)

Enable or disable the daily run

Sets whether the scheduled nightly Daily ETL kickoff is enabled for this organisation, and returns the value that was stored.


### Example

* Bearer (JWT) Authentication (OAuth2Authorizer):

```python
import comodash_dailyrun_api_client_lowlevel
from comodash_dailyrun_api_client_lowlevel.models.daily_run_enabled import DailyRunEnabled
from comodash_dailyrun_api_client_lowlevel.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.training.comodash.io/superset
# See configuration.py for a list of all supported configuration parameters.
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    host = "https://api.training.comodash.io/superset"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): OAuth2Authorizer
configuration = comodash_dailyrun_api_client_lowlevel.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with comodash_dailyrun_api_client_lowlevel.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = comodash_dailyrun_api_client_lowlevel.DailyRunApi(api_client)
    daily_run_enabled = comodash_dailyrun_api_client_lowlevel.DailyRunEnabled() # DailyRunEnabled | 

    try:
        # Enable or disable the daily run
        api_response = api_instance.update_daily_run_enabled(daily_run_enabled)
        print("The response of DailyRunApi->update_daily_run_enabled:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DailyRunApi->update_daily_run_enabled: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **daily_run_enabled** | [**DailyRunEnabled**](DailyRunEnabled.md)|  | 

### Return type

[**DailyRunEnabled**](DailyRunEnabled.md)

### Authorization

[OAuth2Authorizer](../README.md#OAuth2Authorizer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The value stored by the API. |  -  |
**400** | The request body is missing or is not a valid boolean setting. |  -  |
**401** | Authorization information is missing or invalid. |  -  |
**403** | The token is not entitled to perform this operation. |  -  |
**5XX** | Unexpected error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

