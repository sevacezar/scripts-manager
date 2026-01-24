"""Router for script execution endpoints."""

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.logger import get_logger
from src.script_executor.schemas import (
    ScriptExecutionRequest,
    ScriptExecutionResponse,
)
from src.script_executor.service import ScriptExecutionError, ScriptExecutorService


logger = get_logger(__name__)
router = APIRouter(prefix="/scripts", tags=["scripts"])

# Initialize service
script_executor: ScriptExecutorService = ScriptExecutorService()


@router.post(
    "/{script_path:path}",
    response_model=ScriptExecutionResponse,
    summary="Execute Python script",
    description=(
        "Execute a Python script from the scripts directory. "
        "Script must contain a 'main(data: dict) -> dict' function. "
        "Receives JSON in request body, returns JSON in response."
    ),
)
async def execute_script(
    script_path: str,
    request: ScriptExecutionRequest,
    db: AsyncSession = Depends(get_db),
) -> ScriptExecutionResponse:
    """
    Execute a Python script by calling its main() function.
    
    Script requirements:
    - Must be a single .py file
    - Must contain a function: def main(data: dict) -> dict
    - Function receives JSON data as dict
    - Function must return a dict (or None, which becomes empty dict)
    
    Example script:
    ```python
    def main(data: dict) -> dict:
        name = data.get("name", "Unknown")
        return {"message": f"Hello, {name}!"}
    ```
    
    Args:
        script_path: Logical path to script (e.g., "geology/test.py")
        request: ScriptExecutionRequest with data dict
        db: Database session
        
    Returns:
        ScriptExecutionResponse with execution result
        
    Raises:
        HTTPException: If script execution fails
    """
    start_time: float = time.time()
    
    try:
        # Execute script
        result: dict = await script_executor.execute_script(
            db=db,
            logical_path=script_path,
            data=request.data,
        )
        
        execution_time: float = time.time() - start_time
        
        return ScriptExecutionResponse(
            success=True,
            result=result,
            execution_time=execution_time,
        )
        
    except ValueError as e:
        execution_time: float = time.time() - start_time
        logger.error("Validation error", error=str(e), script_path=script_path)
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except ScriptExecutionError as e:
        execution_time: float = time.time() - start_time
        logger.error("Script execution error", error=str(e), script_path=script_path)
        return ScriptExecutionResponse(
            success=False,
            error=str(e),
            execution_time=execution_time,
        )
    except Exception as e:
        execution_time: float = time.time() - start_time
        logger.error("Unexpected error", error=str(e), script_path=script_path, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )
