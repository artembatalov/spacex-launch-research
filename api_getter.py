# надо подумать что такое запуски у которых успешность не 0 и не 1

import requests
import csv

url = "https://api.spacexdata.com/v5/launches/query"

# вот тут я указываю какие я хочу дернуть поля в базе чтобы не получать что нам не надо
payload = {
    "query": {},
    "options": {
        "select": {
            "flight_number": 1,
            "date_utc": 1,
            "success": 1,
            "rocket": 1,
            "launchpad": 1
        },
        "pagination": False,
        "limit": 500,
        "sort": {"flight_number": 1}
    }
}

response = requests.post(url, json=payload)
data = response.json()
launches = data['docs']
print(f"Получено {len(launches)} запусков")

rockets = requests.get('https://api.spacexdata.com/v4/rockets').json()
launchpads = requests.get('https://api.spacexdata.com/v4/launchpads').json()

rocket_names = {r['id']: r['name'] for r in rockets}
launchpad_names = {l['id']: l['name'] for l in launchpads}

# тут записываю в csv используя отдельно взятые ракеты и площадки для запуска по айдишкам

with open('all_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['date', 'year', 'rocket_name', 'launchpad_name', 'success', 'flight_number'])
    
    for launch in launches:
        date_utc = launch.get('date_utc', '')
        year = date_utc[:4] if date_utc else ''
        
        rocket_name = rocket_names.get(launch.get('rocket'), 'Unknown')
        launchpad_name = launchpad_names.get(launch.get('launchpad'), 'Unknown')
        
        success_val = launch.get('success')
        success = 1 if success_val is True else 0 if success_val is False else -1
        
        writer.writerow([
            date_utc,
            year,
            rocket_name,
            launchpad_name,
            success,
            launch.get('flight_number', '')
        ])

print('Все записи сохранены в all_data.csv')

years = sorted(set(date_utc[:4] for date_utc in [l.get('date_utc', '') for l in launches] if date_utc))
print(f"- Период: {years[0]} - {years[-1]} год")
print(f"- Ракет в справочнике: {len(rocket_names)}")
print(f"- Площадок в справочнике: {len(launchpad_names)}")