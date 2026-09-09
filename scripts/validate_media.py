import os
import json

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
JSON_FILE = os.path.join(SCRIPT_DIR, 'basicDatas.json')

def get_latest_media_dir():
    """Finds the most recently created media_new folder."""
    base_path = os.path.join(PROJECT_ROOT, 'public', 'assets')
    if not os.path.exists(base_path):
        return None
        
    existing_dirs = [d for d in os.listdir(base_path) if d.startswith('media_new')]
    
    if not existing_dirs:
        return None
        
    def get_idx(name):
        if name == 'media_new': return 0
        try: return int(name.split('_')[-1])
        except: return -1
        
    existing_dirs.sort(key=get_idx)
    return os.path.join(base_path, existing_dirs[-1])

def main():
    if not os.path.exists(JSON_FILE):
        print("❌ Error: basicDatas.json not found!")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        clients = json.load(f)

    media_dir = get_latest_media_dir()
    if not media_dir:
        print("❌ Error: No media_new folder found in public/assets!")
        return

    print(f"🔍 Validating assets in: {media_dir}\n")

    missing_folders = []
    missing_logos = []
    missing_media = []

    valid_img_exts = ['.png', '.jpg', '.jpeg']
    valid_vid_exts = ['.mp4', '.mov']

    for client in clients:
        booth_id = str(client['id'])
        title = client['title'].replace('<br>', ' ').strip()
        
        booth_dir = os.path.join(media_dir, booth_id)
        
        # Check if the folder exists at all
        if not os.path.exists(booth_dir):
            missing_folders.append(f"Booth {booth_id} ({title})")
            continue
        
        files_in_dir = [f.lower() for f in os.listdir(booth_dir)]
        
        # Check for a valid logo
        has_logo = any(f.startswith('logo') and os.path.splitext(f)[1] in valid_img_exts for f in files_in_dir)
        if not has_logo:
            missing_logos.append(f"Booth {booth_id} ({title})")
            
        # Check for a valid video OR static background
        has_video = any(f.startswith('video') and os.path.splitext(f)[1] in valid_vid_exts for f in files_in_dir)
        has_static = any(f.startswith('static') and os.path.splitext(f)[1] in valid_img_exts for f in files_in_dir)
        
        if not (has_video or has_static):
            missing_media.append(f"Booth {booth_id} ({title})")

    # --- PRINT REPORT ---
    print("====== 📊 VALIDATION REPORT ======\n")
    
    if missing_folders:
        print(f"❌ MISSING FOLDERS ({len(missing_folders)}):")
        for m in missing_folders: print(f"   - {m}")
        print()
        
    if missing_logos:
        print(f"❌ MISSING LOGOS ({len(missing_logos)}):")
        for m in missing_logos: print(f"   - {m}")
        print()
        
    if missing_media:
        print(f"❌ MISSING VIDEO/STATIC ({len(missing_media)}):")
        for m in missing_media: print(f"   - {m}")
        print()
        
    if not missing_folders and not missing_logos and not missing_media:
        print("✅ ALL GOOD! Every client has a folder, a logo, and a media file.")
    else:
        print("⚠️ You can manually place missing assets into their respective booth folders.")

if __name__ == '__main__':
    main()