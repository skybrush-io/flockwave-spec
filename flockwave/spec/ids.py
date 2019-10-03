"""Helper functions to determine whether a given ID used in the Flockwave
protocol is valid.
"""

import re

from typing import Tuple

MAX_UAV_ID_LENGTH = 64


def is_valid_uav_id(identifier: str) -> bool:
    """Returns whether the given identifier is a valid UAV ID.

    Parameters:
        identifier: the UAV identifier to validate

    Returns:
        whether the identifier is valid
    """
    return (
        len(identifier) >= 1
        and len(identifier) <= MAX_UAV_ID_LENGTH
        and "/" not in identifier
    )


_user_regex = re.compile(
    r"^(?P<name>[-A-Za-z0-9!#$%&'*+/=?\\^_`{|}~]*)(@(?P<domain>[-A-Za-z0-9!#$%&'*+/=?\\^_`{|}~.]+))?$"
)


def is_valid_user(identifier: str) -> bool:
    """Returns whether the given identifier is a valid username-domain
    pair.

    Parameters:
        identifier: the identifier to validate

    Returns:
        whether the identifier is a valid username-domain pair
    """
    return _user_regex.match(identifier)


def make_valid_uav_id(identifier: str) -> str:
    """Given an identifier, produces a UAV identifier from it that
    should pass all checks in `is_valid_uav_id()`.

    Parameters:
        identifier: the identifier to transform

    Returns:
        the transformed identifier
    """
    if len(identifier) < 1:
        return "-"
    if len(identifier) > MAX_UAV_ID_LENGTH:
        identifier = identifier[:MAX_UAV_ID_LENGTH]
    return identifier.replace("/", "-")


def parse_user(identifier: str) -> Tuple[str, str]:
    """Given an identifier that contains a username-domain pair, returns
    the username and the domain part separately.

    Parameters:
        identifier: the identifier to parse as a user

    Returns:
        the username and the domain part as a tuple

    Raises:
        ValueError: if the username cannot be parsed
    """
    match = _user_regex.match(identifier)
    if not match:
        raise ValueError(f"{repr(identifier)} is not a valid username")
    return match.group("name") or "", match.group("domain") or ""
