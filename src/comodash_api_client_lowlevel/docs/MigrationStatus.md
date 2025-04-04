# MigrationStatus


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**flash_schema_status** | **str** | Status of the FLASH_SCHEMA process.  | [optional] 
**flash_schema_message** | **str** | Status message of the FLASH_SCHEMA process.  | [optional] 
**full_migration_status** | **str** | Status of the FULL_MIGRATION process.  | 
**full_migration_message** | **str** | Status message of the FULL_MIGRATION process.  | [optional] 

## Example

```python
from comodash_api_client_lowlevel.models.migration_status import MigrationStatus

# TODO update the JSON string below
json = "{}"
# create an instance of MigrationStatus from a JSON string
migration_status_instance = MigrationStatus.from_json(json)
# print the JSON string representation of the object
print MigrationStatus.to_json()

# convert the object into a dict
migration_status_dict = migration_status_instance.to_dict()
# create an instance of MigrationStatus from a dict
migration_status_form_dict = migration_status.from_dict(migration_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


