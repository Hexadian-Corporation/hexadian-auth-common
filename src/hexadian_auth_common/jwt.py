"""JWT token decoding and validation."""

from __future__ import annotations

import jwt

from hexadian_auth_common.errors import AuthenticationError


# TODO: Consider PKCE for enhanced security
def decode_access_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> dict:
    """Validate signature, check expiration, and return decoded JWT claims.

    Args:
        token: The encoded JWT string.
        secret: The shared secret used to verify the token signature.
        algorithm: The signing algorithm (default ``HS256``).

    Returns:
        The decoded claims dictionary.

    Raises:
        AuthenticationError: If the token is invalid or expired.
    """
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError(f"Invalid token: {exc}")
