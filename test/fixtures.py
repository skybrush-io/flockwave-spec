import fastjsonschema

from typing import Any, Callable

from flockwave.spec.schema import Schema
from flockwave.spec.validator import create_validator_for_schema, ValidationError

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
