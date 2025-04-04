# Migration


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**migration_type** | **str** | whether to run a full migration (FULL_MIGRATION) or only copy the schema of the lake across to the new lake (FLASH_SCHEMA)  | 
**clear_out_new_lake** | **str** | whether to clear out the new lake on migration. This is useful when testing has taken place, and data needs to be cleared. If this is set to DO_NOT_CLEAR_OUT, the migration will fail if there is data in the new lake. * CLEAR_OUT: Clear out the new lake * DO_NOT_CLEAR_OUT: Fail if there is already data in the new lake defaults to DO_NOT_CLEAR_OUT  | [optional] [default to 'DO_NOT_CLEAR_OUT']

## Example

```python
from comodash_api_client_lowlevel.models.migration import Migration

# TODO update the JSON string below
json = "{}"
# create an instance of Migration from a JSON string
migration_instance = Migration.from_json(json)
# print the JSON string representation of the object
print Migration.to_json()

# convert the object into a dict
migration_dict = migration_instance.to_dict()
# create an instance of Migration from a dict
migration_form_dict = migration.from_dict(migration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


