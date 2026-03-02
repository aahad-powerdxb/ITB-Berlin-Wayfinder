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

def strip_html(html_content):
    """Removes HTML tags from a string."""
    return re.sub(r'<[^>]+>', ' ', html_content)

def find_source_folder(base_dir, booth_id):
    """
    Tries to find a source media folder, handling composite IDs.
    Example: for "7 & D", it first looks for "7 & D", then for "7".
    """
    # Attempt 1: Look for an exact match for the booth ID
    exact_path = os.path.join(base_dir, booth_id)
    if os.path.exists(exact_path):
        return exact_path, booth_id

    # Attempt 2: If it's a composite ID (e.g., "7 & D"), try the first part
    if ' & ' in booth_id:
        first_part = booth_id.split(' & ')[0].strip()
        first_part_path = os.path.join(base_dir, first_part)
        if os.path.exists(first_part_path):
            print(f"   ℹ️  Note: Exact folder '{booth_id}' not found. Using fallback '{first_part}'.")
            return first_part_path, first_part

    # If nothing is found
    return None, None

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
        booth_id_from_json = str(entry.get('booth', '')).strip()
        title = entry.get('title', 'Unknown Title')
        
        # If booth ID is missing, we can't find the source folder
        if not booth_id_from_json:
            print(f"⚠️ Skipping entry with no booth ID: {title}")
            continue

        # Sanitize the title for the new folder name
        new_folder_name = sanitize_folder_name(title)
        
        # Use the new robust function to find the source folder
        source_folder_path, found_folder_name = find_source_folder(SOURCE_MEDIA_DIR, booth_id_from_json)
        dest_folder = os.path.join(DEST_MEDIA_DIR, new_folder_name)

        # Check if source exists
        if source_folder_path is None:
            print(f"⏭️  Skipping: Source folder not found for booth '{booth_id_from_json}' (tried exact and fallback).")
            total_skipped += 1
            continue

        try:
            # Step 1: Ensure destination folder exists
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
                print(f"✅ Created folder: '{new_folder_name}'")

            # Step 2: Create content.txt if it doesn't exist
            content_path = os.path.join(dest_folder, "content.txt")
            if not os.path.exists(content_path):
                content_text = entry.get('content', '')
                plain_text = strip_html(content_text).strip()
                with open(content_path, 'w', encoding='utf-8') as f:
                    f.write(plain_text)
                print(f"   ✍️  Created content.txt in '{new_folder_name}'")

            # Step 3: Copy media files if they don't exist
            for filename in os.listdir(source_folder_path):
                source_file = os.path.join(source_folder_path, filename)
                dest_file = os.path.join(dest_folder, filename)
                
                if os.path.isfile(source_file): # Ensure we're copying files, not dirs
                    if not os.path.exists(dest_file):
                        shutil.copy2(source_file, dest_file)
                        print(f"   📥 Copied missing file: {filename}")
                    else:
                        # File already exists, can be logged if needed
                        # print(f"   👍 File already exists, skipping: {filename}")
                        pass
            
            total_processed += 1
            
        except Exception as e:
            print(f"❌ Error processing '{new_folder_name}': {e}")
            total_errors += 1

    print("\n--- Duplication Summary ---")
    print(f"✅ Folders Processed: {total_processed}")
    print(f"⏭️  Skipped (Source Missing): {total_skipped}")
    print(f"❌ Errors: {total_errors}")
    print(f"📂 Output Location: {DEST_MEDIA_DIR}")

if __name__ == "__main__":
    duplicate_and_rename_media()
