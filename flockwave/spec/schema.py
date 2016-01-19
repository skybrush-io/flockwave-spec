"""Flockwave protocol JSON schema related functions."""

import json

from memoized import memoized
from jsonpointer import JsonPointer, resolve_pointer
from pkg_resources import resource_stream

__all__ = ("SCHEMA_PACKAGE", "get_message_schema",
           "get_message_body_schema", "get_uav_status_info_schema",
           "ref_resolver")


SCHEMA_PACKAGE = "flockwave.spec"
FLOCKWAVE_SPEC_PREFIX = "http://collmot.com/schemas/flockwave/1.0"


@memoized
def _get_json_object_from_resource(resource_path):
    """Loads a parses a JSON object from the given resource path.

    This function is memoized.

    Arguments:
        resource_path (str): path of the JSON file to load, relative to the
            ``flockwave.spec`` package.

    Returns:
        object: the JSON object from the given resource
    """
    stream = resource_stream(SCHEMA_PACKAGE, resource_path)
    return json.load(stream)


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


def get_message_schema():
    """Returns the JSON schema of Flockwave messages."""
    return _get_schema_from_resource("message.json")


def get_message_body_schema():
    """Returns the JSON schema of Flockwave message bodies."""
    return _get_schema_from_resource("message_body.json")


def get_uav_status_info_schema():
    """Returns the JSON schema of an UAV status information object."""
    return _get_schema_from_resource("definitions.json", "/uavStatusInfo")


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
        stream = resource_stream(SCHEMA_PACKAGE, path)
        return json.load(stream)
    else:
        raise NotImplementedError("remote URI lookups are disallowed")
