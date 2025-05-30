# coding: utf-8

"""
    Comotion Dash API

    Comotion Dash API

    The version of the OpenAPI document: 2.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class Migration(BaseModel):
    """
    Migration
    """ # noqa: E501
    migration_type: StrictStr = Field(description="whether to run a full migration (FULL_MIGRATION) or only copy the schema of the lake across to the new lake (FLASH_SCHEMA) ")
    clear_out_new_lake: Optional[StrictStr] = Field(default='DO_NOT_CLEAR_OUT', description="whether to clear out the new lake on migration. This is useful when testing has taken place, and data needs to be cleared. If this is set to DO_NOT_CLEAR_OUT, the migration will fail if there is data in the new lake. * CLEAR_OUT: Clear out the new lake * DO_NOT_CLEAR_OUT: Fail if there is already data in the new lake defaults to DO_NOT_CLEAR_OUT ")
    __properties: ClassVar[List[str]] = ["migration_type", "clear_out_new_lake"]

    @field_validator('migration_type')
    def migration_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['FULL_MIGRATION', 'FLASH_SCHEMA']):
            raise ValueError("must be one of enum values ('FULL_MIGRATION', 'FLASH_SCHEMA')")
        return value

    @field_validator('clear_out_new_lake')
    def clear_out_new_lake_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['CLEAR_OUT', 'DO_NOT_CLEAR_OUT']):
            raise ValueError("must be one of enum values ('CLEAR_OUT', 'DO_NOT_CLEAR_OUT')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of Migration from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Migration from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "migration_type": obj.get("migration_type"),
            "clear_out_new_lake": obj.get("clear_out_new_lake") if obj.get("clear_out_new_lake") is not None else 'DO_NOT_CLEAR_OUT'
        })
        return _obj


