# StartExecutionResponse

Result of a start request.  Shared by the 200 and 409 responses, so `started` distinguishes the two outcomes. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** |  | [optional] 
**started** | **bool** | True when a new execution was started, false when one was already running. | [optional] 
**execution_arn** | **str** | ARN of the started execution.  Only set when &#x60;started&#x60; is true. | [optional] 
**start_date** | **str** | ISO 8601 start time of the started execution.  Only set when &#x60;started&#x60; is true. | [optional] 
**execution_name** | **str** | Name of the started execution, or null when one was already running. | [optional] 
**state_machine_arn** | **str** | ARN of the state machine the request targeted. | [optional] 
**running_execution** | [**RunningExecution**](RunningExecution.md) | The execution already in progress.  Only set when &#x60;started&#x60; is false.  | [optional] 

## Example

```python
from comodash_dailyrun_api_client_lowlevel.models.start_execution_response import StartExecutionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StartExecutionResponse from a JSON string
start_execution_response_instance = StartExecutionResponse.from_json(json)
# print the JSON string representation of the object
print(StartExecutionResponse.to_json())

# convert the object into a dict
start_execution_response_dict = start_execution_response_instance.to_dict()
# create an instance of StartExecutionResponse from a dict
start_execution_response_from_dict = StartExecutionResponse.from_dict(start_execution_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


