"""Functions related to the validation of messages against the Flockwave
JSON schema.

Requires the ``fsatjsonschema`` module. You can install this with the
``validation`` extra.
"""

import fastjsonschema

from typing import Any, Callable

from flockwave.spec.schema import Schema

__all__ = ("create_validator_for_schema", "ValidationError", "Validator")


Validator = Callable[[Any], None]
"""Type specification for validator functions returned by the module."""


class ValidationError(RuntimeError):
    """Exception thrown when an object fails to validate against a JSON schema."""

    pass


def create_validator_for_schema(schema: Schema) -> Validator:
    """Creates a validator for the given JSON schema object."""
    inner_validator: Validator = fastjsonschema.compile(schema)  # type: ignore

    def validator(obj: Any) -> None:
        try:
            inner_validator(obj)
        except fastjsonschema.JsonSchemaValueException as ex:
            raise ValidationError(str(ex)) from None

    return validator
