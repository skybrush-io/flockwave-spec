"""Functions related to the validation of messages against the Flockwave
JSON schema.

Requires the ``jsonschema`` and ``referencing`` modules. You can install these
with the ``validation`` extra.
"""

from functools import lru_cache
from jsonschema.protocols import Validator
from jsonschema.validators import validator_for
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource
from referencing.jsonschema import DRAFT7, ObjectSchema
from typing import Optional

from flockwave.spec.schema import (
    FLOCKWAVE_SPEC_PREFIX,
    _get_json_object_from_resource,
    Schema,
)

__all__ = ("create_validator_for_schema", "Validator")


@lru_cache
def _get_reference_resolver_registry() -> Registry[ObjectSchema]:
    """Returns a reference resolver registry that resolves URIs starting with
    ``http://collmot.com/schemas/flockwave/1.0`` to local JSON files and
    rejects all other external URIs.
    """
    return Registry(retrieve=_retrieve_resource)


def _retrieve_resource(uri: str) -> Resource:
    """Specialized URI retriever for Flockwave's JSON schema files using the
    new Registry-based method in the ``referencing`` library.

    Should not be called directly.

    When the URI starts with ``http://collmot.com/schemas/flockwave/1.0``,
    it is assumed that the corresponding JSON file is present in the
    ``flockwave.spec`` package so it is looked up from there.

    Raises:
        NoSuchResource: when the URI does not start with the prefix mentioned
            above
    """
    if uri.startswith(FLOCKWAVE_SPEC_PREFIX):
        path = uri.removeprefix(FLOCKWAVE_SPEC_PREFIX).removeprefix("/")
        return Resource.from_contents(
            _get_json_object_from_resource(path), default_specification=DRAFT7
        )  # type: ignore
    else:
        raise NoSuchResource(ref=uri)


def create_validator_for_schema(
    schema: Schema, *, registry: Optional[Registry] = None
) -> Validator:
    """Creates a validator for the given JSON schema object."""
    validator_cls = validator_for(schema)
    registry = registry or _get_reference_resolver_registry()

    # registry=... keyword argument is important here, otherwise it would be
    # interpreted as an old-style RefResolver that is deprecated from
    # jsonschema >= 4.18.0
    return validator_cls(schema, registry=registry)


if __name__ == "__main__":
    # Legacy entry point, one should migrate to flockwave.spec.__main__
    from .cli import validate

    print("/!\\ This entry point is deprecated; use flockwave.spec.cli instead.")
    validate()
