import os
import shutil

# ==========================================
# CONFIGURATION
# ==========================================

# 1. Media Directory: The root folder containing all the numbered subfolders
MEDIA_DIR = r"D:\Sandisk files\wayfinder\public\assets\media"

def swap_video_names():
    print("--- Starting Video Name Swap Process ---")
    
    if not os.path.exists(MEDIA_DIR):
        print(f"❌ Error: Media directory does not exist: {MEDIA_DIR}")
        return

    total_swapped = 0
    total_skipped = 0
    total_errors = 0

    # Walk through all directories in MEDIA_DIR
    for root, dirs, files in os.walk(MEDIA_DIR):
        # Identify pairs of video files to swap
        video_file = None
        video1_file = None
        
        # Look for video files in the current directory
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in ('.mp4', '.mov', '.mkv', '.avi', '.webm'):
                if name == 'video':
                    video_file = file
                elif name == 'video1':
                    video1_file = file
        
        # Only proceed if we found BOTH files or at least one of them
        if video_file and video1_file:
            # Full paths
            path_video = os.path.join(root, video_file)
            path_video1 = os.path.join(root, video1_file)
            
            # Temporary name to facilitate swap
            temp_name = f"temp_swap_{video_file}"
            path_temp = os.path.join(root, temp_name)
            
            try:
                # Rename video.mp4 -> temp_swap_video.mp4
                os.rename(path_video, path_temp)
                
                # Rename video1.mp4 -> video.mp4
                os.rename(path_video1, path_video)
                
                # Rename temp_swap_video.mp4 -> video1.mp4
                os.rename(path_temp, path_video1)
                
                print(f"✅ Swapped: {root} -> '{video_file}' <-> '{video1_file}'")
                total_swapped += 1
                
            except Exception as e:
                print(f"❌ Error swapping in '{root}': {e}")
                # Attempt to rollback if something failed mid-way (basic rollback logic)
                if os.path.exists(path_temp) and not os.path.exists(path_video):
                     try:
                         os.rename(path_temp, path_video)
                         print("   (Rolled back changes)")
                     except:
                         pass
                total_errors += 1

        elif video_file and not video1_file:
            print(f"⏭️  Skipping '{root}': Found '{video_file}' but missing 'video1{os.path.splitext(video_file)[1]}'.")
            total_skipped += 1
            
        elif not video_file and video1_file:
            # If only video1 exists, it might mean we already swapped and the "original" is missing?
            # Or maybe just rename video1 to video?
            # For safety, let's just log it.
             print(f"⏭️  Skipping '{root}': Found '{video1_file}' but missing 'video{os.path.splitext(video1_file)[1]}'.")
             total_skipped += 1

    print("\n--- Swap Summary ---")
    print(f"✅ Folders Swapped: {total_swapped}")
    print(f"⏭️  Folders Skipped: {total_skipped}")
    print(f"❌ Errors: {total_errors}")

if __name__ == "__main__":
    swap_video_names()
