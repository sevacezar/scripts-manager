"""Custom exceptions for scripts manager."""

from src.scripts_manager.error_codes import ErrorCode


class ScriptsManagerError(Exception):
    """Base exception for scripts manager errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: dict[str, str] | None = None,
    ):
        """
        Initialize error.
        
        Args:
            error_code: Error code
            message: Error message
            details: Additional error details
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ScriptsManagerError):
    """Validation error."""

    def __init__(self, message: str, details: dict[str, str] | None = None):
        super().__init__(ErrorCode.VALIDATION_ERROR, message, details)


class ResourceNotFoundError(ScriptsManagerError):
    """Resource not found error."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: dict[str, str] | None = None,
    ):
        super().__init__(error_code, message, details)


class ConflictError(ScriptsManagerError):
    """Conflict error (resource already exists)."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: dict[str, str] | None = None,
    ):
        super().__init__(error_code, message, details)


class PermissionError(ScriptsManagerError):
    """Permission denied error."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: dict[str, str] | None = None,
    ):
        super().__init__(error_code, message, details)

