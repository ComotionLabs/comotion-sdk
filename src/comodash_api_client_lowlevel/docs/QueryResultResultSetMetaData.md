# QueryResultResultSetMetaData


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_info** | [**List[QueryResultResultSetMetaDataColumnInfoInner]**](QueryResultResultSetMetaDataColumnInfoInner.md) |  | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.query_result_result_set_meta_data import QueryResultResultSetMetaData

# TODO update the JSON string below
json = "{}"
# create an instance of QueryResultResultSetMetaData from a JSON string
query_result_result_set_meta_data_instance = QueryResultResultSetMetaData.from_json(json)
# print the JSON string representation of the object
print QueryResultResultSetMetaData.to_json()

# convert the object into a dict
query_result_result_set_meta_data_dict = query_result_result_set_meta_data_instance.to_dict()
# create an instance of QueryResultResultSetMetaData from a dict
query_result_result_set_meta_data_form_dict = query_result_result_set_meta_data.from_dict(query_result_result_set_meta_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


