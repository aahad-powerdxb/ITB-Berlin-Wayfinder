import os

def normalize_filenames(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # Check if the filename is 'Video' or 'Logo' (case-insensitive)
            # but preserve the extension
            name, ext = os.path.splitext(filename)
            
            if name.lower() == 'video':
                new_name = 'video' + ext
            elif name.lower() == 'logo':
                new_name = 'logo' + ext
            elif name.lower() == 'static':
                new_name = 'static' + ext
            else:
                continue

            # If the filename is already correct, skip it
            if filename == new_name:
                continue

            old_path = os.path.join(root, filename)
            new_path = os.path.join(root, new_name)

            # Rename the file
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_name}")
            except OSError as e:
                print(f"Error renaming {old_path}: {e}")

if __name__ == "__main__":
    # Adjust the path to match your project structure
    # This assumes the script is run from the project root or the scripts/ folder
    # and targets public/assets/media
    target_dir = os.path.join("public", "assets", "media")
    
    # If running from scripts/ folder, go up one level first
    if not os.path.exists(target_dir) and os.path.exists(os.path.join("..", target_dir)):
        target_dir = os.path.join("..", target_dir)

    if os.path.exists(target_dir):
        print(f"Scanning directory: {target_dir}")
        normalize_filenames(target_dir)
        print("Filename normalization complete.")
    else:
        print(f"Error: Directory not found: {target_dir}")
