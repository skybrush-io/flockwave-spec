"""Flockwave protocol JSON schema related functions."""

import json

from memoized import memoized
from pkg_resources import resource_stream

__all__ = ("SCHEMA_PACKAGE", "get_message_schema",
           "get_message_body_schema", "ref_resolver")


SCHEMA_PACKAGE = "flockwave.spec"
FLOCKWAVE_SPEC_PREFIX = "http://collmot.com/schemas/flockwave/1.0"


@memoized
def _get_schema_from_resource(resource_path):
    """Loads and parses a JSON schema from the given resource path.

    This function is memoized.

    Arguments:
        resource_path (str): path of the JSON schema resource to load,
            relative to the ``flockwave.spec`` package.

    Returns:
        object: the JSON schema from the given resource
    """
    stream = resource_stream(SCHEMA_PACKAGE, resource_path)
    return json.load(stream)


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
        stream = resource_stream(SCHEMA_PACKAGE, path)
        return json.load(stream)
    else:
        raise NotImplementedError("remote URI lookups are disallowed")
