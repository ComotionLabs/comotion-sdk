# LoadMetaData


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**load_status** | **str** | Current status of the load. | 
**error_type** | **str** | Type of error if the load status is FAIL. | [optional] 
**error_messages** | [**List[LoadMetaDataErrorMessagesInner]**](LoadMetaDataErrorMessagesInner.md) | Detailed error messages if the load status is FAIL. | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.load_meta_data import LoadMetaData

# TODO update the JSON string below
json = "{}"
# create an instance of LoadMetaData from a JSON string
load_meta_data_instance = LoadMetaData.from_json(json)
# print the JSON string representation of the object
print LoadMetaData.to_json()

# convert the object into a dict
load_meta_data_dict = load_meta_data_instance.to_dict()
# create an instance of LoadMetaData from a dict
load_meta_data_form_dict = load_meta_data.from_dict(load_meta_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


