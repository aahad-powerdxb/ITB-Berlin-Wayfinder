import json
import os

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
JSON_FILE_PATH = os.path.join(PROJECT_ROOT, 'src', 'data', 'basicDatas.json')
OUTPUT_TXT_PATH = os.path.join(PROJECT_ROOT, 'json_exhibitors_list.txt')

def export_json_to_txt():
    if not os.path.exists(JSON_FILE_PATH):
        print(f"Error: Could not find {JSON_FILE_PATH}")
        return

    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Sort the data: numeric booths first, then letter booths
    def sort_key(item):
        primary_booth = item.get('booth', '').split(' & ')[0]
        if primary_booth.isdigit():
            return (0, int(primary_booth))
        else:
            return (1, primary_booth)

    sorted_data = sorted(data, key=sort_key)

    # Write to a text file
    with open(OUTPUT_TXT_PATH, 'w', encoding='utf-8') as f:
        for entry in sorted_data:
            booth = entry.get('booth', '')
            title = entry.get('title', '')
            f.write(f"{booth} {title}\n")
            
    print(f"Successfully exported {len(sorted_data)} exhibitors to:\n{OUTPUT_TXT_PATH}")

if __name__ == '__main__':
    export_json_to_txt()