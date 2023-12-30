# LoadMetaDataErrorMessagesInner


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error_type** | **str** | type of error for which the message is shown | [optional] 
**error_message** | **str** | error message | [optional] 
**check_result** | **str** | error state | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.load_meta_data_error_messages_inner import LoadMetaDataErrorMessagesInner

# TODO update the JSON string below
json = "{}"
# create an instance of LoadMetaDataErrorMessagesInner from a JSON string
load_meta_data_error_messages_inner_instance = LoadMetaDataErrorMessagesInner.from_json(json)
# print the JSON string representation of the object
print LoadMetaDataErrorMessagesInner.to_json()

# convert the object into a dict
load_meta_data_error_messages_inner_dict = load_meta_data_error_messages_inner_instance.to_dict()
# create an instance of LoadMetaDataErrorMessagesInner from a dict
load_meta_data_error_messages_inner_form_dict = load_meta_data_error_messages_inner.from_dict(load_meta_data_error_messages_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


