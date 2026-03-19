"""Tests for hexadian_auth_common.introspection."""

from __future__ import annotations

import dataclasses
from unittest.mock import MagicMock, patch

import httpx
import pytest

from hexadian_auth_common.introspection import IntrospectionResult, TokenIntrospector

AUTH_SERVICE_URL = "https://auth.example.com"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.test.token"


def _make_response(data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


class TestTokenIntrospectorURLConstruction:
    def test_no_trailing_slash(self) -> None:
        introspector = TokenIntrospector("https://auth.example.com")
        assert introspector._url == "https://auth.example.com/auth/token/introspect"

    def test_with_trailing_slash(self) -> None:
        introspector = TokenIntrospector("https://auth.example.com/")
        assert introspector._url == "https://auth.example.com/auth/token/introspect"

    def test_with_multiple_trailing_slashes(self) -> None:
        introspector = TokenIntrospector("https://auth.example.com///")
        assert introspector._url == "https://auth.example.com/auth/token/introspect"


class TestTokenIntrospectorIntrospect:
    def test_active_token_returns_full_result(self) -> None:
        response_data = {
            "active": True,
            "sub": "user-123",
            "username": "han_solo",
            "groups": ["haulers"],
            "roles": ["member"],
            "permissions": ["cargo:read"],
            "rsi_handle": "HanSolo",
            "rsi_verified": True,
            "exp": 9999999999,
            "iat": 1700000000,
            "is_user_active": True,
        }
        mock_resp = _make_response(response_data)

        with patch("httpx.post", return_value=mock_resp) as mock_post:
            introspector = TokenIntrospector(AUTH_SERVICE_URL)
            result = introspector.introspect(TOKEN)

        mock_post.assert_called_once_with(
            f"{AUTH_SERVICE_URL}/auth/token/introspect",
            json={"token": TOKEN},
            timeout=5.0,
        )
        assert result == IntrospectionResult(
            active=True,
            sub="user-123",
            username="han_solo",
            groups=["haulers"],
            roles=["member"],
            permissions=["cargo:read"],
            rsi_handle="HanSolo",
            rsi_verified=True,
            exp=9999999999,
            iat=1700000000,
            is_user_active=True,
            reason=None,
        )

    def test_inactive_token_returns_active_false(self) -> None:
        response_data = {"active": False}
        mock_resp = _make_response(response_data)

        with patch("httpx.post", return_value=mock_resp):
            introspector = TokenIntrospector(AUTH_SERVICE_URL)
            result = introspector.introspect(TOKEN)

        assert result.active is False
        assert result.sub is None
        assert result.reason is None

    def test_deactivated_user_returns_reason(self) -> None:
        response_data = {
            "active": False,
            "reason": "user_deactivated",
            "is_user_active": False,
        }
        mock_resp = _make_response(response_data)

        with patch("httpx.post", return_value=mock_resp):
            introspector = TokenIntrospector(AUTH_SERVICE_URL)
            result = introspector.introspect(TOKEN)

        assert result.active is False
        assert result.reason == "user_deactivated"
        assert result.is_user_active is False

    def test_http_error_propagates(self) -> None:
        mock_resp = _make_response({}, status_code=500)
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=MagicMock(),
            response=mock_resp,
        )

        with patch("httpx.post", return_value=mock_resp):
            introspector = TokenIntrospector(AUTH_SERVICE_URL)
            with pytest.raises(httpx.HTTPStatusError):
                introspector.introspect(TOKEN)

    def test_network_error_propagates(self) -> None:
        with patch(
            "httpx.post",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            introspector = TokenIntrospector(AUTH_SERVICE_URL)
            with pytest.raises(httpx.ConnectError):
                introspector.introspect(TOKEN)

    def test_default_timeout_is_enforced(self) -> None:
        """Verify that the default timeout of 5.0 seconds is passed to httpx.post."""
        mock_resp = _make_response({"active": False})

        with patch("httpx.post", return_value=mock_resp) as mock_post:
            introspector = TokenIntrospector(AUTH_SERVICE_URL)
            introspector.introspect(TOKEN)

        _, kwargs = mock_post.call_args
        assert kwargs.get("timeout") == 5.0

    def test_custom_timeout_is_respected(self) -> None:
        """Verify that a custom timeout value is passed to httpx.post."""
        mock_resp = _make_response({"active": False})

        with patch("httpx.post", return_value=mock_resp) as mock_post:
            introspector = TokenIntrospector(AUTH_SERVICE_URL, timeout=10.0)
            introspector.introspect(TOKEN)

        _, kwargs = mock_post.call_args
        assert kwargs.get("timeout") == 10.0

    def test_result_is_frozen(self) -> None:
        result = IntrospectionResult(active=True)
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.active = False  # type: ignore[misc]

    def test_optional_fields_default_to_none(self) -> None:
        result = IntrospectionResult(active=True)
        assert result.sub is None
        assert result.username is None
        assert result.groups is None
        assert result.roles is None
        assert result.permissions is None
        assert result.rsi_handle is None
        assert result.rsi_verified is None
        assert result.exp is None
        assert result.iat is None
        assert result.is_user_active is None
        assert result.reason is None
