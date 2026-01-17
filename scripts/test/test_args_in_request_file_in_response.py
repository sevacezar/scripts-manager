"""Test script: receives JSON data and creates a file response."""

import json
import os
from pathlib import Path

# Access input data from global variable
input_data = globals().get("INPUT_DATA", {})

# Extract data
text = input_data.get("text", "Default text")
filename = input_data.get("filename", "output.txt")

# Create output file
output_dir = Path(input_data.get("_temp_dir", "/tmp"))
output_file = output_dir / filename
output_file.write_text(text, encoding="utf-8")

# Return file path in result
result = {
    "message": "File created successfully",
    "file_path": str(output_file),
    "file_size": output_file.stat().st_size,
}

# Output result as JSON
print(json.dumps(result))

