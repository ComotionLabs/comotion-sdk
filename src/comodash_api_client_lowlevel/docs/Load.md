# Load


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**load_type** | **str** | Type of the load operation. | 
**table_name** | **str** | Name of the table.  Only lowercase with underscores. | 
**load_as_service_client_id** | **str** | Optional parameter to force the load to act as a certain service_client_id. | [optional] 
**partitions** | **List[str]** | List of partition names. | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.load import Load

# TODO update the JSON string below
json = "{}"
# create an instance of Load from a JSON string
load_instance = Load.from_json(json)
# print the JSON string representation of the object
print Load.to_json()

# convert the object into a dict
load_dict = load_instance.to_dict()
# create an instance of Load from a dict
load_form_dict = load.from_dict(load_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


