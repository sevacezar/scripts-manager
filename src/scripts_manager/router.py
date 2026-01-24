"""Router for scripts and folders management endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.database import get_db
from src.logger import get_logger
from src.scripts_manager.schemas import (
    FolderCreate,
    FolderResponse,
    FolderTreeItem,
    FolderUpdate,
    ScriptCreate,
    ScriptResponse,
    ScriptUpdate,
    ScriptsTreeResponse,
)
from src.scripts_manager.service import ScriptsManagerService

logger = get_logger(__name__)
router = APIRouter(prefix="/scripts-manager", tags=["scripts-manager"])

# Initialize service
scripts_service: ScriptsManagerService = ScriptsManagerService()


@router.post(
    "/folders",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create folder",
    description="Create a new folder in scripts directory.",
)
async def create_folder(
    folder_data: FolderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FolderResponse:
    """
    Create a new folder.
    
    Args:
        folder_data: Folder creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created folder information
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        folder = await scripts_service.create_folder(
            db=db,
            name=folder_data.name,
            parent_id=folder_data.parent_id,
            user=current_user,
        )
        
        # Load relationships
        await db.refresh(folder, ["created_by"])
        
        return FolderResponse(
            id=folder.id,
            name=folder.name,
            path=folder.path,
            parent_id=folder.parent_id,
            created_by={"id": folder.created_by.id, "login": folder.created_by.login},
            created_at=folder.created_at,
            updated_at=folder.updated_at,
            can_edit=True,
            can_delete=True,
        )
        
    except ValueError as e:
        logger.warning("Folder creation failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/folders/{folder_id}",
    response_model=FolderResponse,
    summary="Get folder",
    description="Get folder information.",
)
async def get_folder(
    folder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FolderResponse:
    """
    Get folder information.
    
    Args:
        folder_id: Folder ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Folder information
        
    Raises:
        HTTPException: If folder not found
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from src.scripts_manager.models import Folder
    
    result = await db.execute(
        select(Folder)
        .where(Folder.id == folder_id)
        .options(selectinload(Folder.created_by))
    )
    folder = result.scalar_one_or_none()
    
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Folder with id {folder_id} not found",
        )
    
    return FolderResponse(
        id=folder.id,
        name=folder.name,
        path=folder.path,
        parent_id=folder.parent_id,
        created_by={"id": folder.created_by.id, "login": folder.created_by.login},
        created_at=folder.created_at,
        updated_at=folder.updated_at,
        can_edit=folder.created_by_id == current_user.id or current_user.is_admin,
        can_delete=folder.created_by_id == current_user.id or current_user.is_admin,
    )


@router.put(
    "/folders/{folder_id}",
    response_model=FolderResponse,
    summary="Update folder",
    description="Update folder (rename).",
)
async def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FolderResponse:
    """
    Update folder.
    
    Args:
        folder_id: Folder ID
        folder_data: Folder update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated folder information
        
    Raises:
        HTTPException: If update fails
    """
    try:
        folder = await scripts_service.update_folder(
            db=db,
            folder_id=folder_id,
            name=folder_data.name,
            user=current_user,
        )
        
        # Ensure folder is fully loaded - refresh to avoid any lazy loading issues
        await db.refresh(folder, ["created_by", "parent"])
        
        # Access all fields immediately to avoid lazy loading
        folder_id_val: int = folder.id
        folder_name: str = folder.name
        folder_path: str = folder.path
        folder_parent_id: int | None = folder.parent_id
        folder_created_by_id: int = folder.created_by_id
        folder_created_at: datetime = folder.created_at
        folder_updated_at: datetime = folder.updated_at
        created_by_id: int = folder.created_by.id
        created_by_login: str = folder.created_by.login
        
        return FolderResponse(
            id=folder_id_val,
            name=folder_name,
            path=folder_path,
            parent_id=folder_parent_id,
            created_by={"id": created_by_id, "login": created_by_login},
            created_at=folder_created_at,
            updated_at=folder_updated_at,
            can_edit=folder_created_by_id == current_user.id or current_user.is_admin,
            can_delete=folder_created_by_id == current_user.id or current_user.is_admin,
        )
        
    except ValueError as e:
        logger.warning("Folder update failed", error=str(e), folder_id=folder_id, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/folders/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete folder",
    description="Delete folder and all its contents.",
)
async def delete_folder(
    folder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete folder.
    
    Args:
        folder_id: Folder ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        await scripts_service.delete_folder(
            db=db,
            folder_id=folder_id,
            user=current_user,
        )
        
    except ValueError as e:
        logger.warning("Folder deletion failed", error=str(e), folder_id=folder_id, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/scripts",
    response_model=ScriptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create script",
    description="Add a new script to the system.",
)
async def create_script(
    file: UploadFile,
    display_name: str,
    description: str | None = None,
    folder_id: int | None = None,
    replace: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ScriptResponse:
    """
    Create a new script.
    
    Args:
        file: Script file (.py)
        display_name: Display name for the script
        description: Optional description
        folder_id: Optional folder ID
        replace: If True, replace existing script in the same logical folder
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created script information
        
    Raises:
        HTTPException: If creation fails
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )
    
    if not file.filename.endswith(".py"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have .py extension",
        )
    
    try:
        # Read file content
        content: str = (await file.read()).decode("utf-8")
        
        script = await scripts_service.create_script(
            db=db,
            filename=file.filename,
            display_name=display_name,
            description=description,
            folder_id=folder_id,
            content=content,
            user=current_user,
            replace=replace,
        )
        
        # Load relationships (already loaded by service)
        return ScriptResponse(
            id=script.id,
            filename=script.filename,
            logical_path=script.logical_path,
            display_name=script.display_name,
            description=script.description,
            folder_id=script.folder_id,
            created_by={"id": script.created_by.id, "login": script.created_by.login},
            created_at=script.created_at,
            updated_at=script.updated_at,
            can_edit=True,
            can_delete=True,
        )
        
    except ValueError as e:
        logger.warning("Script creation failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/scripts/{script_id}",
    response_model=ScriptResponse,
    summary="Get script",
    description="Get script information.",
)
async def get_script(
    script_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ScriptResponse:
    """
    Get script information.
    
    Args:
        script_id: Script ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Script information
        
    Raises:
        HTTPException: If script not found
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from src.scripts_manager.models import Script
    
    result = await db.execute(
        select(Script)
        .where(Script.id == script_id)
        .options(selectinload(Script.created_by))
    )
    script = result.scalar_one_or_none()
    
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Script with id {script_id} not found",
        )
    
    return ScriptResponse(
        id=script.id,
        filename=script.filename,
        logical_path=script.logical_path,
        display_name=script.display_name,
        description=script.description,
        folder_id=script.folder_id,
        created_by={"id": script.created_by.id, "login": script.created_by.login},
        created_at=script.created_at,
        updated_at=script.updated_at,
        can_edit=script.created_by_id == current_user.id or current_user.is_admin,
        can_delete=script.created_by_id == current_user.id or current_user.is_admin,
    )


@router.get(
    "/scripts/{script_id}/content",
    summary="Get script content",
    description="Get script file content.",
)
async def get_script_content(
    script_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    """
    Get script content.
    
    Args:
        script_id: Script ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Script content
        
    Raises:
        HTTPException: If script not found
    """
    try:
        content = await scripts_service.get_script_content(
            db=db,
            script_id=script_id,
            user=current_user,
        )
        
        return {"content": content}
        
    except ValueError as e:
        logger.warning("Get script content failed", error=str(e), script_id=script_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/scripts/{script_id}",
    response_model=ScriptResponse,
    summary="Update script",
    description="Update script metadata or rename.",
)
async def update_script(
    script_id: int,
    script_data: ScriptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ScriptResponse:
    """
    Update script.
    
    Args:
        script_id: Script ID
        script_data: Script update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated script information
        
    Raises:
        HTTPException: If update fails
    """
    try:
        script = await scripts_service.update_script(
            db=db,
            script_id=script_id,
            display_name=script_data.display_name,
            description=script_data.description,
            filename=script_data.filename,
            user=current_user,
        )
        
        # Script is already reloaded in service with all relationships
        # Ensure script is fully loaded - refresh to avoid any lazy loading issues
        await db.refresh(script, ["created_by", "folder"])
        
        # Access all fields immediately to avoid lazy loading
        script_id_val: int = script.id
        script_filename: str = script.filename
        script_logical_path: str = script.logical_path
        script_display_name: str = script.display_name
        script_description: str | None = script.description
        script_folder_id: int | None = script.folder_id
        script_created_by_id: int = script.created_by_id
        script_created_at: datetime = script.created_at
        script_updated_at: datetime = script.updated_at
        created_by_id: int = script.created_by.id
        created_by_login: str = script.created_by.login
        
        return ScriptResponse(
            id=script_id_val,
            filename=script_filename,
            logical_path=script_logical_path,
            display_name=script_display_name,
            description=script_description,
            folder_id=script_folder_id,
            created_by={"id": created_by_id, "login": created_by_login},
            created_at=script_created_at,
            updated_at=script_updated_at,
            can_edit=script_created_by_id == current_user.id or current_user.is_admin,
            can_delete=script_created_by_id == current_user.id or current_user.is_admin,
        )
        
    except ValueError as e:
        logger.warning("Script update failed", error=str(e), script_id=script_id, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/scripts/{script_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete script",
    description="Delete a script.",
)
async def delete_script(
    script_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete script.
    
    Args:
        script_id: Script ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        await scripts_service.delete_script(
            db=db,
            script_id=script_id,
            user=current_user,
        )
        
    except ValueError as e:
        logger.warning("Script deletion failed", error=str(e), script_id=script_id, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/tree",
    response_model=ScriptsTreeResponse,
    summary="Get scripts tree",
    description="Get complete scripts tree with permissions.",
)
async def get_scripts_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ScriptsTreeResponse:
    """
    Get complete scripts tree.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Complete scripts tree
    """
    tree = await scripts_service.get_scripts_tree(db=db, user=current_user)
    
    return ScriptsTreeResponse.model_validate(tree)



