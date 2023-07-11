from flockwave.spec.schema import (
    get_complex_object_schema,
    get_message_schema,
    get_message_body_schema,
    get_request_body_schema,
    get_response_body_schema,
    get_notification_body_schema,
)
from pytest import mark


def assert_looks_like_a_schema(schema):
    assert isinstance(schema, dict)


def assert_looks_like_an_object_schema(schema):
    assert_looks_like_a_schema(schema)
    assert schema.get("type") == "object"
    assert "properties" in schema


def assert_looks_like_a_top_level_schema(schema):
    assert_looks_like_a_schema(schema)
    assert "$id" in schema
    assert "$schema" in schema


@mark.parametrize(
    "name",
    [
        "beaconBasicProperties",
        "beaconStatusInfo",
        "commandExecutionStatus",
        "connectionInfo",
        "deviceTreeNode",
        "flightLog",
        "flightLogMetadata",
        "logMessage",
        "preflightCheckInfo",
        "preflightCheckItem",
        "transportOptions",
        "uavStatusInfo",
        "weather",
    ],
)
def test_get_complex_schema(name: str):
    # Smoke test only
    schema = get_complex_object_schema(name)
    assert_looks_like_an_object_schema(schema)


def test_get_top_level_schema():
    assert_looks_like_a_top_level_schema(get_message_schema())
    assert_looks_like_a_top_level_schema(get_message_body_schema())
    assert_looks_like_a_top_level_schema(get_notification_body_schema())
    assert_looks_like_a_top_level_schema(get_response_body_schema())
    assert_looks_like_a_top_level_schema(get_request_body_schema())
