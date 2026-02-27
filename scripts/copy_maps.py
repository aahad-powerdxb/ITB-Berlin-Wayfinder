import os
import shutil
import re

# ==========================================
# CONFIGURATION
# ==========================================

# 1. Source Directory: Where your Map-XX.png files are located
SOURCE_DIR = r"C:\Users\AHAD_PC\Downloads\Map lines-20260224T072944Z-3-001\Map lines"

# 2. Destination Directory: The root folder containing the booth folders (1, 2, 7 & D, etc.)
DEST_DIR = r"D:\Sandisk files\wayfinder\public\assets\images\maps"


def normalize_booth_id(raw_id):
    """
    Normalizes the booth ID from the filename to match the folder name.
    
    Examples:
    "01" -> "1"
    "07&D" -> "7 & D"
    "13&A" -> "13 & A"
    "B" -> "B"
    """
    # Remove leading zeros for single digits (e.g., "01" -> "1")
    # But keep "10", "20", etc.
    if raw_id.isdigit():
        return str(int(raw_id))
    
    # Handle combined booth IDs with ampersands (e.g., "07&D", "13&A")
    if '&' in raw_id:
        parts = raw_id.split('&')
        # Normalize the first part (often a number like "07" -> "7")
        first_part = parts[0]
        if first_part.isdigit():
            first_part = str(int(first_part))
        
        # Reconstruct with spaces around the ampersand to match folder structure "7 & D"
        return f"{first_part} & {parts[1]}"
        
    return raw_id

def process_maps():
    print("--- Starting Map Copy Process ---")
    
    # Verify directories exist
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Error: Source directory does not exist: {SOURCE_DIR}")
        return
    if not os.path.exists(DEST_DIR):
        print(f"❌ Error: Destination directory does not exist: {DEST_DIR}")
        return

    # Get list of png files in source
    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith('.png') and f.startswith('Map-')]
    
    if not files:
        print("⚠️ No matching 'Map-*.png' files found in source directory.")
        return

    copied_count = 0
    skipped_count = 0
    error_count = 0

    for filename in files:
        # Extract the raw ID part from "Map-<ID>.png"
        # We strip "Map-" from the start and ".png" from the end
        raw_id = filename[4:-4]
        
        # Normalize to match folder names
        folder_name = normalize_booth_id(raw_id)
        
        # Construct full paths
        source_path = os.path.join(SOURCE_DIR, filename)
        target_folder = os.path.join(DEST_DIR, folder_name)
        target_path = os.path.join(target_folder, "1.png")
        
        # Check if the destination folder exists
        if not os.path.exists(target_folder):
            print(f"⚠️ Warning: Destination folder '{folder_name}' not found for file '{filename}'. Skipping.")
            error_count += 1
            continue
            
        # Check if 1.png already exists
        if os.path.exists(target_path):
            print(f"⏭️  Skipping '{folder_name}': '1.png' already exists.")
            skipped_count += 1
            continue
            
        # Copy the file
        try:
            shutil.copy2(source_path, target_path)
            print(f"✅ Copied '{filename}' to '{target_folder}\\1.png'")
            copied_count += 1
        except Exception as e:
            print(f"❌ Error copying '{filename}': {e}")
            error_count += 1

    print("\n--- Summary ---")
    print(f"Total Files Processed: {len(files)}")
    print(f"✅ Copied: {copied_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"⚠️ Errors/Missing Folders: {error_count}")

if __name__ == "__main__":
    process_maps()
