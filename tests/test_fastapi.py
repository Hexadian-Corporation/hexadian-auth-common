"""Tests for hexadian_auth_common.fastapi."""

from __future__ import annotations

import time

import jwt as pyjwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from hexadian_auth_common.context import UserContext
from hexadian_auth_common.errors import (
    AuthenticationError,
    InsufficientPermissionsError,
)
from hexadian_auth_common.fastapi import (
    JWTAuthDependency,
    _stub_jwt_auth,
    register_exception_handlers,
    require_any_permission,
    require_permission,
)

SECRET = "test-secret"


def _make_token(claims: dict) -> str:
    return pyjwt.encode(claims, SECRET, algorithm="HS256")


def _build_app() -> FastAPI:
    """Create a minimal FastAPI app wired with JWTAuthDependency."""
    app = FastAPI()
    jwt_auth = JWTAuthDependency(secret=SECRET)

    # Override the stub so require_permission / require_any_permission work
    app.dependency_overrides[_stub_jwt_auth] = jwt_auth

    register_exception_handlers(app)

    @app.get("/me")
    async def me(user: UserContext = Depends(jwt_auth)):
        return {"user_id": user.user_id, "username": user.username}

    @app.get("/admin")
    async def admin(
        user: UserContext = Depends(require_permission("admin")),
    ):
        return {"user_id": user.user_id}

    @app.get("/editor")
    async def editor(
        user: UserContext = Depends(require_any_permission("edit", "admin")),
    ):
        return {"user_id": user.user_id}

    return app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(_build_app())


class TestJWTAuthDependency:
    def test_valid_token(self, client: TestClient) -> None:
        token = _make_token(
            {
                "sub": "u1",
                "username": "alice",
                "exp": int(time.time()) + 300,
            }
        )
        resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["user_id"] == "u1"

    def test_missing_token(self, client: TestClient) -> None:
        resp = client.get("/me")
        assert resp.status_code == 401

    def test_expired_token(self, client: TestClient) -> None:
        token = _make_token({"sub": "u1", "exp": int(time.time()) - 10})
        resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()

    def test_invalid_token(self, client: TestClient) -> None:
        resp = client.get("/me", headers={"Authorization": "Bearer bad-token"})
        assert resp.status_code == 401


class TestRequirePermission:
    def test_has_permission(self, client: TestClient) -> None:
        token = _make_token(
            {
                "sub": "u1",
                "username": "alice",
                "permissions": ["admin"],
                "exp": int(time.time()) + 300,
            }
        )
        resp = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_missing_permission(self, client: TestClient) -> None:
        token = _make_token(
            {
                "sub": "u1",
                "username": "alice",
                "permissions": ["read"],
                "exp": int(time.time()) + 300,
            }
        )
        resp = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


class TestRequireAnyPermission:
    def test_has_one_of_permissions(self, client: TestClient) -> None:
        token = _make_token(
            {
                "sub": "u1",
                "username": "alice",
                "permissions": ["edit"],
                "exp": int(time.time()) + 300,
            }
        )
        resp = client.get("/editor", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_has_none_of_permissions(self, client: TestClient) -> None:
        token = _make_token(
            {
                "sub": "u1",
                "username": "alice",
                "permissions": ["read"],
                "exp": int(time.time()) + 300,
            }
        )
        resp = client.get("/editor", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


class TestExceptionHandlers:
    def test_authentication_error_handler(self, client: TestClient) -> None:
        app = _build_app()

        @app.get("/raise-auth")
        async def raise_auth():
            raise AuthenticationError("bad token")

        tc = TestClient(app)
        resp = tc.get("/raise-auth")
        assert resp.status_code == 401
        assert resp.json() == {"detail": "bad token"}

    def test_insufficient_permissions_handler(self, client: TestClient) -> None:
        app = _build_app()

        @app.get("/raise-perm")
        async def raise_perm():
            raise InsufficientPermissionsError(required="admin")

        tc = TestClient(app)
        resp = tc.get("/raise-perm")
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Insufficient permissions"}
