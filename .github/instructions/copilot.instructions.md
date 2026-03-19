<critical>Note: This is a living document and will be updated as we refine our processes. Always refer back to this for the latest guidelines. Update whenever necessary.</critical>

<critical>**Development Workflow:** All changes go through a branch + PR — no direct commits to `main` unless explicitly instructed. See `.github/instructions/development-workflow.instructions.md`.</critical>

# Copilot Instructions — hexadian-auth-common

## Project Context

**H³ (Hexadian Hauling Helper)** is a Star Citizen companion app for managing hauling contracts, owned by **Hexadian Corporation** (GitHub org: `Hexadian-Corporation`).

This package is a **shared Python library** for JWT validation and FastAPI auth dependencies, used by all H³ backend services.

- **Repo:** `Hexadian-Corporation/hexadian-auth-common`
- **Type:** Pure library — no FastAPI app, no MongoDB, no domain models
- **Stack:** Python · PyJWT (base dependency) · FastAPI (optional peer dependency)

## Related Repositories

| Repo | Purpose |
|------|---------|
| [`hexadian-auth-service`](https://github.com/Hexadian-Corporation/hexadian-auth-service) | Centralized identity platform — issues the JWTs this library validates. Token architecture, RBAC, auth code flow. |

## Package Structure

```
src/hexadian_auth_common/
├── __init__.py       # Re-exports: decode_access_token, UserContext, AuthenticationError, InsufficientPermissionsError
├── jwt.py            # JWT decoding and validation (decode_access_token)
├── context.py        # UserContext frozen dataclass built from JWT claims
├── fastapi.py        # FastAPI dependencies: JWTAuthDependency, require_permission, require_any_permission, register_exception_handlers
└── errors.py         # AuthenticationError, InsufficientPermissionsError
```

## Key Exports

### Top-level (`hexadian_auth_common`)

| Export | Module | Description |
|--------|--------|-------------|
| `decode_access_token` | `jwt.py` | Validate signature, check expiration, return decoded JWT claims |
| `UserContext` | `context.py` | Frozen dataclass representing an authenticated user (`user_id`, `username`, `groups`, `roles`, `permissions`, `rsi_handle`, `rsi_verified`) |
| `AuthenticationError` | `errors.py` | Raised when authentication fails (invalid / expired token) |
| `InsufficientPermissionsError` | `errors.py` | Raised when the user lacks required permissions |

### FastAPI extras (`hexadian_auth_common.fastapi`)

| Export | Description |
|--------|-------------|
| `JWTAuthDependency` | Callable FastAPI dependency that validates a JWT Bearer token and returns `UserContext` |
| `require_permission(permission)` | Dependency factory enforcing a single permission |
| `require_any_permission(*permissions)` | Dependency factory passing if the user holds **any** listed permission (OR logic) |
| `register_exception_handlers(app)` | Register `AuthenticationError` → 401 and `InsufficientPermissionsError` → 403 handlers on a FastAPI app |

## Design Constraints

- **Pure library** — no FastAPI app, no MongoDB, no domain models
- Zero runtime dependencies beyond **PyJWT** (base) and **FastAPI** (optional extra)
- Build system: **hatchling** with src layout (`src/hexadian_auth_common/`)
- Domain models are **frozen dataclasses** — no Pydantic, no ORM
- `UserContext.from_claims(claims)` is the canonical way to build a user context from JWT claims

## Installation

```bash
# Base (PyJWT only)
uv add hexadian-auth-common @ git+https://github.com/Hexadian-Corporation/hexadian-auth-common.git

# With FastAPI extras
uv add hexadian-auth-common[fastapi] @ git+https://github.com/Hexadian-Corporation/hexadian-auth-common.git
```

## Issue & PR Title Format

**Format:** `<type>(auth-common): description`

- Example: `feat(auth-common): add decode_access_token function`
- Example: `fix(auth-common): handle expired token edge case`

**Allowed types:** `chore`, `fix`, `ci`, `docs`, `feat`, `refactor`, `test`, `build`, `perf`, `style`, `revert`

The issue title and PR title must be **identical**. PR body must include `Fixes #N`.

## Quality Standards

- `ruff check .` + `ruff format --check .` must pass
- `pytest --cov=hexadian_auth_common` with ≥90% coverage on changed lines (`diff-cover`)
- Type hints on all functions
- Squash merge only — PR title becomes the commit message

## CI & Branch Protection

**Required status checks** (all with `app_id: 15368` — GitHub Actions):

| Check | What it does |
|-------|--------------|
| `Lint & Format` | `ruff check .` + `ruff format --check .` |
| `Tests & Coverage` | `pytest` + `diff-cover` (≥90 % on changed lines) |
| `Validate PR Title` | Conventional-commit format |
| `Secret Scan` | Gitleaks |

> **Critical:** Required status checks must always use `app_id: 15368` (GitHub Actions). Using `app_id: null` causes checks to freeze as "Expected — Waiting for status" for any check name not previously reported on `main`. See BUG-011.

## Tooling

| Action | Command |
|--------|---------|
| Setup | `uv sync --extra dev --extra fastapi` |
| Test | `uv run pytest` |
| Test with coverage | `uv run pytest --cov=hexadian_auth_common --cov-report=xml --cov-report=term-missing` |
| Diff coverage | `uv run diff-cover coverage.xml --compare-branch=origin/main --fail-under=90` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |

## Maintenance Rules

- **Keep the README up to date.** When you add, remove, or change exports, installation instructions, or usage examples — update `README.md`. The README is the source of truth for developers.

## Organization Profile Maintenance

- **Keep the org profile README up to date.** When repositories, ports, architecture, workflows, security policy, or ownership change, update Hexadian-Corporation/.github/profile/README.md in the public .github repo.
- **Treat the org profile as canonical org summary.** Ensure descriptions in this repo remain consistent with the organization profile README.

Remember, before finishing: resolve any merge conflict and merge source (PR origin and destination) branch into current one.