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
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class Load(BaseModel):
    """
    Load
    """ # noqa: E501
    load_type: StrictStr = Field(description="Type of the load operation.")
    table_name: Annotated[str, Field(strict=True)] = Field(description="Name of the table.  Only lowercase with underscores.")
    load_as_service_client_id: Optional[StrictStr] = Field(default=None, description="Optional parameter to force the load to act as a certain service_client_id.")
    partitions: Optional[List[StrictStr]] = Field(default=None, description="List of partition names.")
    __properties: ClassVar[List[str]] = ["load_type", "table_name", "load_as_service_client_id", "partitions"]

    @field_validator('load_type')
    def load_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['APPEND_ONLY']):
            raise ValueError("must be one of enum values ('APPEND_ONLY')")
        return value

    @field_validator('table_name')
    def table_name_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[a-z_]+[a-z0-9_]*[a-z0-9]$", value):
            raise ValueError(r"must validate the regular expression /^[a-z_]+[a-z0-9_]*[a-z0-9]$/")
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
        """Create an instance of Load from a JSON string"""
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
        """Create an instance of Load from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "load_type": obj.get("load_type"),
            "table_name": obj.get("table_name"),
            "load_as_service_client_id": obj.get("load_as_service_client_id"),
            "partitions": obj.get("partitions")
        })
        return _obj


