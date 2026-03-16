"""Tests for hexadian_auth_common.errors."""

from __future__ import annotations

from hexadian_auth_common.errors import (
    AuthenticationError,
    InsufficientPermissionsError,
)


class TestAuthenticationError:
    def test_default_message(self) -> None:
        exc = AuthenticationError()
        assert str(exc) == "Authentication required"
        assert exc.message == "Authentication required"

    def test_custom_message(self) -> None:
        exc = AuthenticationError("Token expired")
        assert str(exc) == "Token expired"
        assert exc.message == "Token expired"

    def test_is_exception(self) -> None:
        assert issubclass(AuthenticationError, Exception)


class TestInsufficientPermissionsError:
    def test_default_message(self) -> None:
        exc = InsufficientPermissionsError()
        assert str(exc) == "Insufficient permissions"
        assert exc.message == "Insufficient permissions"
        assert exc.required is None

    def test_custom_message_and_required_str(self) -> None:
        exc = InsufficientPermissionsError(required="admin", message="Nope")
        assert str(exc) == "Nope"
        assert exc.required == "admin"

    def test_required_list(self) -> None:
        exc = InsufficientPermissionsError(required=["read", "write"])
        assert exc.required == ["read", "write"]

    def test_is_exception(self) -> None:
        assert issubclass(InsufficientPermissionsError, Exception)
