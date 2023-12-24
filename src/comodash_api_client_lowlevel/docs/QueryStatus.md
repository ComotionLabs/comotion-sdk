# QueryStatus


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state** | **str** |  | [optional] 
**state_change_reason** | **str** |  | [optional] 
**submission_date_time** | **str** |  | [optional] 
**completion_date_time** | **str** |  | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.query_status import QueryStatus

# TODO update the JSON string below
json = "{}"
# create an instance of QueryStatus from a JSON string
query_status_instance = QueryStatus.from_json(json)
# print the JSON string representation of the object
print QueryStatus.to_json()

# convert the object into a dict
query_status_dict = query_status_instance.to_dict()
# create an instance of QueryStatus from a dict
query_status_form_dict = query_status.from_dict(query_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


