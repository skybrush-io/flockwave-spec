"""Command-line schema validator script.

This script checks whether a given JSON file contains a valid Flockwave
message.
"""

import click
import json
import jsonschema
import os
import sys

from pkg_resources import resource_stream

__all__ = ("validate", )


SCRIPT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), "..", ".."))

SCHEMA_PACKAGE = "flockwave.spec"
FLOCKWAVE_SPEC_PREFIX = "http://collmot.com/schemas/flockwave/1.0"


def check_validity(filename, schema, resolver=None):
    """Check the validity of a JSON object found in a file-like object.

    Parameters:
        filename (object): the file containing the JSON object. Can be
            anything that ``click.open_file()`` can handle.
        schema (object): the JSON schema to validate the file contents
            against
        resolver (jsonschema.RefResolver or None): custom reference resolver
            for the JSON schema, if needed.
    """
    with click.open_file(filename, "rb") as fp:
        obj = json.load(fp)
    jsonschema.validate(obj, schema, resolver=resolver)


def ref_resolver(uri):
    """Resolves the given URI from a JSON schema file.

    When the URI starts with ``http://collmot.com/schemas/flockwave/1.0``,
    it is assumed that the corresponding JSON file is present in the
    ``flockwave.schema`` package so it is looked up from there. In all
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


@click.command()
@click.argument('name', nargs=-1, type=click.Path(exists=True))
def validate(name):
    """Validates the JSON message stored in the file with the given NAME to see
    if it is a valid Flockwave message. When omitted, the script will validate
    all ``.json`` files found in ``doc/examples``.
    """
    schema_stream = resource_stream(SCHEMA_PACKAGE, "message_body.json")
    schema = json.load(schema_stream)

    # Create a resolver that resolves JSON schema references locally
    resolver = jsonschema.RefResolver.from_schema(
        schema, handlers={"http": ref_resolver})

    if not name:
        examples_dir = os.path.join(SCRIPT_ROOT, "doc", "examples")
        name = [os.path.join(examples_dir, fname)
                for fname in os.listdir(examples_dir)
                if fname.endswith(".json")]

    for fn in name:
        check_validity(fn, schema, resolver)
        click.echo("{0} is a valid Flockwave message.".format(
            click.format_filename(fn)))


if __name__ == "__main__":
    validate()
