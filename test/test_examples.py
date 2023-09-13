import json
import sys

from pathlib import Path
from pytest import fixture

from flockwave.spec.schema import (
    get_response_body_schema,
    get_request_body_schema,
    get_notification_body_schema,
)

from .fixtures import create_schema_validator


this_file = sys.modules[__name__].__file__
assert this_file is not None

examples_dir = Path().parent.parent / "doc" / "examples"
request_filenames = [x.name for x in examples_dir.glob("request_*.json")]
response_filenames = [x.name for x in examples_dir.glob("response_*.json")]
notification_filenames = [x.name for x in examples_dir.glob("notification_*.json")]


@fixture(scope="module")
def is_valid_request():
    return create_schema_validator(get_request_body_schema(), multi=True)


@fixture(scope="module")
def is_valid_response():
    return create_schema_validator(get_response_body_schema(), multi=True)


@fixture(scope="module")
def is_valid_notification():
    return create_schema_validator(get_notification_body_schema(), multi=True)


@fixture(scope="module", params=request_filenames)
def example_request(request):
    return json.load((examples_dir / request.param).open())


@fixture(scope="module", params=response_filenames)
def example_response(request):
    return json.load((examples_dir / request.param).open())


@fixture(scope="module", params=notification_filenames)
def example_notification(request):
    return json.load((examples_dir / request.param).open())


def test_example_request_is_valid(example_request, is_valid_request):
    assert is_valid_request(example_request)


def test_example_response_is_valid(example_response, is_valid_response):
    assert is_valid_response(example_response)


def test_example_notification_is_valid(example_notification, is_valid_notification):
    assert is_valid_notification(example_notification)
