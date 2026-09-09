from googleapiclient.discovery import build
import sys

# The folder ID extracted from your link
FOLDER_ID = '1MlwA5cMlEFHtNPVMp2Dbo1i_rMJQkiBO'
API_KEY = 'AIzaSyD0cYkbDGqV_mjE30y1lysf4Y6-F5vmQ3k'  # Paste your API key here

def print_tree(service, folder_id, indent=0):
    """Recursively fetches and prints the folder structure."""
    try:
        # Query files and folders inside the current folder
        query = f"'{folder_id}' in parents and trashed = false"
        # We only need the name, mimeType (to check if it's a folder), and id
        results = service.files().list(
            q=query, 
            fields="files(id, name, mimeType)",
            pageSize=1000
        ).execute()
        
        items = results.get('files', [])

        if not items and indent == 0:
            print("Folder is empty or inaccessible.")
            return

        # Sort items: folders first, then files
        items.sort(key=lambda x: (x['mimeType'] != 'application/vnd.google-apps.folder', x['name']))

        for item in items:
            is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'
            prefix = "📁 " if is_folder else "📄 "
            print(' ' * indent + prefix + item['name'])
            
            # If it's a folder, dive into it
            if is_folder:
                print_tree(service, item['id'], indent + 4)
                
    except Exception as e:
        print(' ' * indent + f"[Error reading folder: {e}]")

def main():
    if API_KEY == 'YOUR_API_KEY_HERE':
        print("Please insert your Google Cloud API Key into the script.")
        sys.exit(1)
        
    print("Connecting to Google Drive and mapping folder structure...")
    print("This might take a moment depending on how many files there are.\n")
    
    # Build the Drive service using just the API key (no OAuth login required for public folders)
    service = build('drive', 'v3', developerKey=API_KEY)
    
    print("📁 Root (1MlwA5cMlEFHtNPVMp2Dbo1i_rMJQkiBO)")
    print_tree(service, FOLDER_ID, indent=4)

if __name__ == '__main__':
    main()