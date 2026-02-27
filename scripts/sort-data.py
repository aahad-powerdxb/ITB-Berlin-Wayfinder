import json
import os

# Define the path to the JSON file relative to the project root
# os.path.dirname(__file__) gets the directory of the script ('scripts')
# os.path.join(..., '..') goes up one level to the project root
project_root = os.path.join(os.path.dirname(__file__), '..')
json_file_path = os.path.join(project_root, 'src', 'data', 'basicDatas.json')

try:
    # --- Read the file ---
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- Separate entries into numeric and alphabetic ID lists ---
    numeric_entries = []
    alpha_entries = []

    for item in data:
        # Check if the 'id' is an integer
        if isinstance(item.get('id'), int):
            numeric_entries.append(item)
        else:
            alpha_entries.append(item)

    # --- Sort each list independently ---
    # Sort numeric entries by the 'id' value
    numeric_entries.sort(key=lambda x: x['id'])
    # Sort alphabetic entries by the 'id' value
    alpha_entries.sort(key=lambda x: str(x.get('id', '')))

    # --- Combine the sorted lists ---
    sorted_data = numeric_entries + alpha_entries

    # --- Write the sorted data back to the file ---
    with open(json_file_path, 'w', encoding='utf-8') as f:
        # indent=2 makes the JSON file readable (pretty-print)
        json.dump(sorted_data, f, indent=2)

    print("✅ Successfully sorted basicDatas.json by ID.")

except FileNotFoundError:
    print(f"❌ Error: The file was not found at {json_file_path}")
except json.JSONDecodeError:
    print(f"❌ Error: Could not decode JSON from the file. Please check for syntax errors.")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")