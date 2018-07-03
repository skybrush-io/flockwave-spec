"""Flockwave protocol JSON schema related functions."""

import json

from enum import Enum
from memoized import memoized
from jsonpointer import JsonPointer, resolve_pointer
from pkg_resources import resource_stream

__all__ = ("SCHEMA_PACKAGE", "get_message_schema",
           "get_message_body_schema", "get_complex_object_schema",
           "ref_resolver")


SCHEMA_PACKAGE = "flockwave.spec"
FLOCKWAVE_SPEC_PREFIX = "http://collmot.com/schemas/flockwave/1.0"


@memoized
def _get_json_object_from_resource(resource_path):
    """Loads and parses a JSON object from the given resource path.

    This function is memoized.

    Arguments:
        resource_path (str): path of the JSON file to load, relative to the
            ``flockwave.spec`` package.

    Returns:
        object: the JSON object from the given resource
    """
    stream = resource_stream(SCHEMA_PACKAGE, resource_path)
    data = stream.read().decode("utf-8")
    return json.loads(data)


@memoized
def _get_schema_from_resource(resource_path, json_pointer=None):
    """Loads and parses a JSON schema from the given resource path.

    This function is memoized.

    Arguments:
        resource_path (str): path of the JSON file containing the schema
            resource to load, relative to the ``flockwave.spec`` package.
        json_pointer (str or None): JSON pointer to the part of the contents
            of the JSON file that contains the schema we are interested in.
            ``None`` means that the entire JSON file will be returned.

    Returns:
        object: the JSON schema from the given resource
    """
    obj = _get_json_object_from_resource(resource_path)
    if isinstance(json_pointer, JsonPointer):
        obj = json_pointer.get(obj)
    elif json_pointer is not None:
        obj = resolve_pointer(obj, json_pointer)
    return obj


def get_complex_object_schema(name):
    """Returns the JSON schema of a Flockwave complex object from its name.

    Parameters:
        name (str): the name of a Flockwave complex object from the
            specification

    Returns:
        object: the JSON schema for the given Flockwave complex object
    """
    return _get_schema_from_resource("definitions.json", "/" + name)


def get_enum_from_schema(name, class_name=None):
    """Returns a Python enum class from the schema of the given Flockwave
    complex object, assuming that it describes an enum of strings.

    Parameters:
        name (str): the name of a Flockwave complex object from the
            specification
        class_name (str or None): the name of the Python enum class that the
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
        raise TypeError("{0!r} cannot be converted into a Python enum"
                        .format(name))


def get_message_schema():
    """Returns the JSON schema of Flockwave messages."""
    return _get_schema_from_resource("message.json")


def get_message_body_schema():
    """Returns the JSON schema of Flockwave message bodies."""
    return _get_schema_from_resource("message_body.json")


def ref_resolver(uri):
    """Specialized URI resolver for Flockwave's JSON schema files.

    When the URI starts with ``http://collmot.com/schemas/flockwave/1.0``,
    it is assumed that the corresponding JSON file is present in the
    ``flockwave.spec`` package so it is looked up from there. In all
    other cases, we raise an exception. This will be caught by
    ``jsonschema`` and turned into a ``RefResoutionError``.
    """
    if uri.startswith(FLOCKWAVE_SPEC_PREFIX):
        path = uri[len(FLOCKWAVE_SPEC_PREFIX):]
        if path.startswith("/"):
            path = path[1:]
        return _get_json_object_from_resource(path)
    else:
        raise NotImplementedError("remote URI lookups are disallowed")
