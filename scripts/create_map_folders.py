import os
import shutil
from pathlib import Path

def normalize_name(name):
    """
    Normalizes file and folder names so they can be accurately matched.
    Example: 'Map-lines_03.png' -> '3' | '7 & D' -> '7&d'
    """
    # Remove prefix and extension if present
    name = name.replace("Map-lines_", "").replace(".png", "")
    # Lowercase and remove any spaces
    name = name.lower().replace(" ", "")
    # Strip leading zeros (so '03' becomes '3')
    name = name.lstrip("0")
    return name

def main():
    # Define paths
    source_dir = Path(r"C:\Users\AHAD_PC\Downloads\Map-lines_v2-20260302T125449Z-3-001\Map-lines_v2")
    maps_dir = Path(r"D:\Sandisk files\wayfinder\public\assets\images\maps")
    maps1_dir = Path(r"D:\Sandisk files\wayfinder\public\assets\images\maps1")

    # Create the root maps1 directory
    maps1_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read all source files and map them using their normalized name
    source_files = {}
    if source_dir.exists():
        for file_path in source_dir.glob("*.png"):
            norm_key = normalize_name(file_path.name)
            source_files[norm_key] = file_path
    else:
        print(f"Source directory not found: {source_dir}")
        return

    # 2. Iterate through the existing 'maps' layout
    for folder in maps_dir.iterdir():
        if folder.is_dir():
            # Create the exact same subfolder in 'maps1'
            target_folder = maps1_dir / folder.name
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Normalize the folder name to see if we have a matching source image
            norm_folder_key = normalize_name(folder.name)
            
            # 3. If a match is found, copy it over and rename it to '1.png'
            if norm_folder_key in source_files:
                src_file = source_files[norm_folder_key]
                dest_file = target_folder / "1.png"
                
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {src_file.name} -> maps1\\{folder.name}\\1.png")
            else:
                print(f"Skipped: No source image found for folder '{folder.name}'. Folder was created empty.")

if __name__ == "__main__":
    main()