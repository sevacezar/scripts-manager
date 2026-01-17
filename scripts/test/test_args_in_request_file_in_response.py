"""Test script: receives JSON data with file key and creates a file response."""

import json
from pathlib import Path

def main(data: dict) -> dict:
    """
    Main function that processes data and creates a file.
    
    Args:
        data: Input JSON data as dictionary, may contain file_key
        
    Returns:
        Dictionary with file key for created file
    """
    # Extract data
    text: str = data.get("text", "Default text")
    filename: str = data.get("filename", "output.txt")
    
    # In real scenario, you would use file_storage client
    # For this example, we just return the file info
    # The actual file creation would be done via file storage API
    
    result: dict = {
        "message": "File would be created",
        "filename": filename,
        "text_length": len(text),
        "note": "Use file storage API to actually save the file",
    }
    
    return result
