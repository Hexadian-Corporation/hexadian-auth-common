"""User context dataclass derived from JWT claims."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserContext:
    """Represents an authenticated user extracted from JWT claims."""

    user_id: str
    username: str
    groups: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    rsi_handle: str = ""
    rsi_verified: bool = False

    @classmethod
    def from_claims(cls, claims: dict) -> UserContext:
        """Build a :class:`UserContext` from decoded JWT claims.

        Args:
            claims: Decoded JWT payload dictionary.

        Returns:
            A new ``UserContext`` instance.
        """
        return cls(
            user_id=claims.get("sub", ""),
            username=claims.get("username", ""),
            groups=claims.get("groups", []),
            roles=claims.get("roles", []),
            permissions=claims.get("permissions", []),
            rsi_handle=claims.get("rsi_handle", ""),
            rsi_verified=claims.get("rsi_verified", False),
        )
