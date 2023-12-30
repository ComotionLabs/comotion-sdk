# FileUploadResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**presigned_url** | **object** | Presigned URL data for S3 file upload.  The file can be posted to this endpoint using any AWS s3 compatible toolset.  Temporary credentials are included in the url, so no other credentials are required. | 
**sts_credentials** | **object** | Alternatively to the presigned_url, these Temporary AWS STS credentials that can be used to upload the file to the location specified by &#x60;path&#x60; and &#x60;bucket. | 
**path** | **str** | Path of the file in the S3 bucket.  See description of &#x60;sts_credentials&#x60;. | 
**bucket** | **str** | Name of the S3 bucket.  See description of &#x60;sts_credentials&#x60;. | 

## Example

```python
from comodash_api_client_lowlevel.models.file_upload_response import FileUploadResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FileUploadResponse from a JSON string
file_upload_response_instance = FileUploadResponse.from_json(json)
# print the JSON string representation of the object
print FileUploadResponse.to_json()

# convert the object into a dict
file_upload_response_dict = file_upload_response_instance.to_dict()
# create an instance of FileUploadResponse from a dict
file_upload_response_form_dict = file_upload_response.from_dict(file_upload_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


