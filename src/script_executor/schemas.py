"""Pydantic schemas for script executor."""

from typing import Any

from pydantic import BaseModel, Field


class ScriptExecutionRequest(BaseModel):
    """Request model for script execution."""

    data: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON data to pass to script's main() function",
    )


class ScriptExecutionResponse(BaseModel):
    """Response model for script execution."""

    success: bool = Field(description="Whether script executed successfully")
    result: dict[str, Any] | None = Field(
        default=None,
        description="Script execution result (must be JSON-serializable dict)",
    )
    error: str | None = Field(
        default=None,
        description="Error message if execution failed",
    )
    execution_time: float = Field(description="Script execution time in seconds")
