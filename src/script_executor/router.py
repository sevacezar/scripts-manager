"""Router for script execution endpoints."""

import time
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.config import settings
from src.logger import logger
from src.script_executor.schemas import ScriptExecutionResponse
from src.script_executor.service import ScriptExecutionError, ScriptExecutorService

router = APIRouter(prefix="/scripts", tags=["scripts"])

# Initialize service
script_executor = ScriptExecutorService()


@router.post(
    "/{script_path:path}",
    response_model=ScriptExecutionResponse,
    summary="Execute Python script",
    description=(
        "Execute a Python script from the scripts directory. "
        "Supports flexible input: JSON data, parameters, and file uploads. "
        "Script receives data via INPUT_DATA global variable."
    ),
)
async def execute_script(
    script_path: str,
    json_data: Optional[str] = Form(
        default=None,
        description="JSON data as string (will be parsed)",
    ),
    params: Optional[str] = Form(
        default=None,
        description="Additional parameters as JSON string",
    ),
    files: Optional[list[UploadFile]] = File(
        default=None,
        description="Files to upload and pass to script",
    ),
) -> ScriptExecutionResponse:
    """
    Execute a Python script with flexible input data.
    
    The script receives all input data via a global variable `INPUT_DATA`:
    - JSON data and parameters are merged into INPUT_DATA
    - Files are stored in temporary directory, paths stored in INPUT_DATA["_files"]
    
    Example INPUT_DATA structure:
    {
        "key1": "value1",
        "key2": {"nested": "data"},
        "_files": {
            "uploaded_file.txt": "/tmp/xyz/uploaded_file.txt"
        },
        "_temp_dir": "/tmp/xyz"
    }
    
    Args:
        script_path: Relative path to script from scripts directory
        json_data: JSON data as string (optional)
        params: Additional parameters as JSON string (optional)
        files: List of uploaded files (optional)
        
    Returns:
        ScriptExecutionResponse with execution result
        
    Raises:
        HTTPException: If script execution fails
    """
    start_time = time.time()
    
    try:
        # Parse JSON data if provided
        parsed_json_data: Optional[dict] = None
        if json_data:
            import json
            try:
                parsed_json_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid JSON data: {str(e)}",
                )
        
        # Parse params if provided
        parsed_params: Optional[dict[str, str]] = None
        if params:
            import json
            try:
                parsed_params = json.loads(params)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid params JSON: {str(e)}",
                )
        
        # Read uploaded files
        file_data: Optional[dict[str, bytes]] = None
        if files:
            file_data = {}
            for file in files:
                if file.filename:
                    content = await file.read()
                    # Check file size
                    if len(content) > settings.max_file_size:
                        raise HTTPException(
                            status_code=413,
                            detail=f"File {file.filename} exceeds maximum size of {settings.max_file_size} bytes",
                        )
                    file_data[file.filename] = content
        
        # Execute script
        result = script_executor.execute_script(
            script_path=script_path,
            json_data=parsed_json_data,
            params=parsed_params,
            files=file_data,
        )
        
        execution_time = time.time() - start_time
        
        return ScriptExecutionResponse(
            success=True,
            result=result,
            execution_time=execution_time,
        )
        
    except ValueError as e:
        execution_time = time.time() - start_time
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except ScriptExecutionError as e:
        execution_time = time.time() - start_time
        logger.error(f"Script execution error: {str(e)}")
        return ScriptExecutionResponse(
            success=False,
            error=str(e),
            execution_time=execution_time,
        )
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )

