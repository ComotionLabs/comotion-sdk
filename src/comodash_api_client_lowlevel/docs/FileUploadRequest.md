# FileUploadRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_key** | **str** | Optional custom key for the file. This will ensure idempontence.  If multiple files are uploaded to the same load with the same file_key, only the last one will be loaded. Must be lowercase, can include underscores, and must end with &#39;.parquet&#39;. | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.file_upload_request import FileUploadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FileUploadRequest from a JSON string
file_upload_request_instance = FileUploadRequest.from_json(json)
# print the JSON string representation of the object
print FileUploadRequest.to_json()

# convert the object into a dict
file_upload_request_dict = file_upload_request_instance.to_dict()
# create an instance of FileUploadRequest from a dict
file_upload_request_form_dict = file_upload_request.from_dict(file_upload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


