class SentinelError(Exception):
    """Base exception for expected application errors."""


class EntityNotFoundError(SentinelError):
    """Raised when a requested entity does not exist."""


class InvalidRepositoryError(SentinelError):
    """Raised when a GitHub repository reference is malformed."""
