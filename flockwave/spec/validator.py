"""Command-line schema validator script.

This script checks whether a given JSON file contains a valid Flockwave
message.
"""

import click
import json
import jsonschema
import os
import sys

from flockwave.spec.schema import get_message_body_schema, ref_resolver

__all__ = ("validate", )


SCRIPT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), "..", ".."))


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


@click.command()
@click.argument('name', nargs=-1, type=click.Path(exists=True))
def validate(name):
    """Validates the JSON message stored in the file with the given NAME to see
    if it is a valid Flockwave message. When omitted, the script will validate
    all ``.json`` files found in ``doc/examples``.
    """
    schema = get_message_body_schema()

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
