import os

# ==========================================
# CONFIGURATION
# ==========================================

# 1. Media Directory: The root folder containing all the numbered subfolders
MEDIA_DIR = r"D:\Sandisk files\wayfinder\public\assets\media"

def delete_video1_files():
    print("--- Starting Cleanup Process: Deleting 'video1.*' files ---")
    
    if not os.path.exists(MEDIA_DIR):
        print(f"❌ Error: Media directory does not exist: {MEDIA_DIR}")
        return

    total_deleted = 0
    total_skipped = 0
    total_errors = 0

    # Walk through all directories in MEDIA_DIR
    for root, dirs, files in os.walk(MEDIA_DIR):
        for file in files:
            # We are looking for files explicitly named 'video1' with any extension
            name, ext = os.path.splitext(file)
            
            if name == 'video1':
                full_path = os.path.join(root, file)
                
                try:
                    os.remove(full_path)
                    print(f"✅ Deleted: {full_path}")
                    total_deleted += 1
                except Exception as e:
                    print(f"❌ Error deleting '{full_path}': {e}")
                    total_errors += 1
            else:
                # Just for tracking, count files we are skipping
                pass

    print("\n--- Cleanup Summary ---")
    print(f"✅ Files Deleted: {total_deleted}")
    print(f"❌ Errors: {total_errors}")

if __name__ == "__main__":
    delete_video1_files()
