"""Выгрузка запусков SpaceX из Launch Library 2 (ll.thespacedevs.com).

Нужна для периода, где api.spacexdata.com перестал обновляться (с середины 2022).
Сырой ответ API сохраняется как есть в data/raw/launch_library_2022_2025.json.

Бесплатный доступ к LL2 ограничен ~15 запросами в час; выгрузка занимает ~5 запросов.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "launch_library_2022_2025.json"

API_URL = "https://ll.thespacedevs.com/2.2.0/launch/"
PARAMS = {
    "lsp__name": "SpaceX",
    # берём с запасом до момента, когда в spacexdata появляются запуски с неизвестным исходом
    "net__gte": "2022-07-01",
    "net__lte": "2025-12-31T23:59:59Z",
    "ordering": "net",
    "mode": "list",
    "limit": 100,
}


def fetch_all():
    results = []
    url, params = API_URL, PARAMS
    while url:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 429:
            raise SystemExit("Превышен лимит запросов LL2 (~15 в час), попробуйте позже.")
        response.raise_for_status()
        page = response.json()
        results.extend(page["results"])
        print(f"Получено {len(results)} из {page['count']}")
        # в ссылке "next" параметры уже зашиты
        url, params = page["next"], None
    return results


def main():
    results = fetch_all()
    payload = {
        "source": API_URL,
        "params": PARAMS,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(results),
        "results": results,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Сохранено {len(results)} запусков в {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
