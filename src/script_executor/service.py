"""Service for executing Python scripts safely."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.logger import get_logger
from src.scripts_manager.service import ScriptsManagerService

logger = get_logger(__name__)


class ScriptExecutionError(Exception):
    """Exception raised when script execution fails."""

    pass


class ScriptExecutorService:
    """Service for executing Python scripts with input data."""

    def __init__(self):
        """Initialize script executor service."""
        self.scripts_dir = settings.scripts_dir.resolve()
        self.max_execution_time = settings.max_script_execution_time
        self.scripts_manager = ScriptsManagerService()

    async def _get_script_storage_path(
        self,
        db: AsyncSession,
        logical_path: str,
    ) -> Path:
        """
        Get script storage path by logical path.
        
        Args:
            db: Database session
            logical_path: Logical path (e.g., "geology/test.py")
            
        Returns:
            Absolute path to script file
            
        Raises:
            ValueError: If script not found
        """
        # Get script from DB by logical path
        script = await self.scripts_manager.get_script_by_logical_path(db, logical_path)
        
        if not script:
            raise ValueError(f"Script '{logical_path}' not found")
        
        # Build storage path
        storage_path: Path = self.scripts_dir / script.storage_filename
        
        # Check if file exists
        if not storage_path.exists():
            raise ValueError(f"Script file '{script.storage_filename}' not found in filesystem")
        
        # Check file extension
        if storage_path.suffix not in settings.allowed_script_extensions:
            raise ValueError(
                f"Script '{logical_path}' has invalid extension. "
                f"Allowed: {settings.allowed_script_extensions}"
            )
        
        return storage_path

    def _prepare_script_input(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare input data for script execution.
        
        Args:
            data: JSON data to pass to main() function
            
        Returns:
            Dictionary with prepared input data
        """
        # Data is passed as-is to main() function
        return data

    def _create_wrapper_script(
        self,
        script_path: Path,
        input_data: dict[str, Any],
    ) -> Path:
        """
        Create wrapper script that calls main() function from target script.
        
        Args:
            script_path: Path to target script
            input_data: Data to pass to main() function
            
        Returns:
            Path to wrapper script
        """
        wrapper_content: str = f'''import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(r"{script_path.parent}").resolve()))

# Import and execute target script
import importlib.util
spec = importlib.util.spec_from_file_location("user_script", r"{script_path}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Check if main function exists
if not hasattr(module, "main"):
    raise ValueError("Script must contain a 'main' function")

# Call main function with input data
input_data = {json.dumps(input_data, indent=2)}
result = module.main(input_data)

# Output result as JSON
if result is not None:
    if not isinstance(result, dict):
        raise ValueError("main() function must return a dict or None")
    print(json.dumps(result))
'''
        
        # Create temporary wrapper script
        temp_wrapper: tempfile._TemporaryFileWrapper[str] = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        )
        temp_wrapper.write(wrapper_content)
        temp_wrapper.close()
        
        return Path(temp_wrapper.name)

    async def execute_script(
        self,
        db: AsyncSession,
        logical_path: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute Python script by calling its main() function.
        
        Args:
            db: Database session
            logical_path: Logical path to script (e.g., "geology/test.py")
            data: JSON data to pass to script's main() function
            
        Returns:
            Dictionary with execution result (return value from main())
            
        Raises:
            ScriptExecutionError: If execution fails
        """
        validated_path: Path = await self._get_script_storage_path(db, logical_path)
        input_data: dict[str, Any] = self._prepare_script_input(data)
        wrapper_script: Path | None = None
        
        try:
            # Create wrapper script
            wrapper_script = self._create_wrapper_script(validated_path, input_data)
            
            # Execute script
            logger.info("Executing script", logical_path=logical_path)
            
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [sys.executable, str(wrapper_script)],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time,
                cwd=str(self.scripts_dir),
            )
            
            if result.returncode != 0:
                error_msg: str = result.stderr or result.stdout or "Unknown error"
                logger.error("Script execution failed", logical_path=logical_path, error=error_msg)
                raise ScriptExecutionError(f"Script execution failed: {error_msg}")
            
            # Parse JSON output from stdout
            output: str = result.stdout.strip()
            result_data: dict[str, Any]
            if output:
                try:
                    result_data = json.loads(output)
                    if not isinstance(result_data, dict):
                        raise ScriptExecutionError(
                            "Script main() function must return a dict or None"
                        )
                except json.JSONDecodeError as e:
                    raise ScriptExecutionError(f"Script output is not valid JSON: {str(e)}")
            else:
                # If no output, assume None was returned
                result_data = {}
            
            logger.info("Script executed successfully", logical_path=logical_path)
            return result_data
            
        except subprocess.TimeoutExpired:
            raise ScriptExecutionError(
                f"Script execution timeout after {self.max_execution_time} seconds"
            )
        except ScriptExecutionError:
            raise
        except Exception as e:
            logger.error("Error executing script", logical_path=logical_path, error=str(e))
            raise ScriptExecutionError(f"Error executing script: {str(e)}")
        finally:
            # Clean up wrapper script
            if wrapper_script and wrapper_script.exists():
                wrapper_script.unlink()

