"""Service for executing Python scripts safely."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

from src.config import settings
from src.logger import logger


class ScriptExecutionError(Exception):
    """Exception raised when script execution fails."""

    pass


class ScriptExecutorService:
    """Service for executing Python scripts with input data."""

    def __init__(self):
        """Initialize script executor service."""
        self.scripts_dir = settings.scripts_dir.resolve()
        self.max_execution_time = settings.max_script_execution_time

    def _validate_script_path(self, script_path: str) -> Path:
        """
        Validate and resolve script path.
        
        Args:
            script_path: Relative path to script from scripts directory
            
        Returns:
            Absolute path to script
            
        Raises:
            ValueError: If path is invalid or script doesn't exist
        """
        # Normalize path (remove leading slashes, resolve ..)
        normalized_path = script_path.lstrip("/")
        
        # Resolve absolute path
        absolute_path = (self.scripts_dir / normalized_path).resolve()
        
        # Security check: ensure path is within scripts directory
        try:
            absolute_path.relative_to(self.scripts_dir)
        except ValueError:
            raise ValueError(f"Script path '{script_path}' is outside scripts directory")
        
        # Check if file exists
        if not absolute_path.exists():
            raise ValueError(f"Script '{script_path}' not found")
        
        # Check file extension
        if absolute_path.suffix not in settings.allowed_script_extensions:
            raise ValueError(
                f"Script '{script_path}' has invalid extension. "
                f"Allowed: {settings.allowed_script_extensions}"
            )
        
        return absolute_path

    def _prepare_script_input(
        self,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, str]] = None,
        files: Optional[dict[str, bytes]] = None,
    ) -> dict[str, Any]:
        """
        Prepare input data for script execution.
        
        Args:
            json_data: JSON data to pass
            params: Additional string parameters
            files: Uploaded files as bytes
            
        Returns:
            Dictionary with prepared input data
        """
        input_data: dict[str, Any] = {}
        
        if json_data:
            input_data.update(json_data)
        
        if params:
            input_data.update(params)
        
        if files:
            # Store files in temporary directory and pass paths
            temp_dir = tempfile.mkdtemp()
            file_paths = {}
            for filename, file_content in files.items():
                temp_file_path = Path(temp_dir) / filename
                temp_file_path.write_bytes(file_content)
                file_paths[filename] = str(temp_file_path)
            input_data["_files"] = file_paths
            input_data["_temp_dir"] = temp_dir
        
        return input_data

    def _create_wrapper_script(
        self,
        script_path: Path,
        input_data: dict[str, Any],
    ) -> Path:
        """
        Create wrapper script that injects input data and executes target script.
        
        Args:
            script_path: Path to target script
            input_data: Data to inject into script
            
        Returns:
            Path to wrapper script
        """
        wrapper_content = f'''import sys
import json
import os
from pathlib import Path

# Inject input data as global variable
INPUT_DATA = {json.dumps(input_data, indent=2)}

# Make INPUT_DATA available to target script
globals().update({{"INPUT_DATA": INPUT_DATA}})

# Add scripts directory to path
sys.path.insert(0, str(Path(r"{script_path.parent}").resolve()))

# Execute target script
with open(r"{script_path}", "r", encoding="utf-8") as f:
    code = compile(f.read(), r"{script_path}", "exec")
    exec(code, globals())
'''
        
        # Create temporary wrapper script
        temp_wrapper = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        )
        temp_wrapper.write(wrapper_content)
        temp_wrapper.close()
        
        return Path(temp_wrapper.name)

    def execute_script(
        self,
        script_path: str,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, str]] = None,
        files: Optional[dict[str, bytes]] = None,
    ) -> dict[str, Any]:
        """
        Execute Python script with provided input data.
        
        Args:
            script_path: Relative path to script from scripts directory
            json_data: JSON data to pass to script
            params: Additional string parameters
            files: Uploaded files as bytes
            
        Returns:
            Dictionary with execution result
            
        Raises:
            ScriptExecutionError: If execution fails
        """
        validated_path = self._validate_script_path(script_path)
        input_data = self._prepare_script_input(json_data, params, files)
        wrapper_script = None
        
        try:
            # Create wrapper script
            wrapper_script = self._create_wrapper_script(validated_path, input_data)
            
            # Execute script
            logger.info(f"Executing script: {script_path}")
            
            result = subprocess.run(
                [sys.executable, str(wrapper_script)],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time,
                cwd=str(validated_path.parent),
            )
            
            # Clean up temporary files
            if input_data.get("_temp_dir"):
                shutil.rmtree(input_data["_temp_dir"], ignore_errors=True)
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                logger.error(f"Script execution failed: {error_msg}")
                raise ScriptExecutionError(f"Script execution failed: {error_msg}")
            
            # Try to parse JSON output from stdout
            output = result.stdout.strip()
            if output:
                try:
                    result_data = json.loads(output)
                except json.JSONDecodeError:
                    # If not JSON, return as string
                    result_data = output
            else:
                result_data = {"message": "Script executed successfully"}
            
            logger.info(f"Script executed successfully: {script_path}")
            return result_data
            
        except subprocess.TimeoutExpired:
            raise ScriptExecutionError(
                f"Script execution timeout after {self.max_execution_time} seconds"
            )
        except Exception as e:
            logger.error(f"Error executing script {script_path}: {str(e)}")
            raise ScriptExecutionError(f"Error executing script: {str(e)}")
        finally:
            # Clean up wrapper script
            if wrapper_script and wrapper_script.exists():
                wrapper_script.unlink()

