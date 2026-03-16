"""FastAPI dependencies for JWT authentication and permission checks."""

from __future__ import annotations

from typing import Any, Callable

from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from hexadian_auth_common.context import UserContext
from hexadian_auth_common.errors import (
    AuthenticationError,
    InsufficientPermissionsError,
)
from hexadian_auth_common.jwt import decode_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


class JWTAuthDependency:
    """Callable FastAPI dependency that validates a JWT Bearer token.

    Usage::

        jwt_auth = JWTAuthDependency(secret="my-secret")

        @app.get("/me", dependencies=[Depends(jwt_auth)])
        async def me(user: UserContext = Depends(jwt_auth)):
            return {"user_id": user.user_id}
    """

    def __init__(self, secret: str, algorithm: str = "HS256") -> None:
        self.secret = secret
        self.algorithm = algorithm

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ) -> UserContext:
        if credentials is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        try:
            claims = decode_access_token(
                credentials.credentials, self.secret, self.algorithm
            )
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail=exc.message)
        return UserContext.from_claims(claims)


def require_permission(permission: str) -> Callable[..., Any]:
    """Dependency factory that enforces a single permission.

    Args:
        permission: The permission string the user must have.

    Returns:
        A FastAPI dependency coroutine.
    """

    async def _check(user: UserContext = Depends(_stub_jwt_auth)) -> UserContext:
        if permission not in user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission}",
            )
        return user

    return _check


def require_any_permission(*permissions: str) -> Callable[..., Any]:
    """Dependency factory that passes if the user holds **any** listed permission.

    Args:
        permissions: One or more permission strings (OR logic).

    Returns:
        A FastAPI dependency coroutine.
    """

    async def _check(user: UserContext = Depends(_stub_jwt_auth)) -> UserContext:
        if not any(p in user.permissions for p in permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Missing one of required permissions: {', '.join(permissions)}",
            )
        return user

    return _check


# ---------------------------------------------------------------------------
# Exception handlers — register with ``app.add_exception_handler(...)``
# ---------------------------------------------------------------------------


async def authentication_error_handler(
    _request: Request, exc: AuthenticationError
) -> JSONResponse:
    """Return a ``401`` JSON response for :class:`AuthenticationError`."""
    return JSONResponse(status_code=401, content={"detail": exc.message})


async def insufficient_permissions_error_handler(
    _request: Request, exc: InsufficientPermissionsError
) -> JSONResponse:
    """Return a ``403`` JSON response for :class:`InsufficientPermissionsError`."""
    return JSONResponse(status_code=403, content={"detail": exc.message})


def register_exception_handlers(app: Any) -> None:
    """Register authentication/authorisation exception handlers on a FastAPI app.

    Args:
        app: A :class:`fastapi.FastAPI` application instance.
    """
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(
        InsufficientPermissionsError, insufficient_permissions_error_handler
    )


# Private sentinel used as a default so that ``require_permission`` /
# ``require_any_permission`` can declare a dependency on *some* JWTAuthDependency
# without knowing the concrete secret.  In practice the real dependency will be
# overridden via FastAPI's dependency-override mechanism or by the caller providing
# their own ``JWTAuthDependency`` instance.
async def _stub_jwt_auth() -> UserContext:  # pragma: no cover
    """Placeholder — overridden at runtime."""
    raise RuntimeError(
        "JWTAuthDependency was not injected. "
        "Override '_stub_jwt_auth' via app.dependency_overrides."
    )
