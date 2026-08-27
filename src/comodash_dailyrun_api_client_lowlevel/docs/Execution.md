# Execution

A single Daily ETL pipeline execution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Step Functions execution name.  Always starts with &#x60;DailyScheduledETL_{orgName}_&#x60;.  | [optional] 
**status** | **str** | Step Functions execution status, for example RUNNING, SUCCEEDED, FAILED, TIMED_OUT or ABORTED.  Left unconstrained so that new Step Functions statuses do not break deserialisation.  | [optional] 
**start_date** | **str** | ISO 8601 timestamp of when the execution started. | [optional] 
**stop_date** | **str** | ISO 8601 timestamp of when the execution stopped, or null while it is still running.  | [optional] 

## Example

```python
from comodash_dailyrun_api_client_lowlevel.models.execution import Execution

# TODO update the JSON string below
json = "{}"
# create an instance of Execution from a JSON string
execution_instance = Execution.from_json(json)
# print the JSON string representation of the object
print(Execution.to_json())

# convert the object into a dict
execution_dict = execution_instance.to_dict()
# create an instance of Execution from a dict
execution_from_dict = Execution.from_dict(execution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


