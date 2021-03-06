"""Command-line schema validator script.

This script checks whether a given JSON file contains a valid Flockwave
message.
"""

import click
import json
import jsonschema
import os
import sys

from jsonschema.exceptions import ValidationError
from typing import Optional, Sequence

from flockwave.spec.schema import get_message_body_schema, ref_resolver, Schema

__all__ = ("validate",)


SCRIPT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(sys.modules[__name__].__file__), "..", "..", "..")
)


def check_validity(
    filename: str,
    schema: Schema,
    resolver: Optional[jsonschema.RefResolver] = None,
    allow_multiple: bool = True,
) -> int:
    """Check the validity of a JSON object found in a file-like object.

    Parameters:
        allow_multiple (bool): when ``True`` and the input file contains
            an array, each item of the array will be validated against the
            schema separately. When ``False``, the entire array will be
            validated in such cases.
        filename (object): the file containing the JSON object. Can be
            anything that ``click.open_file()`` can handle.
        schema (object): the JSON schema to validate the file contents
            against
        resolver (jsonschema.RefResolver or None): custom reference resolver
            for the JSON schema, if needed.

    Returns:
        int: the number of objects that the input file contained
    """
    with click.open_file(filename, "rb") as fp:
        objs = json.load(fp)

    if not allow_multiple or not isinstance(objs, list):
        objs = [objs]

    for obj in objs:
        jsonschema.validate(obj, schema, resolver=resolver)

    return len(objs)


@click.command()
@click.argument("name", nargs=-1, type=click.Path(exists=True))
def validate(name: Optional[Sequence[str]]) -> None:
    """Validates the JSON message stored in the file with the given NAME to see
    if it is a valid Flockwave message. When omitted, the script will validate
    all ``.json`` files found in ``doc/examples``.
    """
    schema = get_message_body_schema()

    # Create a resolver that resolves JSON schema references locally
    resolver = jsonschema.RefResolver.from_schema(
        schema, handlers={"http": ref_resolver}
    )

    if not name:
        examples_dir = os.path.join(SCRIPT_ROOT, "doc", "examples")
        name = sorted(
            os.path.join(examples_dir, fname)
            for fname in os.listdir(examples_dir)
            if fname.endswith(".json")
        )
        compact_output = True
    else:
        compact_output = False

    for fn in name:
        try:
            num_objs = check_validity(fn, schema, resolver)
        except ValidationError:
            fn = click.format_filename(fn)
            click.echo("{0} is not a valid Flockwave message.".format(fn))
            click.echo("")
            raise

        if not compact_output:
            fn = click.format_filename(fn)
            if num_objs == 1:
                click.echo("{0} is a valid Flockwave message.".format(fn))
            elif num_objs > 1:
                click.echo("{0} contains valid Flockwave messages.".format(fn))
            else:
                click.echo("{0} contains no objects at all.".format(fn))

    if compact_output:
        click.echo("All tested messages were valid.")


if __name__ == "__main__":
    validate()
