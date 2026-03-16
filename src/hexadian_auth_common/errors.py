"""Authentication and authorisation error types."""

from __future__ import annotations


class AuthenticationError(Exception):
    """Raised when authentication fails (invalid / expired token)."""

    def __init__(self, message: str = "Authentication required") -> None:
        self.message = message
        super().__init__(self.message)


class InsufficientPermissionsError(Exception):
    """Raised when the authenticated user lacks the required permissions."""

    def __init__(
        self,
        required: str | list[str] | None = None,
        message: str = "Insufficient permissions",
    ) -> None:
        self.required = required
        self.message = message
        super().__init__(self.message)
