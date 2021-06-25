from pytest import fixture

from flockwave.spec.schema import get_request_body_schema

from .fixtures import create_schema_validator


@fixture(scope="module")
def is_valid():
    return create_schema_validator(get_request_body_schema())


@fixture
def test_empty(is_valid):
    assert not is_valid({})


def test_unknown_type(is_valid):
    assert not is_valid({"type": "NO-SUCH-MESSAGE"})


def test_missing_mandatory_field(is_valid):
    assert not is_valid(
        {
            "type": "CONN-INF",
        }
    )


def test_mandatory_field_with_invalid_type(is_valid):
    assert not is_valid({"type": "CONN-INF", "ids": 1234})
