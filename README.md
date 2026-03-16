# hexadian-auth-common

Shared JWT validation, FastAPI auth dependencies, and user context for Hexadian services.

## Installation

```bash
# Base (PyJWT only)
uv add hexadian-auth-common @ git+https://github.com/Hexadian-Corporation/hexadian-auth-common.git

# With FastAPI extras
uv add hexadian-auth-common[fastapi] @ git+https://github.com/Hexadian-Corporation/hexadian-auth-common.git
```

## Usage

### Decode a JWT

```python
from hexadian_auth_common import decode_access_token

claims = decode_access_token(token, secret="shared-secret")
```

### UserContext from claims

```python
from hexadian_auth_common import UserContext

user = UserContext.from_claims(claims)
print(user.user_id, user.permissions)
```

### FastAPI dependencies

```python
from fastapi import Depends, FastAPI
from hexadian_auth_common.fastapi import (
    JWTAuthDependency,
    register_exception_handlers,
    require_permission,
)

app = FastAPI()
jwt_auth = JWTAuthDependency(secret="shared-secret")
register_exception_handlers(app)

@app.get("/me")
async def me(user=Depends(jwt_auth)):
    return {"user_id": user.user_id}

@app.get("/admin")
async def admin(user=Depends(require_permission("admin"))):
    return {"ok": True}
```

## Development

```bash
pip install -e ".[fastapi,dev]"
ruff check src/ tests/
pytest --cov
```
