"""Выгрузка запусков SpaceX из неофициального api.spacexdata.com (2006–2022).

Результат: data/raw/spacexdata_2006_2022.csv.
Исход запуска: 1 — успех, 0 — неудача, -1 — неизвестен (API перестал обновляться в 2022).

Внимание: по состоянию на 2026 год API недоступен (Cloudflare 525), поэтому
результат выгрузки сохранён в репозитории и пересобирать его не нужно.
"""

import csv
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "spacexdata_2006_2022.csv"

# названия площадок как в Launch Library, чтобы данные двух источников совпадали
LAUNCHPAD_NAMES = {
    "CCSFS SLC 40": "Space Launch Complex 40",
    "VAFB SLC 4E": "Space Launch Complex 4E",
    "KSC LC 39A": "Launch Complex 39A",
}

# запрашиваем только нужные поля запусков
QUERY = {
    "query": {},
    "options": {
        "select": {"flight_number": 1, "date_utc": 1, "success": 1, "rocket": 1, "launchpad": 1},
        "pagination": False,
        "limit": 500,
        "sort": {"flight_number": 1},
    },
}


def main():
    launches = requests.post("https://api.spacexdata.com/v5/launches/query", json=QUERY, timeout=60)
    launches.raise_for_status()
    launches = launches.json()["docs"]
    print(f"Получено {len(launches)} запусков")

    # ракеты и площадки в запусках указаны по id — подтягиваем названия из справочников
    rockets = requests.get("https://api.spacexdata.com/v4/rockets", timeout=60).json()
    launchpads = requests.get("https://api.spacexdata.com/v4/launchpads", timeout=60).json()
    rocket_names = {r["id"]: r["name"] for r in rockets}
    launchpad_names = {p["id"]: p["name"] for p in launchpads}

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "year", "rocket_name", "launchpad_name", "success", "flight_number"])

        for flight_number, launch in enumerate(launches, start=1):
            date = datetime.fromisoformat(launch["date_utc"].replace("Z", "+00:00"))
            launchpad_name = launchpad_names.get(launch["launchpad"], "Unknown")
            success = {True: 1, False: 0}.get(launch["success"], -1)

            writer.writerow([
                date.strftime("%Y-%m-%d %H:%M"),
                date.year,
                rocket_names.get(launch["rocket"], "Unknown"),
                LAUNCHPAD_NAMES.get(launchpad_name, launchpad_name),
                success,
                flight_number,
            ])

    print(f"Сохранено в {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
