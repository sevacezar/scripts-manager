"""Error handling utilities for scripts manager."""

from fastapi import HTTPException, status

from src.scripts_manager.error_codes import ErrorCode
from src.scripts_manager.exceptions import ScriptsManagerError
from src.scripts_manager.schemas import ErrorResponse


def create_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: dict[str, str] | None = None,
) -> HTTPException:
    """
    Create HTTPException with error code and message.
    
    Args:
        error_code: Error code
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        HTTPException with error response
    """
    error_response = ErrorResponse(
        error_code=error_code.value,
        message=message,
        details=details,
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_response.model_dump(),
    )


def handle_scripts_manager_error(error: ScriptsManagerError) -> HTTPException:
    """
    Convert ScriptsManagerError to HTTPException.
    
    Args:
        error: ScriptsManagerError instance
        
    Returns:
        HTTPException with appropriate status code
    """
    # Map error codes to HTTP status codes
    status_code_map: dict[ErrorCode, int] = {
        ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_FILENAME: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_SCRIPT_CONTENT: status.HTTP_400_BAD_REQUEST,
        ErrorCode.SCRIPT_MISSING_MAIN: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_FOLDER_NAME: status.HTTP_400_BAD_REQUEST,
        ErrorCode.FOLDER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.SCRIPT_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.PARENT_FOLDER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.FOLDER_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.SCRIPT_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.SCRIPT_EXISTS_REPLACE_REQUIRED: status.HTTP_409_CONFLICT,
        ErrorCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
        ErrorCode.NOT_FOLDER_OWNER: status.HTTP_403_FORBIDDEN,
        ErrorCode.NOT_SCRIPT_OWNER: status.HTTP_403_FORBIDDEN,
        ErrorCode.NOT_ALL_OWNER: status.HTTP_403_FORBIDDEN,
        ErrorCode.INTERNAL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.FILE_SYSTEM_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code: int = status_code_map.get(error.error_code, status.HTTP_400_BAD_REQUEST)
    
    return create_error_response(
        error_code=error.error_code,
        message=error.message,
        status_code=status_code,
        details=error.details,
    )

