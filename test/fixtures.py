from collections.abc import Callable
from typing import Any

from flockwave.spec.schema import Schema
from flockwave.spec.validator import ValidationError, create_validator_for_schema

__all__ = ("create_schema_validator",)


def create_schema_validator(
    schema: Schema, multi: bool = False
) -> Callable[[Any], bool]:
    validator = create_validator_for_schema(schema)

    def validator_func(obj: Any) -> bool:
        if multi and isinstance(obj, list):
            return all(validator_func(item) for item in obj)
        else:
            try:
                validator(obj)
                return True
            except ValidationError:
                return False

    return validator_func
