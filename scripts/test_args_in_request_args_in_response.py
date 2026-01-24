"""Test script: receives JSON data and returns JSON response."""

def main(data: dict) -> dict:
    """
    Main function that processes input data.
    
    Args:
        data: Input JSON data as dictionary
        
    Returns:
        Dictionary with processed result
    """
    # Extract data
    name: str = data.get("name", "Unknown")
    value: int = data.get("value", 0)
    
    # Process data
    result: dict = {
        "message": f"Hello, {name}!",
        "processed_value": value * 2,
        "received_data": data,
    }
    
    return result
