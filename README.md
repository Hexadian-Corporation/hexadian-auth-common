> **© 2026 Hexadian Corporation** — Licensed under [PolyForm Noncommercial 1.0.0 (Modified)](./LICENSE). No commercial use, no public deployment, no plagiarism. See [LICENSE](./LICENSE) for full terms.

# hexadian-auth-common

Shared Python library for JWT validation, FastAPI auth dependencies, and user context for **H³ – Hexadian Hauling Helper** services.

## JWT Contract

This repository hosts [`JWT_CONTRACT.md`](JWT_CONTRACT.md) — the **single source of truth** for the JWT token structure shared across all Hexadian auth-common packages (Python, PHP). It defines the claims schema, `UserContext` field mapping, validation rules, and error behavior that every conforming implementation must follow.

## Related Repositories

| Repo | Purpose |
|------|---------|
| [`hexadian-auth-service`](https://github.com/Hexadian-Corporation/hexadian-auth-service) | Centralized identity platform — issues the JWTs this library validates |
| [`hexadian-auth-common-php`](https://github.com/Hexadian-Corporation/hexadian-auth-common-php) | PHP counterpart — same JWT contract, same `UserContext` fields. For PHP consumers. |

## Stack

- Python 3.11+
- [PyJWT](https://pyjwt.readthedocs.io/) (JWT decoding & validation)
- [FastAPI](https://fastapi.tiangolo.com/) (optional — auth dependencies & exception handlers)
- [hatchling](https://hatch.pypa.io/) (build backend)

## Installation

```bash
# Base (PyJWT only — for JWT decoding without FastAPI)
uv add hexadian-auth-common @ git+https://github.com/Hexadian-Corporation/hexadian-auth-common.git

# With FastAPI extras (includes auth dependencies & exception handlers)
uv add "hexadian-auth-common[fastapi] @ git+https://github.com/Hexadian-Corporation/hexadian-auth-common.git"
```

## Package Exports

### Core (`hexadian_auth_common`)

| Export | Type | Description |
|---|---|---|
| `decode_access_token` | function | Validate signature, check expiration, and return decoded JWT claims |
| `UserContext` | dataclass | Authenticated user context built from JWT claims |
| `AuthenticationError` | exception | Raised when authentication fails (invalid / expired token) |
| `InsufficientPermissionsError` | exception | Raised when the user lacks required permissions |

### FastAPI (`hexadian_auth_common.fastapi`)

| Export | Type | Description |
|---|---|---|
| `JWTAuthDependency` | class | Callable FastAPI dependency that validates a JWT Bearer token |
| `require_permission` | function | Dependency factory that enforces a single permission |
| `require_any_permission` | function | Dependency factory that passes if the user holds **any** listed permission |
| `register_exception_handlers` | function | Register auth exception handlers on a FastAPI app |

## UserContext Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `user_id` | `str` | — | Subject (`sub`) from JWT claims |
| `username` | `str` | — | Username from claims |
| `groups` | `list[str]` | `[]` | Group memberships |
| `roles` | `list[str]` | `[]` | Assigned roles |
| `permissions` | `list[str]` | `[]` | Granted permissions |
| `rsi_handle` | `str` | `""` | RSI (Roberts Space Industries) handle |
| `rsi_verified` | `bool` | `False` | Whether the RSI handle is verified |

## Usage

### Decode a JWT

```python
from hexadian_auth_common import decode_access_token

claims = decode_access_token(token, secret="my-secret")
```

### Build a UserContext from claims

```python
from hexadian_auth_common import UserContext

user = UserContext.from_claims(claims)
print(user.user_id, user.permissions)
```

### Protect FastAPI endpoints

```python
from fastapi import Depends, FastAPI
from hexadian_auth_common.fastapi import (
    JWTAuthDependency,
    register_exception_handlers,
    require_any_permission,
    require_permission,
)

app = FastAPI()
jwt_auth = JWTAuthDependency(secret="my-secret")
register_exception_handlers(app)

@app.get("/me")
async def me(user=Depends(jwt_auth)):
    return {"user_id": user.user_id}

@app.get("/admin")
async def admin(user=Depends(require_permission("admin:read"))):
    return {"ok": True}

@app.get("/editor")
async def editor(user=Depends(require_any_permission("editor:write", "admin:write"))):
    return {"ok": True}
```

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `secret` | — | Shared secret used to verify JWT signatures |
| `algorithm` | `HS256` | JWT signing algorithm passed to PyJWT |

Both `decode_access_token` and `JWTAuthDependency` accept `secret` and `algorithm`.

## Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
uv sync --extra dev --extra fastapi
```

### Test

```bash
uv run pytest --cov
```

### Lint

```bash
uv run ruff check .
```

### Format

```bash
uv run ruff format .
```

## CI

The CI workflow (`.github/workflows/ci.yml`) runs on every pull request to `main`:

| Job | Description |
|---|---|
| **Lint & Format** | Runs `ruff check` and `ruff format --check` |
| **Tests & Coverage** | Runs `pytest` with coverage and enforces ≥90% coverage on changed lines via `diff-cover` |
