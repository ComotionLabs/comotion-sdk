# ExecutionStatus

Execution information.  Which fields are populated depends on the `mode` used on the request, so every field is optional. In `list` mode only `executions` is set.  In `latest` and `last_successful` mode the execution fields are set directly on this object, or `message` is set when there is nothing to return. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**executions** | [**List[Execution]**](Execution.md) | Recent executions.  Populated in &#x60;list&#x60; mode. | [optional] 
**name** | **str** | Execution name.  Populated in &#x60;latest&#x60; and &#x60;last_successful&#x60; mode. | [optional] 
**status** | **str** | Execution status.  Populated in &#x60;latest&#x60; and &#x60;last_successful&#x60; mode. | [optional] 
**start_date** | **str** | Execution start time.  Populated in &#x60;latest&#x60; and &#x60;last_successful&#x60; mode. | [optional] 
**stop_date** | **str** | Execution stop time.  Populated in &#x60;latest&#x60; and &#x60;last_successful&#x60; mode. | [optional] 
**message** | **str** | Explanatory message, set in &#x60;last_successful&#x60; mode when there are no successful executions.  | [optional] 

## Example

```python
from comodash_dailyrun_api_client_lowlevel.models.execution_status import ExecutionStatus

# TODO update the JSON string below
json = "{}"
# create an instance of ExecutionStatus from a JSON string
execution_status_instance = ExecutionStatus.from_json(json)
# print the JSON string representation of the object
print(ExecutionStatus.to_json())

# convert the object into a dict
execution_status_dict = execution_status_instance.to_dict()
# create an instance of ExecutionStatus from a dict
execution_status_from_dict = ExecutionStatus.from_dict(execution_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


