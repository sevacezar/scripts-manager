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
    Validate script content - check for main function with one dict argument.
    
    Args:
        content: Script content as string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Parse AST for safe validation
        tree: ast.Module = ast.parse(content)
        
        # Search for main function
        main_function = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                main_function = node
                break
        
        if not main_function:
            return False, "Скрипт должен содержать функцию 'main' с одним аргументом типа dict"
        
        # Check that main has exactly one argument
        args = main_function.args.args
        if len(args) != 1:
            return False, "Функция 'main' должна принимать ровно один аргумент типа dict"
        
        # Check that the argument has type annotation (dict or Dict)
        arg = args[0]
        if arg.annotation:
            # Check if annotation is dict or Dict
            is_dict_type = False
            if isinstance(arg.annotation, ast.Name):
                # dict or Dict
                is_dict_type = arg.annotation.id in ('dict', 'Dict')
            elif isinstance(arg.annotation, ast.Subscript):
                # dict[...] or Dict[...]
                if isinstance(arg.annotation.value, ast.Name):
                    is_dict_type = arg.annotation.value.id in ('dict', 'Dict')
            
            if not is_dict_type:
                return False, "Аргумент функции 'main' должен иметь тип dict"
        
        return True, None
        
    except SyntaxError as e:
        # Format syntax error message with line number and details
        error_msg = "Неверный синтаксис Python"
        if e.lineno:
            error_msg += f" на строке {e.lineno}"
        if e.offset:
            error_msg += f", позиция {e.offset}"
        if e.text:
            error_msg += f":\n{e.text.rstrip()}"
            if e.offset:
                # Add caret indicator pointing to the error position
                indent = ' ' * (e.offset - 1)
                error_msg += f"\n{indent}^"
        if e.msg:
            error_msg += f"\n{e.msg}"
        return False, error_msg
    except Exception as e:
        logger.error("Script validation error", error=str(e))
        return False, f"Ошибка валидации: {str(e)}"

