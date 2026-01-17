"""Test script: receives JSON data and returns JSON response."""

import json

# Access input data from global variable
input_data = globals().get("INPUT_DATA", {})

# Extract data
name = input_data.get("name", "Unknown")
value = input_data.get("value", 0)

# Process data
result = {
    "message": f"Hello, {name}!",
    "processed_value": value * 2,
    "received_data": input_data,
}

# Output result as JSON (script executor will capture this)
print(json.dumps(result))

