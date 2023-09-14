"""Command-line schema validator script.

This script checks whether a given JSON file contains a valid Flockwave
message.
"""

import click
import json
import os
import sys

from jsonschema.exceptions import ValidationError
from pathlib import Path
from typing import Optional, Sequence

from flockwave.spec.schema import get_message_body_schema

from .validator import create_validator_for_schema, Validator


def check_validity(
    filename: str,
    validator: Validator,
    allow_multiple: bool = True,
) -> int:
    """Check the validity of a JSON object found in a file-like object.

    Parameters:
        filename: the file containing the JSON object. Can be
            anything that ``click.open_file()`` can handle, but typically
            it is a string.
        validator: the validator that is called to determine whether the JSON
            object is valid.
        allow_multiple: when ``True`` and the input file contains
            an array, each item of the array will be validated against the
            schema separately. When ``False``, the entire array will be
            validated in such cases.

    Returns:
        int: the number of objects that the input file contained
    """
    with click.open_file(filename, "rb") as fp:
        objs = json.load(fp)

    if not allow_multiple or not isinstance(objs, list):
        objs = [objs]

    for obj in objs:
        validator.validate(obj)

    return len(objs)


@click.command()
@click.argument("name", nargs=-1, type=click.Path(exists=True))
def validate(name: Optional[Sequence[str]] = None) -> None:
    """Validates the JSON message stored in the file with the given NAME to see
    if it is a valid Flockwave message. When omitted, the script will validate
    all ``.json`` files found in ``doc/modules/ROOT/examples``.
    """
    own_path = sys.modules[__name__].__file__
    assert own_path is not None

    SCRIPT_ROOT = Path(own_path).parent.parent.parent.parent.absolute()

    if not name:
        examples_dir = SCRIPT_ROOT / "doc" / "modules" / "ROOT" / "examples"
        name = sorted(
            os.path.join(examples_dir, fname)
            for fname in os.listdir(examples_dir)
            if fname.endswith(".json")
        )
        compact_output = True
    else:
        compact_output = False

    schema = get_message_body_schema()
    validator = create_validator_for_schema(schema)

    for fn in name:
        try:
            num_objs = check_validity(fn, validator)
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
