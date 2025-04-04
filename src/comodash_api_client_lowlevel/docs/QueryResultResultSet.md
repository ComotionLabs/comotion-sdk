# QueryResultResultSet


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rows** | [**List[QueryResultResultSetRowsInner]**](QueryResultResultSetRowsInner.md) |  | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.query_result_result_set import QueryResultResultSet

# TODO update the JSON string below
json = "{}"
# create an instance of QueryResultResultSet from a JSON string
query_result_result_set_instance = QueryResultResultSet.from_json(json)
# print the JSON string representation of the object
print QueryResultResultSet.to_json()

# convert the object into a dict
query_result_result_set_dict = query_result_result_set_instance.to_dict()
# create an instance of QueryResultResultSet from a dict
query_result_result_set_form_dict = query_result_result_set.from_dict(query_result_result_set_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


