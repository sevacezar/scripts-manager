"""Pydantic schemas for file storage."""

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response model for file upload."""

    key: str = Field(description="File key/path for future access")
    size: int = Field(description="File size in bytes")


class FileDownloadResponse(BaseModel):
    """Response model for file download info."""

    key: str = Field(description="File key/path")
    size: int = Field(description="File size in bytes")
    content_type: str | None = Field(
        default=None,
        description="Content type of the file",
    )

