import json
import csv
from datetime import datetime

json_filename = 'from2022to2025.json'

with open(json_filename, 'r', encoding='utf-8') as f:
    data = json.load(f)


with open('from2022to2025.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow(['date', 'year', 'rocket_name', 'launchpad_name', 'success', 'flight_number'])
    
    results = data['results']
    for idx, launch in enumerate(results, start=1):
        net_str = launch.get('net')
        date_obj = datetime.fromisoformat(net_str.replace('Z', '+00:00'))
        date_str = date_obj.strftime('%Y-%m-%d %H:%M')
        year = date_obj.year
        
        rocket_name = launch.get('name', 'Unknown').split(' | ')[0]
        
        launchpad_name = launch.get('pad', 'Unknown')
        
        status_name = launch.get('status', {}).get('name', '')
        success = 1 if status_name.lower() == 'launch successful' else 0
        
        flight_number = idx
        
        writer.writerow([date_str, year, rocket_name, launchpad_name, success, flight_number])