"""Pydantic schemas for scripts and folders management."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.scripts_manager.error_codes import ErrorCode


class UserInfo(BaseModel):
    """User information for responses."""

    id: int = Field(description="User ID")
    login: str = Field(description="User login")

    class Config:
        """Pydantic config."""

        from_attributes = True


class FolderBase(BaseModel):
    """Base folder schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Folder name")
    parent_id: int | None = Field(
        default=None,
        description="Parent folder ID (None for root)",
    )


class FolderCreate(FolderBase):
    """Schema for folder creation."""

    pass


class FolderUpdate(BaseModel):
    """Schema for folder update."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New folder name",
    )


class FolderResponse(BaseModel):
    """Schema for folder response."""

    id: int = Field(description="Folder ID")
    name: str = Field(description="Folder name")
    path: str = Field(description="Folder path")
    parent_id: int | None = Field(description="Parent folder ID")
    created_by: UserInfo = Field(description="Folder creator")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    can_edit: bool = Field(description="Can user edit this folder")
    can_delete: bool = Field(description="Can user delete this folder")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ScriptBase(BaseModel):
    """Base script schema."""

    display_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Display name for the script",
    )
    description: str | None = Field(
        default=None,
        description="Script description",
    )
    folder_id: int | None = Field(
        default=None,
        description="Folder ID (None for root)",
    )


class ScriptCreate(ScriptBase):
    """Schema for script creation."""

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Script filename with .py extension",
    )
    replace: bool = Field(
        default=False,
        description="Replace existing script if it exists in the same logical folder",
    )


class ScriptUpdate(BaseModel):
    """Schema for script update."""

    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New display name",
    )
    description: str | None = Field(
        default=None,
        description="New description",
    )
    filename: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New filename",
    )


class ScriptResponse(BaseModel):
    """Schema for script response."""

    id: int = Field(description="Script ID")
    filename: str = Field(description="Script filename (original name)")
    logical_path: str = Field(description="Logical path for execution (e.g., 'geology/test.py')")
    display_name: str = Field(description="Display name")
    description: str | None = Field(description="Description")
    folder_id: int | None = Field(description="Folder ID")
    created_by: UserInfo = Field(description="Script creator")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    can_edit: bool = Field(description="Can user edit this script")
    can_delete: bool = Field(description="Can user delete this script")

    class Config:
        """Pydantic config."""

        from_attributes = True


class FolderTreeItem(BaseModel):
    """Schema for folder tree item."""

    folder: FolderResponse | None = Field(default=None, description="Folder data")
    scripts: list[ScriptResponse] = Field(
        default_factory=list,
        description="Scripts in this folder",
    )
    subfolders: list["FolderTreeItem"] = Field(
        default_factory=list,
        description="Subfolders",
    )


class ScriptsTreeResponse(BaseModel):
    """Schema for scripts tree response."""

    root_scripts: list[ScriptResponse] = Field(
        default_factory=list,
        description="Scripts in root",
    )
    root_folders: list[FolderTreeItem] = Field(
        default_factory=list,
        description="Folders in root",
    )


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: dict[str, str] | None = Field(
        default=None,
        description="Additional error details",
    )

