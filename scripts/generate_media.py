import os
import json
import difflib
import io
import time
import shutil
import sys
import gdown
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Configuration
API_KEY = 'AIzaSyD0cYkbDGqV_mjE30y1lysf4Y6-F5vmQ3k'  # Paste your API key here
ROOT_FOLDER_ID = '1MlwA5cMlEFHtNPVMp2Dbo1i_rMJQkiBO'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
JSON_FILE = os.path.join(SCRIPT_DIR, 'basicDatas.json')

MANUAL_OVERRIDES = {
    "les roches": "LES ROCHES",
    "aldar hospitality": "ALDAR",
    "teamlab phenomena": "TLP",
    "tourism365": "TOURISM365",
    "abu dhabi pass": "AD PASS",
    "al ain museum": "AL AIN MUSEUM",
    "al ain zoo": "AL AIN ZOO",
    "adrea": "ADREA",
    "arabian oryx travel & tourism llc": "Arabian Oryx",
    "gromaxx hotels management": "Gromaxx",
    "zayed international airport": "ZIA",
    "miral double booth (for ceo)": "Miral_CEO Booth",
    "abu dhabi national hotels": "ADNH",
    "aloft hotel abu dhabi": "Aloft AD",
    "anantara qasr al sarab desert resort": "Qasr Al Sarab",
    "bab al qasr \nhotel & residences": "Bab Al Qasr",
    "conrad abu dhabi eithad towers": "Conrad AD",
    "emirates palace mandarin oriental abu dhabi": "Emirates Palace"
}

def get_active_media_session():
    """Finds an incomplete session to resume, or creates a new directory."""
    base_path = os.path.join(PROJECT_ROOT, 'public', 'assets', 'media_new')
    parent_dir = os.path.dirname(base_path)
    
    existing_dirs = []
    if os.path.exists(parent_dir):
        existing_dirs = [d for d in os.listdir(parent_dir) if d.startswith('media_new')]
        
    def get_idx(name):
        if name == 'media_new': return 0
        try: return int(name.split('_')[-1])
        except: return -1
        
    existing_dirs.sort(key=get_idx)
    
    # Check the latest directory for a state file
    if existing_dirs:
        latest_dir = os.path.join(parent_dir, existing_dirs[-1])
        state_file = os.path.join(latest_dir, 'sync_state.json')
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                # If incomplete, return this directory and the booth to resume from
                if state.get('status') in ['in_progress', 'error']:
                    return latest_dir, str(state.get('current_booth'))
            except json.JSONDecodeError:
                pass
                
        # If latest is complete, determine the next folder name
        next_idx = get_idx(existing_dirs[-1]) + 1
        new_dir = f"{base_path}_{next_idx}"
    else:
        new_dir = base_path
        
    os.makedirs(new_dir, exist_ok=True)
    return new_dir, None

def update_state(media_dir, status, booth_id=None, error_msg=None):
    """Updates the sync_state.json log file."""
    state_file = os.path.join(media_dir, 'sync_state.json')
    state = {'status': status, 'current_booth': booth_id, 'error': error_msg}
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def execute_api_with_retry(request, max_retries=3):
    """Retries Google API calls if the network connection drops."""
    for attempt in range(max_retries):
        try:
            return request.execute()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)

def get_drive_folders(service, parent_id):
    query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    request = service.files().list(q=query, fields="files(id, name)", pageSize=1000)
    results = execute_api_with_retry(request)
    return results.get('files', [])

def get_all_files_recursively(service, folder_id, path=""):
    all_files = []
    query = f"'{folder_id}' in parents and trashed=false"
    request = service.files().list(q=query, fields="files(id, name, mimeType)", pageSize=1000)
    results = execute_api_with_retry(request)
    
    for item in results.get('files', []):
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            all_files.extend(get_all_files_recursively(service, item['id'], path + item['name'] + "/"))
        else:
            item['path'] = path
            all_files.append(item)
    return all_files

def classify_assets(files):
    logo = None
    media = None
    media_type = None 
    
    valid_img_exts = ['.png', '.jpg', '.jpeg']
    valid_vid_exts = ['.mp4', '.mov']
    ignore_exts = ['.ds_store', '.msg', '.ini', '.db', '.zip', '.pdf', '.ai']

    images = []

    for f in files:
        name_lower = f['name'].lower()
        ext = os.path.splitext(name_lower)[1]
        
        if ext in ignore_exts: continue
            
        # Classify Video
        if ext in valid_vid_exts:
            if not media or media_type == 'static':
                media = f
                media_type = 'video'
            continue
            
        # Collect all valid images
        if ext in valid_img_exts:
            images.append(f)
            
    # 1st Pass: Look for explicit logos (file or folder name contains "logo")
    for img in images:
        name_lower = img['name'].lower()
        path_lower = img['path'].lower()
        if 'logo' in name_lower or 'logo' in path_lower:
            if not logo: 
                logo = img
                break
                
    # 2nd Pass: If no explicit logo was found, just use the first available image
    if not logo and images:
        logo = images[0]
        
    # 3rd Pass: Assign a static image if we don't have a video
    if not media:
        for img in images:
            if img != logo:  # Don't reuse the logo as the static background
                media = img
                media_type = 'static'
                break
                
    return logo, media, media_type

