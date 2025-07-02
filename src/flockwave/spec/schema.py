"""Flockwave protocol JSON schema related functions."""

import json

from enum import Enum
from importlib.resources import open_text
from jsonpointer import JsonPointer, resolve_pointer
from jsonref import replace_refs
from typing import Any, Dict, Optional, Union

from .memoize import memoized

__all__ = (
    "SCHEMA_PACKAGE",
    "get_message_schema",
    "get_message_body_schema",
    "get_notification_body_schema",
    "get_request_body_schema",
    "get_response_body_schema",
    "get_complex_object_schema",
    "Schema",
)


SCHEMA_PACKAGE = "flockwave.spec"
FLOCKWAVE_SPEC_PREFIX = "http://collmot.com/schemas/flockwave/1.0"


Schema = Dict[str, Any]
"""Type alias for schema objects"""


@memoized
def _get_json_object_from_resource(resource_path: str) -> Dict[str, Any]:
    """Loads and parses a JSON object from the given resource path.

    This function is memoized.

    Arguments:
        resource_path: path of the JSON file to load, relative to the
            ``flockwave.spec`` package.

    Returns:
        the JSON object from the given resource
    """
    with open_text(SCHEMA_PACKAGE, resource_path) as fp:
        return json.load(fp)


@memoized
def _get_schema_from_resource(
    resource_path: str,
    json_pointer: Optional[Union[str, JsonPointer]] = None,
) -> Schema:
    """Loads and parses a JSON schema from the given resource path.

    This function is memoized.

    Arguments:
        resource_path: path of the JSON file containing the schema
            resource to load, relative to the ``flockwave.spec`` package.
        json_pointer: JSON pointer to the part of the contents
            of the JSON file that contains the schema we are interested in.
            ``None`` means that the entire JSON file will be returned.
        resolve_refs: whether JSON references should be resolved to the
            files they refer to

    Returns:
        the JSON schema from the given resource
    """
    obj = _get_json_object_from_resource(resource_path)
    obj = replace_refs(
        obj,
        loader=_jsonref_loader,
        jsonschema=True,
        proxies=True,
    )

    if isinstance(json_pointer, JsonPointer):
        obj = json_pointer.get(obj)
    elif json_pointer is not None:
        obj = resolve_pointer(obj, json_pointer)

    # We need to trigger the resolution of '$ref' references. In theory,
    # we could use proxies=False but we were running into problems with that.
    repr(obj)

    return obj  # type: ignore


def get_complex_object_schema(name: str) -> Schema:
    """Returns the JSON schema of a Flockwave complex object from its name.

    Parameters:
        name: the name of a Flockwave complex object from the specification

    Returns:
        object: the JSON schema for the given Flockwave complex object
    """
    return _get_schema_from_resource("definitions.json", "/" + name)


def get_enum_from_schema(name: str, class_name: Optional[str] = None) -> Enum:
    """Returns a Python enum class from the schema of the given Flockwave
    complex object, assuming that it describes an enum of strings.

    Parameters:
        name: the name of a Flockwave complex object from the
            specification
        class_name: the name of the Python enum class that the
            function generates. ``None`` means the name of the Flockwave
            complex object, capitalized.

    Returns:
        Enum: a Python enum class that takes its values from the given
           JSON schema enum

    Throws:
        TypeError: if the given Flockwave complex object is not an enum
    """
    schema = get_complex_object_schema(name)
    if schema.get("type") == "string" and "enum" in schema:
        class_name = class_name or name.capitalize()
        return Enum(class_name, schema["enum"])
    else:
        raise TypeError(f"{name!r} cannot be converted into a Python enum")


def get_message_schema() -> Schema:
    """Returns the JSON schema of Flockwave messages."""
    return _get_schema_from_resource("message.json")


def get_message_body_schema() -> Schema:
    """Returns the JSON schema of Flockwave message bodies."""
    return _get_schema_from_resource("message_body.json")


def get_notification_body_schema() -> Schema:
    """Returns the JSON schema of Flockwave notification bodies."""
    return _get_schema_from_resource("notification_body.json")


def get_response_body_schema() -> Schema:
    """Returns the JSON schema of Flockwave response bodies."""
    return _get_schema_from_resource("response_body.json")


def get_request_body_schema() -> Schema:
    """Returns the JSON schema of Flockwave request bodies."""
    return _get_schema_from_resource("request_body.json")


def _jsonref_loader(uri: str):
    """Specialized URI resolver for Flockwave's JSON schema files.

    When the URI starts with ``http://collmot.com/schemas/flockwave/1.0``,
    it is assumed that the corresponding JSON file is present in the
    ``flockwave.spec`` package so it is looked up from there. In all
    other cases, we raise an exception.
    """
    if uri.startswith(FLOCKWAVE_SPEC_PREFIX):
        path = uri.removeprefix(FLOCKWAVE_SPEC_PREFIX).removeprefix("/")
        return _get_json_object_from_resource(path)
    else:
        raise RuntimeError("remote URI lookups are disallowed")
