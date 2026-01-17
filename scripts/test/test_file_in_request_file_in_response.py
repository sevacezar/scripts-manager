"""Test script: receives file(s) and processes them, returns result."""

import json
from pathlib import Path

# Access input data from global variable
input_data = globals().get("INPUT_DATA", {})

# Get uploaded files
files = input_data.get("_files", {})

# Process files
processed_files = []
for filename, file_path in files.items():
    file_path_obj = Path(file_path)
    if file_path_obj.exists():
        content = file_path_obj.read_text(encoding="utf-8")
        processed_files.append({
            "filename": filename,
            "size": file_path_obj.stat().st_size,
            "lines": len(content.splitlines()),
            "preview": content[:100],  # First 100 characters
        })

# Return result
result = {
    "message": f"Processed {len(processed_files)} file(s)",
    "files": processed_files,
}

# Output result as JSON
print(json.dumps(result))

