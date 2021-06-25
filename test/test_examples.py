import json
import sys

from pathlib import Path
from pytest import fixture

from flockwave.spec.schema import get_message_body_schema

from .fixtures import create_schema_validator


examples_dir = Path(sys.modules[__name__].__file__).parent.parent / "doc" / "examples"
example_filenames = [x.name for x in examples_dir.glob("*.json")]


@fixture(scope="module")
def is_valid():
    return create_schema_validator(get_message_body_schema(), multi=True)


@fixture(scope="module", params=example_filenames)
def example(request):
    return json.load((examples_dir / request.param).open())


def test_example_is_valid(example, is_valid):
    assert is_valid(example)
