"""Shared JWT validation, FastAPI auth dependencies, and user context."""

from hexadian_auth_common.context import UserContext
from hexadian_auth_common.errors import (
    AuthenticationError,
    InsufficientPermissionsError,
)
from hexadian_auth_common.jwt import decode_access_token

__all__ = [
    "AuthenticationError",
    "InsufficientPermissionsError",
    "UserContext",
    "decode_access_token",
]
