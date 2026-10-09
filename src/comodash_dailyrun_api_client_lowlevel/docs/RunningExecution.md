# RunningExecution

The in-flight execution that blocked a manual start.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**start_date** | **str** |  | [optional] 

## Example

```python
from comodash_dailyrun_api_client_lowlevel.models.running_execution import RunningExecution

# TODO update the JSON string below
json = "{}"
# create an instance of RunningExecution from a JSON string
running_execution_instance = RunningExecution.from_json(json)
# print the JSON string representation of the object
print(RunningExecution.to_json())

# convert the object into a dict
running_execution_dict = running_execution_instance.to_dict()
# create an instance of RunningExecution from a dict
running_execution_from_dict = RunningExecution.from_dict(running_execution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


