"""Tests for hexadian_auth_common.context."""

from __future__ import annotations

import pytest

from hexadian_auth_common.context import UserContext


class TestUserContext:
    def test_from_claims_full(self) -> None:
        claims = {
            "sub": "user-42",
            "username": "bob",
            "groups": ["alpha"],
            "roles": ["admin"],
            "permissions": ["read", "write"],
            "rsi_handle": "BobInSpace",
            "rsi_verified": True,
        }
        ctx = UserContext.from_claims(claims)
        assert ctx.user_id == "user-42"
        assert ctx.username == "bob"
        assert ctx.groups == ["alpha"]
        assert ctx.roles == ["admin"]
        assert ctx.permissions == ["read", "write"]
        assert ctx.rsi_handle == "BobInSpace"
        assert ctx.rsi_verified is True

    def test_from_claims_defaults(self) -> None:
        ctx = UserContext.from_claims({})
        assert ctx.user_id == ""
        assert ctx.username == ""
        assert ctx.groups == []
        assert ctx.roles == []
        assert ctx.permissions == []
        assert ctx.rsi_handle == ""
        assert ctx.rsi_verified is False

    def test_from_claims_partial(self) -> None:
        claims = {"sub": "u1", "username": "alice"}
        ctx = UserContext.from_claims(claims)
        assert ctx.user_id == "u1"
        assert ctx.username == "alice"
        assert ctx.groups == []

    def test_frozen(self) -> None:
        ctx = UserContext(user_id="u1", username="alice")
        with pytest.raises(AttributeError):
            ctx.user_id = "u2"  # type: ignore[misc]
