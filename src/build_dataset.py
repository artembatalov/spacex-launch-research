"""Сборка итогового датасета запусков SpaceX за 2006–2025 годы из двух источников.

1. data/raw/spacexdata_2006_2022.csv — api.spacexdata.com (fetch_spacexdata.py).
   API перестал обновляться в 2022: начиная с запуска Starlink 3-1 (11.07.2022)
   у части запусков исход неизвестен (success = -1), часть запусков отсутствует.
2. data/raw/launch_library_2022_2025.json — Launch Library 2 (fetch_launch_library.py).

Из spacexdata берём всё строго до первого запуска с неизвестным исходом,
дальше — Launch Library. Названия ракет и площадок приводим к единому виду.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPACEXDATA_CSV = ROOT / "data" / "raw" / "spacexdata_2006_2022.csv"
LAUNCH_LIBRARY_JSON = ROOT / "data" / "raw" / "launch_library_2022_2025.json"
OUTPUT = ROOT / "data" / "spacex_launches_2006_2025.csv"

DATE_FORMAT = "%Y-%m-%d %H:%M"
LAST_DATE = datetime(2025, 12, 31, 23, 59)

# в Launch Library модификация Block 5 вынесена в название ракеты, в spacexdata — нет
ROCKET_NAMES = {"Falcon 9 Block 5": "Falcon 9"}

# исход запуска в Launch Library; неудачи и частичные неудачи считаем неуспешными
LAUNCH_LIBRARY_STATUS = {"Success": 1, "Failure": 0, "Partial Failure": 0}

FIELDS = ["date", "year", "rocket_name", "launchpad_name", "success", "flight_number", "source"]


def read_spacexdata():
    with open(SPACEXDATA_CSV, newline="", encoding="utf-8") as f:
        rows = [
            {
                "date": datetime.strptime(row["date"], DATE_FORMAT),
                "rocket_name": row["rocket_name"],
                "launchpad_name": row["launchpad_name"],
                "success": int(row["success"]),
                "source": "spacexdata",
            }
            for row in csv.DictReader(f)
        ]

    cutoff = min(row["date"] for row in rows if row["success"] == -1)
    return [row for row in rows if row["date"] < cutoff], cutoff


def read_launch_library(cutoff):
    with open(LAUNCH_LIBRARY_JSON, encoding="utf-8") as f:
        launches = json.load(f)["results"]

    rows = []
    for launch in launches:
        date = datetime.fromisoformat(launch["net"].replace("Z", "+00:00")).replace(tzinfo=None)
        rocket_name = launch["name"].split(" | ")[0]
        rows.append({
            "date": date.replace(second=0, microsecond=0),
            "rocket_name": ROCKET_NAMES.get(rocket_name, rocket_name),
            "launchpad_name": launch["pad"],
            "success": LAUNCH_LIBRARY_STATUS[launch["status"]["abbrev"]],
            "source": "launch_library",
        })

    if min(row["date"] for row in rows) > cutoff:
        raise ValueError(f"Выгрузка Launch Library должна начинаться не позже {cutoff:%Y-%m-%d}")
    return [row for row in rows if cutoff <= row["date"] <= LAST_DATE]


def main():
    first_part, cutoff = read_spacexdata()
    second_part = read_launch_library(cutoff)
    launches = sorted(first_part + second_part, key=lambda row: row["date"])

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for flight_number, row in enumerate(launches, start=1):
            writer.writerow({
                **row,
                "date": row["date"].strftime(DATE_FORMAT),
                "year": row["date"].year,
                "flight_number": flight_number,
            })

    print(f"spacexdata: {len(first_part)} запусков до {cutoff:%Y-%m-%d}")
    print(f"Launch Library: {len(second_part)} запусков с {cutoff:%Y-%m-%d}")
    print(f"Итого {len(launches)} запусков "
          f"({launches[0]['date']:%d.%m.%Y} – {launches[-1]['date']:%d.%m.%Y}) -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
