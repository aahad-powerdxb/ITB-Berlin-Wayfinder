import os

def create_folders(base_path):
    if not os.path.exists(base_path):
        print(f"Error: Base path not found: {base_path}")
        return

    # Range 1-35
    for i in range(1, 36):
        folder_name = str(i)
        folder_path = os.path.join(base_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created: {folder_path}")
        else:
            print(f"Skipped (Exists): {folder_path}")

    # Range A-E
    # ASCII value for 'A' is 65, 'E' is 69
    for i in range(65, 70):
        folder_name = chr(i)
        folder_path = os.path.join(base_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created: {folder_path}")
        else:
            print(f"Skipped (Exists): {folder_path}")

if __name__ == "__main__":
    # Adjust path relative to project root
    target_dir = os.path.join("public", "assets", "images", "maps")
    
    # Check if running from scripts/ or root
    if not os.path.exists(target_dir) and os.path.exists(os.path.join("..", target_dir)):
        target_dir = os.path.join("..", target_dir)

    print(f"Creating folders in: {target_dir}")
    create_folders(target_dir)
    print("Done.")
