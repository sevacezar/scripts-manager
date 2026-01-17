"""Test script: receives file key in data and processes it."""

def main(data: dict) -> dict:
    """
    Main function that processes file key from input data.
    
    Args:
        data: Input JSON data as dictionary, should contain file_key
        
    Returns:
        Dictionary with processing result
    """
    # Get file key from input data
    file_key: str | None = data.get("file_key")
    
    if not file_key:
        return {
            "error": "file_key is required in input data",
            "message": "Upload file first using /api/v1/files/upload endpoint",
        }
    
    # In real scenario, you would download file using file_storage client
    # For this example, we just return the file key info
    
    result: dict = {
        "message": f"File key received: {file_key}",
        "file_key": file_key,
        "note": "Download file using /api/v1/files/{key} endpoint",
        "processing": "File would be processed here",
    }
    
    return result
