import json
import os
import shutil
import re

# ==========================================
# CONFIGURATION
# ==========================================

# 1. Paths
#    The script assumes it is running from the project root or scripts folder
#    Adjust these absolute paths if necessary
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(PROJECT_ROOT, "src", "data", "basicDatas.json")
SOURCE_MEDIA_DIR = os.path.join(PROJECT_ROOT, "public", "assets", "media")
DEST_MEDIA_DIR = os.path.join(PROJECT_ROOT, "public", "assets", "media for ITB")

def sanitize_folder_name(name):
    """
    Sanitizes a string to be safe for use as a folder name.
    Replaces invalid characters with underscores or removes them.
    Also handles <br> tags often found in titles.
    """
    # Remove HTML tags like <br>
    name = re.sub(r'<[^>]+>', ' ', name)
    
    # Replace characters invalid in Windows/Linux filenames
    # Invalid chars: < > : " / \ | ? *
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    
    # Remove leading/trailing whitespace and dots
    name = name.strip().strip('.')
    
    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name)
    
    return name

def duplicate_and_rename_media():
    print("--- Starting Media Duplication for ITB ---")
    
    # 1. Verify source existence
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: JSON file not found at {JSON_PATH}")
        return
    if not os.path.exists(SOURCE_MEDIA_DIR):
        print(f"❌ Error: Source media directory not found at {SOURCE_MEDIA_DIR}")
        return

    # 2. Load JSON Data
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return

    # 3. Create Destination Directory
    if not os.path.exists(DEST_MEDIA_DIR):
        try:
            os.makedirs(DEST_MEDIA_DIR)
            print(f"✅ Created destination directory: {DEST_MEDIA_DIR}")
        except OSError as e:
            print(f"❌ Error creating destination directory: {e}")
            return

    total_processed = 0
    total_skipped = 0
    total_errors = 0

    # 4. Process each entry
    for entry in data:
        booth_id = str(entry.get('booth', '')).strip()
        title = entry.get('title', 'Unknown Title')
        
        # If booth ID is missing, we can't find the source folder
        if not booth_id:
            print(f"⚠️ Skipping entry with no booth ID: {title}")
            continue

        # Sanitize the title for the new folder name
        new_folder_name = sanitize_folder_name(title)
        
        # Define Source and Destination Paths
        source_folder = os.path.join(SOURCE_MEDIA_DIR, booth_id)
        dest_folder = os.path.join(DEST_MEDIA_DIR, new_folder_name)

        # Check if source exists
        if not os.path.exists(source_folder):
            print(f"⏭️  Skipping: Source folder '{booth_id}' not found for '{title}'")
            total_skipped += 1
            continue
            
        print(f"📂 Copying: '{booth_id}' -> '{new_folder_name}'")

        try:
            # Copy the entire directory tree
            # shutil.copytree requires the destination dir to NOT exist
            if os.path.exists(dest_folder):
                print(f"   ⚠️ Destination '{new_folder_name}' already exists. Merging/Overwriting...")
                # If it exists, we use copy_tree from distutils or handle manual copy
                # Ideally, we remove it first or use dirs_exist_ok=True (Python 3.8+)
                shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
            else:
                shutil.copytree(source_folder, dest_folder)
                
            total_processed += 1
            
        except Exception as e:
            print(f"❌ Error copying to '{new_folder_name}': {e}")
            total_errors += 1

    print("\n--- Duplication Summary ---")
    print(f"✅ Folders Created: {total_processed}")
    print(f"⏭️  Skipped (Source Missing): {total_skipped}")
    print(f"❌ Errors: {total_errors}")
    print(f"📂 Output Location: {DEST_MEDIA_DIR}")

if __name__ == "__main__":
    duplicate_and_rename_media()
