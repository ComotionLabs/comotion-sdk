# DailyRunEnabled


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**daily_run** | **bool** | Whether the scheduled nightly Daily ETL kickoff is enabled. | 

## Example

```python
from comodash_dailyrun_api_client_lowlevel.models.daily_run_enabled import DailyRunEnabled

# TODO update the JSON string below
json = "{}"
# create an instance of DailyRunEnabled from a JSON string
daily_run_enabled_instance = DailyRunEnabled.from_json(json)
# print the JSON string representation of the object
print(DailyRunEnabled.to_json())

# convert the object into a dict
daily_run_enabled_dict = daily_run_enabled_instance.to_dict()
# create an instance of DailyRunEnabled from a dict
daily_run_enabled_from_dict = DailyRunEnabled.from_dict(daily_run_enabled_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


