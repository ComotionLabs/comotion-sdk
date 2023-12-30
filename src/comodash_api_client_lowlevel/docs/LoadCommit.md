# LoadCommit

Load request body schema

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**check_sum** | **object** | Checksum data for the files to be committed. | 

## Example

```python
from comodash_api_client_lowlevel.models.load_commit import LoadCommit

# TODO update the JSON string below
json = "{}"
# create an instance of LoadCommit from a JSON string
load_commit_instance = LoadCommit.from_json(json)
# print the JSON string representation of the object
print LoadCommit.to_json()

# convert the object into a dict
load_commit_dict = load_commit_instance.to_dict()
# create an instance of LoadCommit from a dict
load_commit_form_dict = load_commit.from_dict(load_commit_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


