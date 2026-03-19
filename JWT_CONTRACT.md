# JWT Contract Specification

> **Single source of truth** for the JWT token structure used across all Hexadian auth-common packages.
>
> [`hexadian-auth-common`](https://github.com/Hexadian-Corporation/hexadian-auth-common) (Python) conforms to this contract.

---

## 1. Token Metadata

| Field     | Value                                  | Required | Description                          |
|-----------|----------------------------------------|----------|--------------------------------------|
| Algorithm | `HS256`                                | Yes      | HMAC SHA-256, symmetric shared secret |
| Header    | `{"alg": "HS256", "typ": "JWT"}`       | Yes      | Standard JWT header                  |
| Expiry    | 15 minutes                             | Yes      | Access token TTL                     |

Tokens are signed with a symmetric shared secret using the HMAC SHA-256 algorithm. The issuing auth service (`hexadian-auth-service`) sets the `exp` claim to 15 minutes from issuance.

---

## 2. Claims Schema

```json
{
  "sub": "<user-id>",
  "username": "<username>",
  "groups": ["<group-name>"],
  "roles": ["<role-name>"],
  "permissions": ["<permission-code>"],
  "rsi_handle": "<rsi-handle>",
  "rsi_verified": false,
  "iat": 0,
  "exp": 0
}
```

---

## 3. Claim Details

| Claim          | Type             | Required | Default | Description                              |
|----------------|------------------|----------|---------|------------------------------------------|
| `sub`          | string           | Yes      | —       | User ID (opaque string)                  |
| `username`     | string           | Yes      | —       | Unique username                          |
| `groups`       | string[]         | Yes      | `[]`    | Group names the user belongs to          |
| `roles`        | string[]         | Yes      | `[]`    | Role names resolved from groups          |
| `permissions`  | string[]         | Yes      | `[]`    | Permission codes resolved from roles     |
| `rsi_handle`   | string or null   | No       | `null`  | RSI profile handle                       |
| `rsi_verified` | boolean          | No       | `false` | Whether RSI handle is verified           |
| `iat`          | integer          | Yes      | —       | Issued-at (Unix timestamp, seconds)      |
| `exp`          | integer          | Yes      | —       | Expiration (Unix timestamp, seconds)     |

---

## 4. UserContext Field Mapping

Each auth-common package constructs a `UserContext` object from decoded JWT claims. The table below shows the canonical mapping for each language.

| JWT Claim      | Python field   | PHP property   | Type                   |
|----------------|----------------|----------------|------------------------|
| `sub`          | `user_id`      | `userId`       | string                 |
| `username`     | `username`     | `username`     | string                 |
| `groups`       | `groups`       | `groups`       | list/array of strings  |
| `roles`        | `roles`        | `roles`        | list/array of strings  |
| `permissions`  | `permissions`  | `permissions`  | list/array of strings  |
| `rsi_handle`   | `rsi_handle`   | `rsiHandle`    | string or null         |
| `rsi_verified` | `rsi_verified` | `rsiVerified`  | boolean                |

---

## 5. Validation Rules

These rules are language-agnostic. Every conforming implementation **must** enforce them.

- Signature **MUST** be verified using HS256 with the shared secret.
- `exp` claim **MUST** be checked; expired tokens **MUST** be rejected.
- Missing `sub` or `username` claims **MUST** raise an authentication error.
- `groups`, `roles`, `permissions` default to empty arrays if missing.
- `rsi_handle` defaults to `null` if missing.
- `rsi_verified` defaults to `false` if missing.

---

## 6. Error Behavior

| Scenario                                 | Error Type                    | HTTP Status |
|------------------------------------------|-------------------------------|-------------|
| Missing/malformed token                  | AuthenticationError           | 401         |
| Expired token                            | AuthenticationError           | 401         |
| Invalid signature                        | AuthenticationError           | 401         |
| Token valid but missing required permission | InsufficientPermissionsError | 403         |
