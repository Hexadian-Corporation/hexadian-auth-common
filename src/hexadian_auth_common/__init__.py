"""Shared JWT validation, FastAPI auth dependencies, and user context."""

from hexadian_auth_common.context import UserContext
from hexadian_auth_common.errors import (
    AuthenticationError,
    InsufficientPermissionsError,
)
from hexadian_auth_common.introspection import IntrospectionResult, TokenIntrospector
from hexadian_auth_common.jwt import decode_access_token

__all__ = [
    "AuthenticationError",
    "InsufficientPermissionsError",
    "IntrospectionResult",
    "TokenIntrospector",
    "UserContext",
    "decode_access_token",
]
