"""Service for managing scripts and folders."""

from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import User
from src.config import settings
from src.logger import get_logger
from src.scripts_manager.error_codes import ErrorCode
from src.scripts_manager.exceptions import (
    ConflictError,
    PermissionError,
    ResourceNotFoundError,
    ValidationError,
)
from src.scripts_manager.models import Folder, Script
from src.scripts_manager.validators import validate_script_content

logger = get_logger(__name__)


class ScriptsManagerService:
    """Service for managing scripts and folders."""

    def __init__(self):
        """Initialize scripts manager service."""
        self.scripts_dir: Path = settings.scripts_dir.resolve()
        # Ensure scripts directory exists
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

    def _build_logical_path(self, filename: str, folder: Folder | None) -> str:
        """
        Build logical path for script based on folder hierarchy.
        
        Args:
            filename: Script filename
            folder: Folder object (None for root)
            
        Returns:
            Logical path (e.g., "geology/test.py")
        """
        if folder:
            return f"{folder.path}/{filename}"
        return filename

    async def create_folder(
        self,
        db: AsyncSession,
        name: str,
        parent_id: int | None,
        user: User,
    ) -> Folder:
        """
        Create a new folder (only in DB, no filesystem operations).
        
        Args:
            db: Database session
            name: Folder name
            parent_id: Parent folder ID (None for root)
            user: User creating the folder
            
        Returns:
            Created Folder object
            
        Raises:
            ValueError: If folder already exists or parent not found
        """
        # Get parent folder if specified
        parent: Folder | None = None
        parent_path: str = ""
        if parent_id:
            parent_result = await db.execute(select(Folder).where(Folder.id == parent_id))
            parent = parent_result.scalar_one_or_none()
            if not parent:
                raise ResourceNotFoundError(
                    ErrorCode.PARENT_FOLDER_NOT_FOUND,
                    f"Parent folder with id {parent_id} not found",
                    {"parent_id": str(parent_id)},
                )
            parent_path = parent.path
        
        # Build folder path
        if parent_path:
            folder_path: str = f"{parent_path}/{name}"
        else:
            folder_path = name
        
        # Check if folder already exists in DB
        existing = await db.execute(select(Folder).where(Folder.path == folder_path))
        if existing.scalar_one_or_none():
            raise ConflictError(
                ErrorCode.FOLDER_ALREADY_EXISTS,
                f"Folder '{folder_path}' already exists",
                {"path": folder_path},
            )
        
        # Create folder in DB only
        folder: Folder = Folder(
            name=name,
            path=folder_path,
            parent_id=parent_id,
            created_by_id=user.id,
        )
        
        db.add(folder)
        await db.commit()
        await db.refresh(folder)
        
        logger.info("Folder created", folder_id=folder.id, path=folder_path, user_id=user.id)
        
        return folder

    async def create_script(
        self,
        db: AsyncSession,
        filename: str,
        display_name: str,
        description: str | None,
        folder_id: int | None,
        content: str,
        user: User,
        replace: bool = False,
    ) -> Script:
        """
        Create a new script.
        
        All scripts are stored in the root scripts/ directory with their original names.
        Logical path is built from folder hierarchy in DB.
        
        Args:
            db: Database session
            filename: Script filename (original name)
            display_name: Display name
            description: Description
            folder_id: Folder ID (None for root)
            content: Script content
            user: User creating the script
            replace: If True, replace existing script in the same logical folder
            
        Returns:
            Created Script object
            
        Raises:
            ValueError: If validation fails or script already exists
        """
        # Validate filename
        if not filename.endswith(".py"):
            raise ValidationError(
                "Script filename must have .py extension",
                {"filename": filename},
            )
        
        # Validate script content
        is_valid, error_msg = validate_script_content(content)
        if not is_valid:
            if "main" in error_msg.lower():
                raise ValidationError(
                    error_msg,
                    {"error_code": ErrorCode.SCRIPT_MISSING_MAIN.value},
                )
            raise ValidationError(
                f"Script validation failed: {error_msg}",
                {"error_code": ErrorCode.INVALID_SCRIPT_CONTENT.value},
            )
        
        # Get folder if specified
        folder: Folder | None = None
        if folder_id:
            folder_result = await db.execute(select(Folder).where(Folder.id == folder_id))
            folder = folder_result.scalar_one_or_none()
            if not folder:
                raise ResourceNotFoundError(
                    ErrorCode.FOLDER_NOT_FOUND,
                    f"Folder with id {folder_id} not found",
                    {"folder_id": str(folder_id)},
                )
        
        # Build logical path
        logical_path: str = self._build_logical_path(filename, folder)
        
        # Check if script already exists in this logical location
        existing_result = await db.execute(
            select(Script).where(Script.logical_path == logical_path)
        )
        existing_script: Script | None = existing_result.scalar_one_or_none()
        
        if existing_script:
            if not replace:
                raise ConflictError(
                    ErrorCode.SCRIPT_EXISTS_REPLACE_REQUIRED,
                    f"Script '{logical_path}' already exists. Use replace=True to replace it.",
                    {"logical_path": logical_path, "script_id": str(existing_script.id)},
                )
            # Check permissions for replacement
            if existing_script.created_by_id != user.id and not user.is_admin:
                raise PermissionError(
                    ErrorCode.NOT_SCRIPT_OWNER,
                    "You don't have permission to replace this script",
                    {"script_id": str(existing_script.id)},
                )
            
            # Update existing script
            existing_script.filename = filename
            existing_script.display_name = display_name
            existing_script.description = description
            existing_script.created_by_id = user.id  # New creator
            
            # Update file content
            storage_path: Path = self.scripts_dir / existing_script.storage_filename
            storage_path.write_text(content, encoding="utf-8")
            
            await db.commit()
            await db.refresh(existing_script, ["created_by"])
            
            logger.info(
                "Script replaced",
                script_id=existing_script.id,
                logical_path=logical_path,
                user_id=user.id,
            )
            
            return existing_script
        
        # Create new script file in root directory
        storage_filename: str = filename
        storage_path: Path = self.scripts_dir / storage_filename
        
        # If file already exists in filesystem, generate unique name
        if storage_path.exists():
            counter: int = 1
            name_part: str = storage_filename[:-3]  # Without .py
            while storage_path.exists():
                storage_filename = f"{name_part}_{counter}.py"
                storage_path = self.scripts_dir / storage_filename
                counter += 1
            logger.warning(
                "File with same name exists, using unique name",
                original=filename,
                storage=storage_filename,
            )
        
        # Write script file
        storage_path.write_text(content, encoding="utf-8")
        
        # Create script in DB
        script: Script = Script(
            filename=filename,
            storage_filename=storage_filename,
            logical_path=logical_path,
            display_name=display_name,
            description=description,
            folder_id=folder_id,
            created_by_id=user.id,
        )
        
        db.add(script)
        await db.commit()
        await db.refresh(script, ["created_by"])
        
        logger.info(
            "Script created",
            script_id=script.id,
            logical_path=logical_path,
            storage_filename=storage_filename,
            user_id=user.id,
        )
        
        return script

    async def update_script(
        self,
        db: AsyncSession,
        script_id: int,
        display_name: str | None,
        description: str | None,
        filename: str | None,
        user: User,
    ) -> Script:
        """
        Update script metadata or rename.
        
        Args:
            db: Database session
            script_id: Script ID
            display_name: New display name
            description: New description
            filename: New filename (changes logical_path)
            user: User updating the script
            
        Returns:
            Updated Script object
            
        Raises:
            ValueError: If script not found or user has no permission
        """
        # Get script with folder relationship loaded
        result = await db.execute(
            select(Script)
            .where(Script.id == script_id)
            .options(selectinload(Script.folder))
        )
        script: Script | None = result.scalar_one_or_none()
        
        if not script:
            raise ResourceNotFoundError(
                ErrorCode.SCRIPT_NOT_FOUND,
                f"Script with id {script_id} not found",
                {"script_id": str(script_id)},
            )
        
        # Check permissions
        if script.created_by_id != user.id and not user.is_admin:
            raise PermissionError(
                ErrorCode.NOT_SCRIPT_OWNER,
                "You don't have permission to edit this script",
                {"script_id": str(script_id)},
            )
        
        # Update metadata
        if display_name is not None:
            script.display_name = display_name
        if description is not None:
            script.description = description
        
        # Handle filename change (changes logical_path)
        if filename is not None:
            if not filename.endswith(".py"):
                raise ValidationError(
                    "Script filename must have .py extension",
                    {"filename": filename},
                )
            
            # Build new logical path (folder is already loaded)
            new_logical_path: str = self._build_logical_path(filename, script.folder)
            
            # Check if new logical path exists
            existing_result = await db.execute(
                select(Script).where(Script.logical_path == new_logical_path)
            )
            existing: Script | None = existing_result.scalar_one_or_none()
            if existing and existing.id != script_id:
                raise ConflictError(
                    ErrorCode.SCRIPT_ALREADY_EXISTS,
                    f"Script '{new_logical_path}' already exists",
                    {"logical_path": new_logical_path},
                )
            
            # Update logical path and filename
            script.filename = filename
            script.logical_path = new_logical_path
        
        # Store script_id before commit
        script_id_val: int = script.id
        
        await db.flush()
        await db.commit()
        
        # Reload script from DB to get all updated values including updated_at
        reload_result = await db.execute(
            select(Script)
            .where(Script.id == script_id_val)
            .options(selectinload(Script.created_by), selectinload(Script.folder))
        )
        reloaded_script: Script = reload_result.scalar_one()
        
        logger.info("Script updated", script_id=reloaded_script.id, user_id=user.id)
        
        return reloaded_script

    async def delete_script(
        self,
        db: AsyncSession,
        script_id: int,
        user: User,
    ) -> None:
        """
        Delete a script.
        
        Args:
            db: Database session
            script_id: Script ID
            user: User deleting the script
            
        Raises:
            ValueError: If script not found or user has no permission
        """
        # Get script
        result = await db.execute(select(Script).where(Script.id == script_id))
        script: Script | None = result.scalar_one_or_none()
        
        if not script:
            raise ResourceNotFoundError(
                ErrorCode.SCRIPT_NOT_FOUND,
                f"Script with id {script_id} not found",
                {"script_id": str(script_id)},
            )
        
        # Check permissions
        if script.created_by_id != user.id and not user.is_admin:
            raise PermissionError(
                ErrorCode.NOT_SCRIPT_OWNER,
                "You don't have permission to delete this script",
                {"script_id": str(script_id)},
            )
        
        # Store logical_path for logging before deletion
        logical_path: str = script.logical_path
        storage_filename: str = script.storage_filename
        
        # Delete file from root directory
        storage_path: Path = self.scripts_dir / storage_filename
        if storage_path.exists():
            storage_path.unlink()
        
        # Delete from DB using delete() statement
        await db.execute(delete(Script).where(Script.id == script_id))
        await db.commit()
        
        logger.info(
            "Script deleted",
            script_id=script_id,
            logical_path=logical_path,
            user_id=user.id,
        )

    async def update_folder(
        self,
        db: AsyncSession,
        folder_id: int,
        name: str | None,
        user: User,
    ) -> Folder:
        """
        Update folder (rename) - only updates DB, no filesystem operations.
        
        Args:
            db: Database session
            folder_id: Folder ID
            name: New folder name
            user: User updating the folder
            
        Returns:
            Updated Folder object
            
        Raises:
            ValueError: If folder not found or user has no permission
        """
        # Get folder with relationships
        result = await db.execute(
            select(Folder)
            .where(Folder.id == folder_id)
            .options(selectinload(Folder.parent))
        )
        folder: Folder | None = result.scalar_one_or_none()
        
        if not folder:
            raise ResourceNotFoundError(
                ErrorCode.FOLDER_NOT_FOUND,
                f"Folder with id {folder_id} not found",
                {"folder_id": str(folder_id)},
            )
        
        # Check permissions
        if folder.created_by_id != user.id and not user.is_admin:
            raise PermissionError(
                ErrorCode.NOT_FOLDER_OWNER,
                "You don't have permission to edit this folder",
                {"folder_id": str(folder_id)},
            )
        
        if name is not None:
            # Build new path
            parent_path: str = ""
            if folder.parent:
                parent_path = folder.parent.path
            
            if parent_path:
                new_path: str = f"{parent_path}/{name}"
            else:
                new_path = name
            
            # Check if new path exists
            existing = await db.execute(select(Folder).where(Folder.path == new_path))
            if existing.scalar_one_or_none():
                raise ConflictError(
                    ErrorCode.FOLDER_ALREADY_EXISTS,
                    f"Folder '{new_path}' already exists",
                    {"path": new_path},
                )
            
            # Update folder and all children paths recursively
            await self._update_folder_path_recursive(db, folder, new_path)
            
            folder.name = name
            folder.path = new_path
        
        # Store folder_id before commit
        folder_id_val: int = folder.id
        
        # Flush and commit changes
        await db.flush()
        await db.commit()
        
        # Reload folder from DB to get all updated values including updated_at
        # This ensures we have a fresh object with all fields loaded
        reload_result = await db.execute(
            select(Folder)
            .where(Folder.id == folder_id_val)
            .options(selectinload(Folder.created_by), selectinload(Folder.parent))
        )
        reloaded_folder: Folder = reload_result.scalar_one()
        
        logger.info("Folder updated", folder_id=reloaded_folder.id, user_id=user.id)
        
        return reloaded_folder

    async def _update_folder_path_recursive(
        self,
        db: AsyncSession,
        folder: Folder,
        new_base_path: str,
    ) -> None:
        """
        Recursively update logical paths for folder and all scripts in it.
        
        Args:
            db: Database session
            folder: Folder to update
            new_base_path: New base path
        """
        # Update folder path
        folder.path = new_base_path
        
        # Update all scripts in folder (logical_path changes)
        scripts_result = await db.execute(
            select(Script).where(Script.folder_id == folder.id)
        )
        scripts: list[Script] = list(scripts_result.scalars().all())
        
        for script in scripts:
            script.logical_path = f"{new_base_path}/{script.filename}"
        
        # Update all subfolders recursively
        subfolders_result = await db.execute(
            select(Folder).where(Folder.parent_id == folder.id)
        )
        subfolders: list[Folder] = list(subfolders_result.scalars().all())
        
        for subfolder in subfolders:
            subfolder_name: str = subfolder.name
            new_subfolder_path: str = f"{new_base_path}/{subfolder_name}"
            await self._update_folder_path_recursive(db, subfolder, new_subfolder_path)

    async def _check_folder_deletion_permissions(
        self,
        db: AsyncSession,
        folder: Folder,
        user: User,
    ) -> tuple[bool, str | None]:
        """
        Check if user can delete folder (recursively check all children).
        
        Args:
            db: Database session
            folder: Folder to check
            user: User requesting deletion
            
        Returns:
            Tuple of (can_delete, error_message)
        """
        # Admin can delete anything
        if user.is_admin:
            return True, None
        
        # Check if user is folder creator
        if folder.created_by_id != user.id:
            return False, f"You are not the creator of folder '{folder.name}'"
        
        # Recursively check all subfolders
        subfolders_result = await db.execute(
            select(Folder).where(Folder.parent_id == folder.id)
        )
        subfolders: list[Folder] = list(subfolders_result.scalars().all())
        
        for subfolder in subfolders:
            can_delete, error = await self._check_folder_deletion_permissions(
                db, subfolder, user
            )
            if not can_delete:
                return False, error
        
        # Check all scripts in folder
        scripts_result = await db.execute(
            select(Script).where(Script.folder_id == folder.id)
        )
        scripts: list[Script] = list(scripts_result.scalars().all())
        
        for script in scripts:
            if script.created_by_id != user.id:
                return False, f"You are not the creator of script '{script.filename}'"
        
        return True, None

    async def delete_folder(
        self,
        db: AsyncSession,
        folder_id: int,
        user: User,
    ) -> None:
        """
        Delete a folder and all its contents (only from DB).
        Scripts are deleted from DB, but files remain in scripts/ directory.
        
        Args:
            db: Database session
            folder_id: Folder ID
            user: User deleting the folder
            
        Raises:
            ValueError: If folder not found or user has no permission
        """
        # Get folder
        result = await db.execute(select(Folder).where(Folder.id == folder_id))
        folder: Folder | None = result.scalar_one_or_none()
        
        if not folder:
            raise ResourceNotFoundError(
                ErrorCode.FOLDER_NOT_FOUND,
                f"Folder with id {folder_id} not found",
                {"folder_id": str(folder_id)},
            )
        
        # Check permissions recursively
        can_delete, error_msg = await self._check_folder_deletion_permissions(db, folder, user)
        if not can_delete:
            raise PermissionError(
                ErrorCode.NOT_ALL_OWNER,
                error_msg or "You don't have permission to delete this folder",
                {"folder_id": str(folder_id)},
            )
        
        # Collect all scripts to delete (for logging and file deletion)
        all_scripts: list[Script] = []
        await self._collect_folder_scripts(db, folder, all_scripts)
        
        # Store path for logging before deletion
        folder_path: str = folder.path
        
        # Delete physical files for all scripts
        for script in all_scripts:
            storage_path: Path = self.scripts_dir / script.storage_filename
            if storage_path.exists():
                try:
                    storage_path.unlink()
                    logger.debug("Script file deleted", path=str(storage_path), script_id=script.id)
                except Exception as e:
                    logger.warning(
                        "Failed to delete script file",
                        path=str(storage_path),
                        script_id=script.id,
                        error=str(e),
                    )
        
        # Collect all folder IDs to delete (including subfolders)
        folder_ids_to_delete: list[int] = []
        await self._collect_folder_ids(db, folder, folder_ids_to_delete)
        
        # Delete all scripts in these folders first (if cascade doesn't work)
        if folder_ids_to_delete:
            await db.execute(delete(Script).where(Script.folder_id.in_(folder_ids_to_delete)))
        
        # Delete all folders (cascade should handle scripts, but we delete them explicitly above)
        await db.execute(delete(Folder).where(Folder.id.in_(folder_ids_to_delete)))
        await db.commit()
        
        logger.info(
            "Folder deleted",
            folder_id=folder_id,
            path=folder_path,
            user_id=user.id,
            scripts_count=len(all_scripts),
            folders_count=len(folder_ids_to_delete),
        )

    async def _collect_folder_scripts(
        self,
        db: AsyncSession,
        folder: Folder,
        scripts: list[Script],
    ) -> None:
        """
        Recursively collect all scripts in folder and subfolders.
        
        Args:
            db: Database session
            folder: Folder to collect from
            scripts: List to append scripts to
        """
        # Get scripts in folder
        scripts_result = await db.execute(
            select(Script).where(Script.folder_id == folder.id)
        )
        scripts.extend(list(scripts_result.scalars().all()))
        
        # Get subfolders
        subfolders_result = await db.execute(
            select(Folder).where(Folder.parent_id == folder.id)
        )
        subfolders: list[Folder] = list(subfolders_result.scalars().all())
        
        # Recursively collect from subfolders
        for subfolder in subfolders:
            await self._collect_folder_scripts(db, subfolder, scripts)

    async def _collect_folder_ids(
        self,
        db: AsyncSession,
        folder: Folder,
        folder_ids: list[int],
    ) -> None:
        """
        Recursively collect all folder IDs including subfolders.
        
        Args:
            db: Database session
            folder: Folder to collect from
            folder_ids: List to append folder IDs to
        """
        folder_ids.append(folder.id)
        
        # Get subfolders
        subfolders_result = await db.execute(
            select(Folder).where(Folder.parent_id == folder.id)
        )
        subfolders: list[Folder] = list(subfolders_result.scalars().all())
        
        # Recursively collect from subfolders
        for subfolder in subfolders:
            await self._collect_folder_ids(db, subfolder, folder_ids)

    async def get_scripts_tree(
        self,
        db: AsyncSession,
        user: User,
    ) -> dict[str, Any]:
        """
        Get complete scripts tree with permissions.
        
        Args:
            db: Database session
            user: Current user
            
        Returns:
            Dictionary with tree structure
        """
        # Get all folders with relationships
        folders_result = await db.execute(
            select(Folder).options(selectinload(Folder.created_by))
        )
        all_folders: list[Folder] = list(folders_result.scalars().all())
        
        # Get all scripts with relationships
        scripts_result = await db.execute(
            select(Script).options(selectinload(Script.created_by))
        )
        all_scripts: list[Script] = list(scripts_result.scalars().all())
        
        # Build folder map
        folder_map: dict[int, Folder] = {f.id: f for f in all_folders}
        
        # Build tree structure
        root_folders: list[Folder] = [f for f in all_folders if f.parent_id is None]
        root_scripts: list[Script] = [s for s in all_scripts if s.folder_id is None]
        
        # Build response
        tree: dict[str, Any] = {
            "root_folders": [
                await self._build_folder_tree_item(db, folder, folder_map, all_scripts, user)
                for folder in root_folders
            ],
            "root_scripts": [
                await self._build_script_response(script, user) for script in root_scripts
            ],
        }
        
        return tree

    async def _build_folder_tree_item(
        self,
        db: AsyncSession,
        folder: Folder,
        folder_map: dict[int, Folder],
        all_scripts: list[Script],
        user: User,
    ) -> dict[str, Any]:
        """
        Build folder tree item recursively.
        
        Args:
            db: Database session
            folder: Folder to build
            folder_map: Map of folder IDs to folders
            all_scripts: All scripts list
            user: Current user
            
        Returns:
            Dictionary with folder tree item
        """
        # Get scripts in this folder
        folder_scripts: list[Script] = [
            s for s in all_scripts if s.folder_id == folder.id
        ]
        
        # Get subfolders
        subfolders: list[Folder] = [
            f for f in folder_map.values() if f.parent_id == folder.id
        ]
        
        # Build subfolders recursively
        subfolder_items: list[dict[str, Any]] = [
            await self._build_folder_tree_item(db, sf, folder_map, all_scripts, user)
            for sf in subfolders
        ]
        
        return {
            "folder": await self._build_folder_response(folder, user),
            "scripts": [
                await self._build_script_response(script, user) for script in folder_scripts
            ],
            "subfolders": subfolder_items,
        }

    async def _build_folder_response(
        self,
        folder: Folder,
        user: User,
    ) -> dict[str, Any]:
        """
        Build folder response with permissions.
        
        Args:
            folder: Folder object
            user: Current user
            
        Returns:
            Dictionary with folder data
        """
        return {
            "id": folder.id,
            "name": folder.name,
            "path": folder.path,
            "parent_id": folder.parent_id,
            "created_by": {"id": folder.created_by.id, "login": folder.created_by.login},
            "created_at": folder.created_at,
            "updated_at": folder.updated_at,
            "can_edit": folder.created_by_id == user.id or user.is_admin,
            "can_delete": folder.created_by_id == user.id or user.is_admin,
        }

    async def _build_script_response(
        self,
        script: Script,
        user: User,
    ) -> dict[str, Any]:
        """
        Build script response with permissions.
        
        Args:
            script: Script object
            user: Current user
            
        Returns:
            Dictionary with script data
        """
        return {
            "id": script.id,
            "filename": script.filename,
            "logical_path": script.logical_path,
            "display_name": script.display_name,
            "description": script.description,
            "folder_id": script.folder_id,
            "created_by": {"id": script.created_by.id, "login": script.created_by.login},
            "created_at": script.created_at,
            "updated_at": script.updated_at,
            "can_edit": script.created_by_id == user.id or user.is_admin,
            "can_delete": script.created_by_id == user.id or user.is_admin,
        }

    async def get_script_content(
        self,
        db: AsyncSession,
        script_id: int,
        user: User,
    ) -> str:
        """
        Get script content.
        
        Args:
            db: Database session
            script_id: Script ID
            user: Current user
            
        Returns:
            Script content as string
            
        Raises:
            ValueError: If script not found
        """
        result = await db.execute(select(Script).where(Script.id == script_id))
        script: Script | None = result.scalar_one_or_none()
        
        if not script:
            raise ResourceNotFoundError(
                ErrorCode.SCRIPT_NOT_FOUND,
                f"Script with id {script_id} not found",
                {"script_id": str(script_id)},
            )
        
        storage_path: Path = self.scripts_dir / script.storage_filename
        
        if not storage_path.exists():
            raise ResourceNotFoundError(
                ErrorCode.SCRIPT_NOT_FOUND,
                f"Script file '{script.storage_filename}' not found in filesystem",
                {"storage_filename": script.storage_filename, "script_id": str(script_id)},
            )
        
        return storage_path.read_text(encoding="utf-8")

    async def get_script_by_logical_path(
        self,
        db: AsyncSession,
        logical_path: str,
    ) -> Script | None:
        """
        Get script by logical path (for script executor).
        
        Args:
            db: Database session
            logical_path: Logical path (e.g., "geology/test.py")
            
        Returns:
            Script object or None if not found
        """
        result = await db.execute(
            select(Script).where(Script.logical_path == logical_path)
        )
        return result.scalar_one_or_none()
