"""Functions related to the validation of messages against the Flockwave
JSON schema.

Requires the ``jsonschema`` and ``referencing`` modules. You can install these
with the ``validation`` extra.
"""

import fastjsonschema

from typing import Any, Callable, cast

from flockwave.spec.schema import Schema

__all__ = ("create_validator_for_schema", "Validator")


Validator = Callable[[Any], None]


def create_validator_for_schema(schema: Schema) -> Validator:
    """Creates a validator for the given JSON schema object."""
    validator = fastjsonschema.compile(schema)
    return cast(Validator, validator)


if __name__ == "__main__":
    # Legacy entry point, one should migrate to flockwave.spec.__main__
    from .cli import validate

    print("/!\\ This entry point is deprecated; use flockwave.spec.cli instead.")
    validate()
