import json
import os
import re

# ==========================================
# CONFIGURATION
# ==========================================

# 1. Paths
#    The script assumes it is running from the project root or scripts folder
#    Adjust these absolute paths if necessary
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(PROJECT_ROOT, "src", "data", "basicDatas.json")
MEDIA_DIR_ITB = os.path.join(PROJECT_ROOT, "public", "assets", "media for ITB")

def sanitize_folder_name(name):
    """
    Sanitizes a string to be safe for use as a folder name.
    This function MUST be identical to the one in create_itb_media.py
    for an accurate comparison.
    """
    # Remove HTML tags like <br>
    name = re.sub(r'<[^>]+>', ' ', name)
    # Replace characters invalid in Windows/Linux filenames
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing whitespace and dots
    name = name.strip().strip('.')
    # Replace multiple spaces with a single space
    name = re.sub(r'\s+', ' ', name)
    return name

def verify_itb_media():
    print("--- Starting Verification for 'media for ITB' ---")

    # 1. Verify necessary files and folders exist
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: JSON file not found at {JSON_PATH}")
        return
    if not os.path.exists(MEDIA_DIR_ITB):
        print(f"❌ Error: 'media for ITB' directory not found at {MEDIA_DIR_ITB}")
        return

    # 2. Load JSON and generate the set of expected folder names
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        expected_folders = {sanitize_folder_name(entry['title']) for entry in data if 'title' in entry}
    except Exception as e:
        print(f"❌ Error reading or processing JSON file: {e}")
        return

    # 3. Get the set of actual folder names from the filesystem
    try:
        # We only want directories, so we filter the list
        actual_folders = {name for name in os.listdir(MEDIA_DIR_ITB) if os.path.isdir(os.path.join(MEDIA_DIR_ITB, name))}
    except Exception as e:
        print(f"❌ Error reading the 'media for ITB' directory: {e}")
        return

    # 4. Compare the two sets
    missing_folders = expected_folders - actual_folders
    extra_folders = actual_folders - expected_folders
    
    print("\n--- Verification Report ---")
    print(f"Expected Folders (from JSON): {len(expected_folders)}")
    print(f"Actual Folders (on disk):    {len(actual_folders)}")

    is_match = len(missing_folders) == 0 and len(extra_folders) == 0

    if is_match:
        print("\n✅ Success! All folders match the JSON entries perfectly.")
    else:
        print("\n❌ Mismatch found!")
        
        if missing_folders:
            print("\n-------------------------------------------------")
            print("Folders MISSING from 'media for ITB' directory:")
            print("-------------------------------------------------")
            for folder in sorted(list(missing_folders)):
                print(f"- {folder}")

        if extra_folders:
            print("\n-------------------------------------------------")
            print("Folders found that are NOT in basicDatas.json:")
            print("-------------------------------------------------")
            for folder in sorted(list(extra_folders)):
                print(f"- {folder}")

if __name__ == "__main__":
    verify_itb_media()
