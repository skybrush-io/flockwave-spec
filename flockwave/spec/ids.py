"""Helper functions to determine whether a given ID used in the Flockwave
protocol is valid.
"""

MAX_UAV_ID_LENGTH = 64


def is_valid_uav_id(identifier):
    """Returns whether the given identifier is a valid UAV ID.

    Parameters:
        identifier (str): the UAV identifier to validate

    Returns:
        bool: whether the identifier is valid
    """
    return (
        len(identifier) >= 1
        and len(identifier) <= MAX_UAV_ID_LENGTH
        and "/" not in identifier
    )


def make_valid_uav_id(identifier):
    """Given an identifier, produces a UAV identifier from it that
    should pass all checks in `is_valid_uav_id`.

    Parameters:
        identifier (str): the identifier to transform

    Returns:
        str: the transformed identifier
    """
    if len(identifier) < 1:
        return "-"
    if len(identifier) > MAX_UAV_ID_LENGTH:
        identifier = identifier[:MAX_UAV_ID_LENGTH]
    return identifier.replace("/", "-")
