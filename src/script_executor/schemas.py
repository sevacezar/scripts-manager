"""Pydantic schemas for script executor."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ScriptExecutionRequest(BaseModel):
    """Request model for script execution with flexible data input."""

    # JSON data passed to script
    json_data: Optional[dict[str, Any]] = Field(
        default=None,
        description="JSON data to pass to the script",
    )
    
    # Additional parameters as key-value pairs
    params: Optional[dict[str, str]] = Field(
        default=None,
        description="Additional string parameters",
    )


class ScriptExecutionResponse(BaseModel):
    """Response model for script execution."""

    success: bool = Field(description="Whether script executed successfully")
    result: Optional[Any] = Field(
        default=None,
        description="Script execution result (JSON-serializable)",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if execution failed",
    )
    execution_time: float = Field(description="Script execution time in seconds")

