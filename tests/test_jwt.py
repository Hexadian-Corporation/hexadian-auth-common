"""Tests for hexadian_auth_common.jwt."""

from __future__ import annotations

import time

import jwt as pyjwt
import pytest

from hexadian_auth_common.errors import AuthenticationError
from hexadian_auth_common.jwt import decode_access_token

SECRET = "test-secret"


def _make_token(claims: dict, secret: str = SECRET, algorithm: str = "HS256") -> str:
    return pyjwt.encode(claims, secret, algorithm=algorithm)


class TestDecodeAccessToken:
    def test_valid_token(self) -> None:
        claims = {"sub": "user-1", "username": "alice", "exp": int(time.time()) + 300}
        token = _make_token(claims)
        decoded = decode_access_token(token, SECRET)
        assert decoded["sub"] == "user-1"
        assert decoded["username"] == "alice"

    def test_expired_token_raises(self) -> None:
        claims = {"sub": "user-1", "exp": int(time.time()) - 10}
        token = _make_token(claims)
        with pytest.raises(AuthenticationError, match="Token has expired"):
            decode_access_token(token, SECRET)

    def test_invalid_signature_raises(self) -> None:
        claims = {"sub": "user-1", "exp": int(time.time()) + 300}
        token = _make_token(claims, secret="wrong-secret")
        with pytest.raises(AuthenticationError, match="Invalid token"):
            decode_access_token(token, SECRET)

    def test_malformed_token_raises(self) -> None:
        with pytest.raises(AuthenticationError, match="Invalid token"):
            decode_access_token("not-a-jwt", SECRET)

    def test_custom_algorithm(self) -> None:
        claims = {"sub": "user-1", "exp": int(time.time()) + 300}
        token = _make_token(claims, algorithm="HS384")
        decoded = decode_access_token(token, SECRET, algorithm="HS384")
        assert decoded["sub"] == "user-1"

    def test_extra_claims_preserved(self) -> None:
        claims = {
            "sub": "user-1",
            "permissions": ["read", "write"],
            "exp": int(time.time()) + 300,
        }
        token = _make_token(claims)
        decoded = decode_access_token(token, SECRET)
        assert decoded["permissions"] == ["read", "write"]
