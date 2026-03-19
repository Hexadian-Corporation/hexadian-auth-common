"""Token introspection HTTP client for the auth service."""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class IntrospectionResult:
    """Result of a token introspection call."""

    active: bool
    sub: str | None = None
    username: str | None = None
    groups: list[str] | None = None
    roles: list[str] | None = None
    permissions: list[str] | None = None
    rsi_handle: str | None = None
    rsi_verified: bool | None = None
    exp: int | None = None
    iat: int | None = None
    is_user_active: bool | None = None
    reason: str | None = None


class TokenIntrospector:
    """HTTP client for the auth service token introspection endpoint."""

    def __init__(self, auth_service_url: str, timeout: float = 5.0) -> None:
        self._url = f"{auth_service_url.rstrip('/')}/auth/token/introspect"
        self._timeout = timeout

    def introspect(self, token: str) -> IntrospectionResult:
        """Call POST /auth/token/introspect and return a typed result.

        Args:
            token: The JWT access token to introspect.

        Returns:
            IntrospectionResult with active=True and full claims, or
            active=False with optional reason.

        Raises:
            httpx.HTTPError: On network/connection failure.
        """
        response = httpx.post(self._url, json={"token": token}, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        return IntrospectionResult(
            active=data["active"],
            sub=data.get("sub"),
            username=data.get("username"),
            groups=data.get("groups"),
            roles=data.get("roles"),
            permissions=data.get("permissions"),
            rsi_handle=data.get("rsi_handle"),
            rsi_verified=data.get("rsi_verified"),
            exp=data.get("exp"),
            iat=data.get("iat"),
            is_user_active=data.get("is_user_active"),
            reason=data.get("reason"),
        )
