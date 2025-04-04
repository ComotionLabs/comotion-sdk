# QueryResultResultSetRowsInner


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[QueryResultResultSetRowsInnerDataInner]**](QueryResultResultSetRowsInnerDataInner.md) |  | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.query_result_result_set_rows_inner import QueryResultResultSetRowsInner

# TODO update the JSON string below
json = "{}"
# create an instance of QueryResultResultSetRowsInner from a JSON string
query_result_result_set_rows_inner_instance = QueryResultResultSetRowsInner.from_json(json)
# print the JSON string representation of the object
print QueryResultResultSetRowsInner.to_json()

# convert the object into a dict
query_result_result_set_rows_inner_dict = query_result_result_set_rows_inner_instance.to_dict()
# create an instance of QueryResultResultSetRowsInner from a dict
query_result_result_set_rows_inner_form_dict = query_result_result_set_rows_inner.from_dict(query_result_result_set_rows_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


