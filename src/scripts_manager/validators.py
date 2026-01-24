"""Validators for scripts."""

import ast
from pathlib import Path

from src.logger import get_logger

logger = get_logger(__name__)

# Service files/folders to ignore
SERVICE_PATTERNS: list[str] = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".git",
    ".DS_Store",
    "*.tmp",
    "*.swp",
    "*.bak",
]


def is_service_file(path: Path) -> bool:
    """
    Check if file/folder is a service file that should be ignored.
    
    Args:
        path: Path to check
        
    Returns:
        True if service file, False otherwise
    """
    name: str = path.name
    
    # Check exact matches
    if name in ["__pycache__", ".git", ".DS_Store"]:
        return True
    
    # Check extensions
    if path.suffix in [".pyc", ".pyo", ".pyd", ".tmp", ".swp", ".bak"]:
        return True
    
    return False


def validate_script_content(content: str) -> tuple[bool, str | None]:
    """
    Validate script content - check for main function.
    
    Args:
        content: Script content as string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Parse AST for safe validation
        tree: ast.Module = ast.parse(content)
        
        # Search for main function
        has_main: bool = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                has_main = True
                # Optional: check signature
                # For now, just check existence
                break
        
        if not has_main:
            return False, "Script must contain a 'main(data: dict) -> dict' function"
        
        return True, None
        
    except SyntaxError as e:
        return False, f"Invalid Python syntax: {str(e)}"
    except Exception as e:
        logger.error("Script validation error", error=str(e))
        return False, f"Validation error: {str(e)}"