def download_file(service, file_id, destination_path, max_retries=3):
    """Downloads using gdown, with a fallback to the official API if rate-limited."""
    part_file = destination_path + '.part'
    
    for attempt in range(max_retries):
        try:
            # 1. Try gdown first
            gdown.download(id=file_id, output=destination_path, quiet=True)
            
            if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                if os.path.exists(part_file): os.remove(part_file)
                return  
            else:
                raise Exception("gdown downloaded an empty file.")
                
        except Exception as e:
            print(f"      ⚠️ gdown blip on attempt {attempt+1}/{max_retries}. Trying official API fallback...")
            
            # TRASH CLEANUP
            if os.path.exists(destination_path): os.remove(destination_path)
            if os.path.exists(part_file): os.remove(part_file)
            
            # 2. Try Official API Fallback
            try:
                request = service.files().get_media(fileId=file_id)
                # Using 'with' automatically closes the file handle so it doesn't get locked in Windows!
                with io.FileIO(destination_path, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request, chunksize=5*1024*1024) 
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                
                if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                    return # Success via fallback!
            except Exception as api_e:
                print(f"      ⚠️ API fallback failed: {api_e}")
                # Now that 'fh' is safely closed, we can delete the corrupted file
                if os.path.exists(destination_path): os.remove(destination_path)
            
            # Give Google's rate limiter a longer 5-second cooldown breather
            time.sleep(5)  
            
            if attempt == max_retries - 1:
                print(f"      ❌ Failed completely to download: {destination_path}")
                raise Exception(f"Download failed after {max_retries} retries.")

def main():
    if not os.path.exists(JSON_FILE):
        print("basicDatas.json not found.")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        clients = json.load(f)

    service = build('drive', 'v3', developerKey=API_KEY)
    media_out_dir, resume_booth_id = get_active_media_session()
    
    if resume_booth_id:
        print(f"\n🔄 Resuming incomplete session in {os.path.basename(media_out_dir)} from booth {resume_booth_id}...")
        partial_booth_dir = os.path.join(media_out_dir, resume_booth_id)
        if os.path.exists(partial_booth_dir):
            shutil.rmtree(partial_booth_dir)
            print(f"🧹 Cleaned up partial/corrupted downloads for booth {resume_booth_id}")
    else:
        print(f"\n📁 Created new output directory: {os.path.basename(media_out_dir)}")

    print("Fetching Drive structure...")
    category_folders = get_drive_folders(service, ROOT_FOLDER_ID)
    
    drive_client_folders = []
    for cat in category_folders:
        drive_client_folders.extend(get_drive_folders(service, cat['id']))

    drive_folder_names = {f['name']: f for f in drive_client_folders}
    drive_lower_to_actual = {name.lower(): name for name in drive_folder_names.keys()}

    print("\nStarting Asset Download Phase...")
    skip = True if resume_booth_id else False

    try:
        for client in clients:
            client_title = client['title'].replace('<br>', ' ').strip()
            client_title_lower = client_title.lower()
            booth_id = str(client['id'])
            
            # Skip logic for resuming
            if skip:
                if booth_id == resume_booth_id:
                    skip = False
                else:
                    continue

            update_state(media_out_dir, 'in_progress', booth_id)
            matched_folder_name = None

            if client_title_lower in MANUAL_OVERRIDES:
                target = MANUAL_OVERRIDES[client_title_lower]
                if target in drive_folder_names:
                    matched_folder_name = target
            elif client_title_lower in drive_lower_to_actual:
                matched_folder_name = drive_lower_to_actual[client_title_lower]
            else:
                matches = difflib.get_close_matches(client_title, drive_folder_names.keys(), n=1, cutoff=0.6)
                if matches:
                    matched_folder_name = matches[0]

            if not matched_folder_name:
                print(f"⚠️  No Drive folder found for: '{client_title}' (Booth {booth_id}) -> Add to MANUAL_OVERRIDES!")
                continue
                
            folder_data = drive_folder_names[matched_folder_name]
            print(f"\n✅ Matched '{client_title}' -> Drive Folder: '{matched_folder_name}'")
            
            booth_dir = os.path.join(media_out_dir, booth_id)
            os.makedirs(booth_dir, exist_ok=True)
            
            all_files = get_all_files_recursively(service, folder_data['id'])
            logo_file, media_file, media_type = classify_assets(all_files)
            
            if logo_file:
                ext = os.path.splitext(logo_file['name'])[1].lower()
                dest = os.path.join(booth_dir, f"logo{ext}")
                print(f"   ⬇️  Downloading Logo: {logo_file['name']}")
                download_file(service, logo_file['id'], dest)
            else:
                print("   ❌ No Logo found.")
                
            if media_file:
                ext = os.path.splitext(media_file['name'])[1].lower()
                prefix = 'video' if media_type == 'video' else 'static'
                dest = os.path.join(booth_dir, f"{prefix}{ext}")
                print(f"   ⬇️  Downloading {prefix.title()}: {media_file['name']}")
                download_file(service, media_file['id'], dest)
            else:
                print("   ❌ No Video/Static media found.")

        # If loop finishes without raising exceptions, mark complete
        update_state(media_out_dir, 'complete', None)
        print(f"\n🎉 All done! Check your new media folder at: {media_out_dir}")

    except Exception as e:
        print(f"\n🛑 Script stopped due to an error: {e}")
        update_state(media_out_dir, 'error', booth_id, str(e))
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Script interrupted by user.")
        update_state(media_out_dir, 'error', booth_id, "Manually aborted")
        sys.exit(1)

if __name__ == '__main__':
    main()