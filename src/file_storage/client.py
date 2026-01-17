"""File storage client protocol and implementations."""

import secrets
from abc import ABC, abstractmethod
from pathlib import Path

from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)


class FileStorageClient(ABC):
    """Protocol for file storage clients (S3-compatible interface)."""

    @abstractmethod
    async def save_file(
        self,
        file_content: bytes,
        prefix: str = "",
        filename: str | None = None,
    ) -> str:
        """
        Save file and return relative path/key.
        
        Args:
            file_content: File content as bytes
            prefix: Prefix/path for file organization (like S3 prefix)
            filename: Optional filename. If not provided, generates unique name
            
        Returns:
            Relative path/key to the file (e.g., "prefix/filename.ext")
        """
        pass

    @abstractmethod
    async def get_file(self, key: str) -> bytes:
        """
        Download file by key.
        
        Args:
            key: Relative path/key to the file
            
        Returns:
            File content as bytes
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        pass

    @abstractmethod
    async def delete_file(self, key: str) -> None:
        """
        Delete file by key.
        
        Args:
            key: Relative path/key to the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        pass

    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """
        Check if file exists.
        
        Args:
            key: Relative path/key to the file
            
        Returns:
            True if file exists, False otherwise
        """
        pass


class LocalFileStorage(FileStorageClient):
    """Local file system implementation of file storage."""

    def __init__(self, base_dir: Path | None = None):
        """
        Initialize local file storage.
        
        Args:
            base_dir: Base directory for file storage. Defaults to uploads directory.
        """
        self.base_dir: Path = (base_dir or settings.uploads_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Local file storage initialized", base_dir=str(self.base_dir))

    def _generate_filename(self, original_filename: str | None = None) -> str:
        """
        Generate unique filename.
        
        Args:
            original_filename: Optional original filename to preserve extension
            
        Returns:
            Generated unique filename
        """
        if original_filename:
            # Preserve extension if provided
            extension: str = Path(original_filename).suffix
            random_part: str = secrets.token_urlsafe(16)
            return f"{random_part}{extension}"
        else:
            # Generate completely random filename
            return secrets.token_urlsafe(24)

    def _normalize_key(self, key: str) -> Path:
        """
        Normalize and validate key path.
        
        Args:
            key: File key/path
            
        Returns:
            Normalized Path object
            
        Raises:
            ValueError: If key is invalid or outside base directory
        """
        # Remove leading slashes
        normalized: str = key.lstrip("/")
        
        # Resolve path
        full_path: Path = (self.base_dir / normalized).resolve()
        
        # Security check: ensure path is within base directory
        try:
            full_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError(f"File key '{key}' is outside storage directory")
        
        return full_path

    async def save_file(
        self,
        file_content: bytes,
        prefix: str = "",
        filename: str | None = None,
    ) -> str:
        """
        Save file to local storage with random filename.
        
        Args:
            file_content: File content as bytes
            prefix: Prefix/path for file organization
            filename: Optional original filename (used only to preserve extension)
            
        Returns:
            Relative path/key to the file
        """
        # Normalize prefix
        normalized_prefix: str = prefix.strip("/").replace("\\", "/")
        
        # Always generate random filename to avoid collisions
        # Preserve extension from original filename if provided
        generated_filename: str = self._generate_filename(filename)
        
        # Build full path
        if normalized_prefix:
            target_dir: Path = self.base_dir / normalized_prefix
            target_dir.mkdir(parents=True, exist_ok=True)
            key: str = f"{normalized_prefix}/{generated_filename}"
        else:
            key = generated_filename
        
        target_path: Path = self._normalize_key(key)
        
        # Write file
        target_path.write_bytes(file_content)
        
        logger.info(
            "File saved",
            key=key,
            size=len(file_content),
            prefix=prefix,
            original_filename=filename,
        )
        
        return key

    async def get_file(self, key: str) -> bytes:
        """
        Download file from local storage.
        
        Args:
            key: Relative path/key to the file
            
        Returns:
            File content as bytes
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path: Path = self._normalize_key(key)
        
        if not file_path.exists():
            logger.warning("File not found", key=key)
            raise FileNotFoundError(f"File '{key}' not found")
        
        content: bytes = file_path.read_bytes()
        
        logger.info("File retrieved", key=key, size=len(content))
        
        return content

    async def delete_file(self, key: str) -> None:
        """
        Delete file from local storage.
        
        Args:
            key: Relative path/key to the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path: Path = self._normalize_key(key)
        
        if not file_path.exists():
            logger.warning("File not found for deletion", key=key)
            raise FileNotFoundError(f"File '{key}' not found")
        
        file_path.unlink()
        
        # Try to remove empty parent directories
        try:
            parent: Path = file_path.parent
            if parent != self.base_dir and not any(parent.iterdir()):
                parent.rmdir()
        except OSError:
            # Directory not empty or other error, ignore
            pass
        
        logger.info("File deleted", key=key)

    async def file_exists(self, key: str) -> bool:
        """
        Check if file exists in local storage.
        
        Args:
            key: Relative path/key to the file
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            file_path: Path = self._normalize_key(key)
            exists: bool = file_path.exists() and file_path.is_file()
            return exists
        except ValueError:
            return False

