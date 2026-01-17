"""Router for file storage endpoints."""

import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import Response

from src.config import settings
from src.file_storage import LocalFileStorage
from src.file_storage.schemas import FileDownloadResponse, FileUploadResponse
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/files", tags=["files"])

# Initialize file storage
file_storage: LocalFileStorage = LocalFileStorage()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    summary="Upload file",
    description="Upload a file and get a key for future access.",
)
async def upload_file(
    file: UploadFile,
    prefix: str = "",
) -> FileUploadResponse:
    """
    Upload a file to storage.
    
    Args:
        file: File to upload
        prefix: Optional prefix/path for file organization (like S3 prefix)
        
    Returns:
        FileUploadResponse with file key
        
    Raises:
        HTTPException: If upload fails
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    try:
        # Read file content
        content: bytes = await file.read()
        
        # Check file size
        if len(content) > settings.max_file_size:
            logger.error(
                "File size exceeds limit",
                filename=file.filename,
                file_size=len(content),
                max_size=settings.max_file_size,
            )
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum size of {settings.max_file_size} bytes",
            )
        
        # Save file
        key: str = await file_storage.save_file(
            file_content=content,
            prefix=prefix,
            filename=file.filename,
        )
        
        logger.info("File uploaded", key=key, filename=file.filename, size=len(content))
        
        return FileUploadResponse(key=key, size=len(content))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File upload failed", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get(
    "/{key:path}/info",
    response_model=FileDownloadResponse,
    summary="Get file info",
    description="Get file information without downloading content.",
)
async def get_file_info(key: str) -> FileDownloadResponse:
    """
    Get file information.
    
    Args:
        key: File key/path
        
    Returns:
        FileDownloadResponse with file info
        
    Raises:
        HTTPException: If file not found
    """
    try:
        # Check if file exists
        exists: bool = await file_storage.file_exists(key)
        if not exists:
            logger.warning("File not found", key=key)
            raise HTTPException(status_code=404, detail=f"File '{key}' not found")
        
        # Get file content to determine size (could be optimized)
        content: bytes = await file_storage.get_file(key)
        content_type: str | None = mimetypes.guess_type(key)[0]
        
        return FileDownloadResponse(
            key=key,
            size=len(content),
            content_type=content_type,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get file info failed", error=str(e), key=key)
        raise HTTPException(status_code=500, detail=f"Get file info failed: {str(e)}")


@router.get(
    "/{key:path}",
    response_class=Response,
    summary="Download file",
    description="Download file by key.",
)
async def download_file(key: str) -> Response:
    """
    Download file by key.
    
    Args:
        key: File key/path
        
    Returns:
        File content as response
        
    Raises:
        HTTPException: If file not found
    """
    try:
        # Check if file exists
        exists: bool = await file_storage.file_exists(key)
        if not exists:
            logger.warning("File not found", key=key)
            raise HTTPException(status_code=404, detail=f"File '{key}' not found")
        
        # Get file content
        content: bytes = await file_storage.get_file(key)
        
        # Determine content type
        content_type: str | None = mimetypes.guess_type(key)[0] or "application/octet-stream"
        
        logger.info("File downloaded", key=key, size=len(content))
        
        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{Path(key).name}"',
            },
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File download failed", error=str(e), key=key)
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")


@router.delete(
    "/{key:path}",
    summary="Delete file",
    description="Delete file by key.",
)
async def delete_file(key: str) -> dict[str, str]:
    """
    Delete file by key.
    
    Args:
        key: File key/path
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If file not found
    """
    try:
        await file_storage.delete_file(key)
        
        logger.info("File deleted", key=key)
        
        return {"message": f"File '{key}' deleted successfully"}
        
    except FileNotFoundError:
        logger.warning("File not found for deletion", key=key)
        raise HTTPException(status_code=404, detail=f"File '{key}' not found")
    except Exception as e:
        logger.error("File deletion failed", error=str(e), key=key)
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")

