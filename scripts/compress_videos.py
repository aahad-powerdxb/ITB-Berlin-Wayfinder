import os
import subprocess
import shutil

# ==========================================
# CONFIGURATION
# ==========================================

# 1. Media Directory: The root folder containing all the numbered subfolders
MEDIA_DIR = r"D:\Sandisk files\wayfinder\public\assets\media"

# 2. Targeted Folders List (Optional)
#    If this list is NOT empty, the script will ONLY process folders named in this list.
#    If this list is empty (e.g., TARGET_FOLDERS = []), it will process ALL folders recursively (default behavior).
#    Example: TARGET_FOLDERS = ["1", "10", "13", "B"]
TARGET_FOLDERS = ["17", "B", "C"] 

# 3. FFMPEG Path: If 'ffmpeg' is not in your system PATH, provide the full path to ffmpeg.exe
#    Example: r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_PATH = "ffmpeg" 

# 3. Target File Size Calculation
#    We want to aim for roughly 80MB for a 300MB file (approx 26% of original size).
#    A CRF of 23 is "visually lossless" but doesn't guarantee size.
#    Raising CRF to 28-30 will aggressively reduce quality and size.
#    Alternatively, we can set a target bitrate if we know duration, but CRF is simpler for batch.
CRF_VALUE = "28"  # Increased from 23 to 28 for more aggressive compression
PRESET_VALUE = "slow" # 'slow' gives better compression efficiency (smaller file at same quality)

# 4. Resize Option (Optional)
#    Scaling down 4K to 1080p or 1080p to 720p saves HUGE amounts of space.
#    Set to "1920:1080" or "1280:720" to force resize. Set to None to keep original resolution.
RESIZE_SCALE = "1920:1080" # Force 1080p max (preserves aspect ratio usually if used with -vf scale)



def compress_videos():
    print("--- Starting Video Compression Process ---")
    
    if not os.path.exists(MEDIA_DIR):
        print(f"❌ Error: Media directory does not exist: {MEDIA_DIR}")
        return

    # Check for ffmpeg availability
    try:
        subprocess.run([FFMPEG_PATH, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(f"❌ Error: 'ffmpeg' command not found. Please ensure FFMPEG is installed and added to your PATH, or update FFMPEG_PATH in the script.")
        return

    total_processed = 0
    total_skipped = 0
    total_errors = 0

    # Determine which directories to process
    if TARGET_FOLDERS:
        print(f"🎯 Processing only targeted folders: {TARGET_FOLDERS}")
        # Construct full paths for targeted folders
        dirs_to_process = []
        for folder_name in TARGET_FOLDERS:
            full_path = os.path.join(MEDIA_DIR, folder_name)
            if os.path.exists(full_path):
                dirs_to_process.append(full_path)
            else:
                print(f"⚠️ Warning: Targeted folder '{folder_name}' not found at {full_path}")
    else:
        print("🌍 Processing ALL folders in Media Directory (Recursive)")
        # If no target list, we'll walk the whole tree (handled by loop below)
        dirs_to_process = None

    # Helper function to process a single directory path
    def process_directory(directory_path):
        nonlocal total_processed, total_skipped, total_errors
        
        # Get list of files in this directory
        try:
            files = os.listdir(directory_path)
        except Exception as e:
            print(f"❌ Error accessing directory '{directory_path}': {e}")
            total_errors += 1
            return

        for file in files:
            # Check if the file is a video
            if file.lower().endswith(('.mp4', '.mov', '.mkv', '.avi', '.webm')):
                
                # We are looking for original video files to compress.
                name, ext = os.path.splitext(file)
                
                # Skip if the file ends with '1' (e.g., video1.mp4) to avoid re-compressing the output
                if name.endswith('1'):
                    continue

                input_path = os.path.join(directory_path, file)
                output_filename = f"{name}1{ext}"
                output_path = os.path.join(directory_path, output_filename)
                
                if os.path.exists(output_path):
                    print(f"⏭️  Skipping '{input_path}': Output file '{output_filename}' already exists.")
                    total_skipped += 1
                    continue

                print(f"🎬 Compressing: {input_path} -> {output_filename}")

                # Build the ffmpeg command
                command = [
                    FFMPEG_PATH,
                    "-i", input_path,
                    "-vcodec", "libx264",
                    "-crf", CRF_VALUE,
                    "-preset", PRESET_VALUE,
                ]

                # Add resizing filter if configured
                if RESIZE_SCALE:
                    command.extend(["-vf", f"scale='min(1920,iw)':-2"])

                command.extend([
                    "-acodec", "aac",
                    "-b:a", "128k", 
                    output_path
                ])
                
                try:
                    # Run ffmpeg
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully compressed '{file}'")
                        total_processed += 1
                    else:
                        print(f"❌ Error compressing '{file}': FFMPEG returned non-zero exit code.")
                        print(f"   Stderr: {result.stderr}")
                        total_errors += 1
                        
                except Exception as e:
                    print(f"❌ Exception while processing '{file}': {e}")
                    total_errors += 1

    # --- MAIN PROCESSING LOOP ---
    if TARGET_FOLDERS:
        # Loop through only the specific targeted folders
        for dir_path in dirs_to_process:
            process_directory(dir_path)
    else:
        # Loop through all directories recursively (original behavior)
        for root, dirs, files in os.walk(MEDIA_DIR):
            process_directory(root)

    print("\n--- Compression Summary ---")
    print(f"✅ Processed: {total_processed}")
    print(f"⏭️  Skipped: {total_skipped}")
    print(f"❌ Errors: {total_errors}")

if __name__ == "__main__":
    compress_videos()
