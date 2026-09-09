import csv
import json
import os
import difflib

# Define paths based on project structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

BOOTH_FILE_PATH = os.path.join(PROJECT_ROOT, 'booth_allocation.txt')
CSV_FILE_PATH = os.path.join(PROJECT_ROOT, 'public', 'assets', 'sheets', 'ATM Stakeholder Tracker_as of 27Aug.xlsx - Company Profile.csv')
JSON_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'src', 'data')
JSON_OUTPUT_PATH = os.path.join(JSON_OUTPUT_DIR, 'basicDatas.json')

# Map CSV names to the strict names in booth_allocations.txt to assist the fuzzy matcher
MANUAL_OVERRIDES = {
    "teamlab phenomena": "TEAMLAB PHENOMENA ABU DHABI",
    "adrea": "ABU DHABI ROYAL EQUESTRIAN ARTS",
    "gromaxx hotels management": "GROMAXX HOTELS MANAGEMENT LLC",
    "city seasons group of hotels": "CITY SEASONS HOTELS",
    "four seasons abu dhabi": "FOUR SEASONS HOTEL ABU DHABI AT AL MARYAH ISLAND",
    "abu dhabi national hotels": "ADNH",
    "aloft hotel abu dhabi": "ALOFT BY MARRIOTT ABU DHABI",
    "anantara qasr al sarab desert resort": "QASR AL SARAB DESERT RESORT & SIR BANI YAS ISLAND BY ANANTARA",
    "bab al qasr \nhotel & residences": "BAB AL QASR HOTEL & RESIDENCES",
    "conrad abu dhabi eithad towers": "CONRAD ABU DHABI ETIHAD TOWERS",
    "emirates palace mandarin oriental abu dhabi": "EMIRATES PALACE MANDARIN ORIENTAL",
    "federal authority for identity & citizenships": "FEDERAL AUTHORITY FOR IDENTITY, CITIZENSHIP, CUSTOMS & PORT SECURITY",
    "grand hyatt abu dhabi hotel": "GRAND HYATT ABU DHABI HOTEL & RESIDENCES EMIRATES PEARL",
    "grand mercure majlis residencies": "GRAND MERCURE MAJLIS RESIDENCIES",
    "happy journey travel & tours l.l.c": "HAPPY JOURNEY TRAVEL & TOURS LLC",
    "integrated transport centre": "INTEGRATED TRANSPORT CENTRE",
    "intercontinental hotel group": "INTERCONTINENTAL HOTEL & RESIDENCES",
    "magic arabia": "MAGIC ARABIA",
    "zayed international airport": "ZAYED INTERNATIONAL AIRPORT",
    "adnoc jebel dhanna": "AL DHANNAH CITY",
    "miral double booth (for ceo)": "MIRAL DESTINATIONS",
    "7 stars dmc": "SEVEN STARS GLOBAL LLC",
    "ayla grand hotel - al ain": "AYLA HOTELS AND RESORTS",
    "masarra": "MASARRA DESTINATION MANAGEMENT COMPANY",
    "venuewise": "VENUEWISE AI-POWERED VENUE SOURCING",
    "aloft al ain": "ALOFT BY MARRIOTT AL AIN",
    "rocket destination tourism llc": "ROCKET DMC INTERNATIONAL"
}

def load_booth_allocations():
    """Parses the text file and groups booth numbers by exhibitor name."""
    booth_map = {}
    if not os.path.exists(BOOTH_FILE_PATH):
        print(f"Error: Booth file not found at {BOOTH_FILE_PATH}")
        return booth_map

    with open(BOOTH_FILE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines or the section header
            if not line or 'Lettered' in line:
                continue
            
            # Split the booth number from the name (e.g., "11 ABU DHABI ROYAL EQUESTRIAN ARTS")
            parts = line.split(' ', 1)
            if len(parts) == 2:
                booth_num = parts[0].strip()
                name = parts[1].strip().upper()
                
                # Append to list to handle dual booths like 11 & E
                if name in booth_map:
                    booth_map[name].append(booth_num)
                else:
                    booth_map[name] = [booth_num]
    
    return booth_map

def generate_json_from_csv():
    json_data = []
    
    booth_map = load_booth_allocations()
    map_keys = list(booth_map.keys())
    matched_exhibitors = set()

    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: CSV file not found at:\n{CSV_FILE_PATH}")
        return

    os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)

    with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader, None) # Skip header
        
        for row in reader:
            if not row or len(row) < 2 or not row[1].strip():
                continue
            
            display_name = row[1].strip()
            display_name_lower = display_name.lower()
            
            content = row[2].strip() if len(row) > 2 else ""
            content = content.replace('\n', '<br>')

            matched_name = None
            
            # 1. Check Manual Overrides
            if display_name_lower in MANUAL_OVERRIDES:
                matched_name = MANUAL_OVERRIDES[display_name_lower]
            
            # 2. Fuzzy Match against booth map
            if not matched_name:
                matches = difflib.get_close_matches(display_name.upper(), map_keys, n=1, cutoff=0.6)
                if matches:
                    matched_name = matches[0]
            
            if matched_name and matched_name in booth_map:
                matched_exhibitors.add(matched_name)
                booth_str = " & ".join(booth_map[matched_name])
                
                client_entry = {
                    "id": booth_str if '&' not in booth_str else booth_str.split(' & ')[0], 
                    "title": display_name,
                    "content": content,
                    "booth": booth_str
                }
                
                json_data.append(client_entry)

    # 3. Auto-Inject Missing Exhibitors
    for name, booths in booth_map.items():
        if name not in matched_exhibitors:
            booth_str = " & ".join(booths)
            json_data.append({
                "id": booth_str if '&' not in booth_str else booth_str.split(' & ')[0],
                "title": name.title(), # Formats ALL CAPS to Title Case for the UI
                "content": "",
                "booth": booth_str
            })

    with open(JSON_OUTPUT_PATH, mode='w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=2, ensure_ascii=False)
    
    print(f"\nSuccess! Processed {len(json_data)} clients.")
    print(f"JSON saved to: {JSON_OUTPUT_PATH}")

if __name__ == '__main__':
    generate_json_from_csv()