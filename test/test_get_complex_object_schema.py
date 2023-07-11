from flockwave.spec.schema import get_complex_object_schema
from pytest import mark


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
    assert isinstance(schema, dict)
    assert schema.get("type") == "object"
    assert "properties" in schema
